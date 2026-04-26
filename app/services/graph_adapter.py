"""
graph_adapter.py
----------------
Adapter owned by Part 3.

Purpose:
- Load SQLAlchemy rows from Postgres.
- Convert DB rows into the Pydantic graph models.
- Build a merged NetworkX graph.
- Call the matching engine.

Imports from graph/ (the canonical implementation) not app/graph/.
"""

from __future__ import annotations

import re
from sqlalchemy.orm import Session

from app.models import Worker, WorkerSkill, Job, JobSkill

from graph.models import (
    WorkerNode,
    WorkerProfile,
    WorkerSkillEdge,
    JobNode,
    JobPost,
    JobSkillEdge,
    SkillNode,
    LocationNode,
    SkillSource,
    SkillImportance,
    LaborSignalNode,
    AutomationRiskNode,
    SectorNode,
    OccupationNode,
)

from graph.graph import create_worker_graph, create_job_graph, merge_graphs
from graph.matching import match_worker_to_jobs as graph_match_worker_to_jobs


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def _safe_id(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_") or "unknown"


def _location_id(city: str, country_code: str) -> str:
    return f"{country_code}-{_safe_id(city).upper()}"


def _worker_node_id(worker_id: int | str) -> str:
    return f"worker:{worker_id}"


def _job_node_id(job_id: int | str) -> str:
    return f"job:{job_id}"


def _skill_node_from_name(skill_name: str) -> SkillNode:
    """
    Build a SkillNode from a plain skill name.
    esco_id is derived from the name until Part 2's ESCO mapping
    is fully wired in — at which point skill_name will already
    be a proper ESCO URI coming from the DB.
    """
    return SkillNode(
        esco_id=_safe_id(skill_name),
        label=skill_name,
    )


def _skill_id(row: WorkerSkill | JobSkill) -> str:
    return getattr(row, "skill_id", None) or _safe_id(row.skill_name)


def _skill_source(row: WorkerSkill | JobSkill) -> SkillSource:
    source = getattr(row, "source", None) or SkillSource.esco_semantic_search.value
    try:
        return SkillSource(source)
    except ValueError:
        return SkillSource.esco_semantic_search


# ─────────────────────────────────────────────────────────────
# Profile builders
# ─────────────────────────────────────────────────────────────

def _build_worker_profile(
    worker: Worker,
    worker_skills: list[WorkerSkill],
) -> tuple[WorkerProfile, LocationNode, list[SkillNode]]:
    """
    Convert a Worker DB row + its skills into a WorkerProfile
    suitable for graph construction.
    """
    country_code = getattr(worker, "country_code", "GH")
    city         = worker.location
    location_id  = _location_id(city, country_code)

    skill_nodes = [
        SkillNode(
            esco_id=_skill_id(ws),
            label=ws.skill_name,
            category="esco" if getattr(ws, "skill_id", None) else "fallback",
        )
        for ws in worker_skills
    ]

    profile = WorkerProfile(
        worker=WorkerNode(
            worker_id=_worker_node_id(worker.id),
            name=worker.name or f"Worker {worker.id}",
            country_code=country_code,
            location_id=location_id,
            education_level=getattr(worker, "education_level", None),
        ),
        skills=[
            WorkerSkillEdge(
                worker_id=_worker_node_id(worker.id),
                esco_id=_skill_id(ws),
                confidence=getattr(ws, "confidence", None) or 1.0,
                source=_skill_source(ws),
            )
            for ws in worker_skills
        ],
    )

    location = LocationNode(
        location_id=location_id,
        city=city,
        country_code=country_code,
        country_name=getattr(worker, "country_name", city),
    )

    return profile, location, skill_nodes


def _build_job_post(
    job: Job,
    job_skills: list[JobSkill],
) -> tuple[JobPost, LocationNode, list[SkillNode]]:
    """
    Convert a Job DB row + its skills into a JobPost
    suitable for graph construction.
    """
    country_code = getattr(job, "country_code", "GH")
    city         = job.location
    location_id  = _location_id(city, country_code)

    skill_nodes = [
        SkillNode(
            esco_id=_skill_id(js),
            label=js.skill_name,
            category="esco" if getattr(js, "skill_id", None) else "fallback",
        )
        for js in job_skills
    ]

    post = JobPost(
        job=JobNode(
            job_id=_job_node_id(job.id),
            title=job.title,
            country_code=country_code,
            location_id=location_id,
            sector_id=getattr(job, "sector_id", None),
            occupation_id=getattr(job, "isco_code", None),
            opportunity_type=getattr(job, "opportunity_type", "formal_employment"),
        ),
        skills=[
            JobSkillEdge(
                job_id=_job_node_id(job.id),
                esco_id=_skill_id(js),
                importance=SkillImportance(
                    getattr(js, "importance", None) or SkillImportance.required
                ),
            )
            for js in job_skills
        ],
    )

    location = LocationNode(
        location_id=location_id,
        city=city,
        country_code=country_code,
        country_name=getattr(job, "country_name", city),
    )

    return post, location, skill_nodes


# ─────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────

def get_matches_for_worker(worker_id: int, db: Session) -> list[dict]:
    """
    Load worker + all jobs from Postgres, build merged graph,
    run matching, return JSON-serializable results for the route.
    """
    worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if not worker:
        return []

    worker_skills = db.query(WorkerSkill).filter(
        WorkerSkill.worker_id == worker_id
    ).all()

    worker_profile, worker_location, worker_skill_nodes = _build_worker_profile(
        worker, worker_skills
    )

    worker_graph = create_worker_graph(worker_profile, worker_location, worker_skill_nodes)

    graphs = [worker_graph]
    jobs_by_id: dict[str, Job] = {}

    for job in db.query(Job).all():
        job_skills = db.query(JobSkill).filter(JobSkill.job_id == job.id).all()
        if not job_skills:
            continue

        job_post, job_location, job_skill_nodes = _build_job_post(job, job_skills)

        # Optional enrichment — attach labor signals and automation risk
        # if the DB has them. Currently stubbed; Part 3 fills these in
        # when econometric data tables are ready.
        labor_signals  = _load_labor_signals(job, db)
        automation_risk = _load_automation_risk(job, db)
        sector         = _load_sector(job)
        occupation     = _load_occupation(job)

        job_graph = create_job_graph(
            job_post,
            job_location,
            job_skill_nodes,
            sector=sector,
            occupation=occupation,
            labor_signals=labor_signals,
            automation_risk=automation_risk,
        )

        graphs.append(job_graph)
        jobs_by_id[_job_node_id(job.id)] = job

    merged = merge_graphs(*graphs)
    results = graph_match_worker_to_jobs(_worker_node_id(worker_id), merged)

    response = []
    for result in results:
        job = jobs_by_id.get(result.job_id)
        if not job:
            continue

        response.append({
            "job_id":         int(result.job_id.removeprefix("job:")),
            "title":          job.title,
            "location":       job.location,
            "score":          round(result.score * 100, 2),
            "skill_score":    round(result.skill_score * 100, 2),
            "location_score": round(result.location_score * 100, 2),
            "matched_skills": [
                merged.nodes[s].get("label", s)
                for s in result.matched_skills
                if s in merged.nodes
            ],
            "missing_skills": [
                {
                    "skill":            gap.label,
                    "importance":       gap.importance.value,
                    "gap_size":         gap.gap_size,
                    "next_step":        gap.suggested_next_step,
                }
                for gap in result.missing_skills
            ],
            "labor_signals": [
                {
                    "label":       sig.label,
                    "value":       sig.value,
                    "source":      sig.source,
                    "year":        sig.year,
                    "explanation": sig.explanation,
                }
                for sig in result.labor_signals
            ],
            "automation_risk": {
                "score":            result.automation_risk.score,
                "level":            result.automation_risk.level,
                "source":           result.automation_risk.source,
                "calibration_note": result.automation_risk.calibration_note,
            } if result.automation_risk else None,
            "explanation": result.explanation,
        })

    return response


# ─────────────────────────────────────────────────────────────
# Enrichment stubs — Part 3 replaces these with real DB queries
# once econometric data tables are in place.
# ─────────────────────────────────────────────────────────────

def _load_labor_signals(job: Job, db: Session) -> list[LaborSignalNode]:
    """
    Return visible demo labor signals for this job's sector/occupation.
    Part 3 can replace this with real DB queries while preserving the API shape.
    """
    sector_id = _infer_sector_id(job)
    title = job.title.lower()

    if "agric" in title or "crop" in title or "farm" in title:
        return [
            LaborSignalNode(
                signal_id=f"gh_{sector_id}_agriculture_employment",
                label="Employment by sector",
                value="Agriculture remains a major youth employment sector",
                source="ILO ILOSTAT / World Bank WDI demo signal",
                year=2024,
                country_code="GH",
                sector_id=sector_id,
                explanation="Shows why nearby agricultural pathways are realistic rather than aspirational.",
            ),
            LaborSignalNode(
                signal_id=f"gh_{sector_id}_informality",
                label="Informal employment exposure",
                value="High",
                source="ILOSTAT informality demo signal",
                year=2024,
                country_code="GH",
                sector_id=sector_id,
                explanation="Flags that many opportunities may be informal or mixed formal/informal.",
            ),
        ]

    return [
        LaborSignalNode(
            signal_id=f"gh_{sector_id}_digital_services_growth",
            label="Digital services opportunity",
            value="Growing local demand",
            source="World Bank WDI / ITU demo signal",
            year=2024,
            country_code="GH",
            sector_id=sector_id,
            explanation="Connects repair and ICT support skills to reachable local service work.",
        ),
        LaborSignalNode(
            signal_id=f"gh_{sector_id}_wage_employment_share",
            label="Wage and salaried employment share",
            value="Visible labor market constraint",
            source="ILO modelled estimate demo signal",
            year=2024,
            country_code="GH",
            sector_id=sector_id,
            explanation="Reminds users that formal wage jobs are only one part of the opportunity landscape.",
        ),
    ]


def _load_automation_risk(job: Job, db: Session) -> AutomationRiskNode | None:
    """
    Return demo automation exposure by inferred occupation.
    Part 3 can replace this with Frey-Osborne / O*NET / ILO task data.
    """
    occupation_id = _infer_occupation_id(job)
    title = job.title.lower()

    if "agric" in title or "field" in title:
        return AutomationRiskNode(
            risk_id=f"risk_{occupation_id}",
            occupation_id=occupation_id,
            score=0.35,
            level="medium",
            source="Frey-Osborne / O*NET-derived demo signal",
            calibration_note="Hands-on and local coordination tasks reduce full automation exposure.",
        )

    return AutomationRiskNode(
        risk_id=f"risk_{occupation_id}",
        occupation_id=occupation_id,
        score=0.42,
        level="medium",
        source="Frey-Osborne / O*NET-derived demo signal",
        calibration_note="Routine diagnostics face pressure, but hands-on repair and customer trust remain durable.",
    )


def _load_sector(job: Job) -> SectorNode | None:
    sector_id = _infer_sector_id(job)
    return SectorNode(sector_id=sector_id, label=sector_id.replace("_", " ").title())


def _load_occupation(job: Job) -> OccupationNode | None:
    occupation_id = _infer_occupation_id(job)
    return OccupationNode(
        occupation_id=occupation_id,
        label=occupation_id.replace("_", " ").upper(),
    )


def _infer_sector_id(job: Job) -> str:
    explicit = getattr(job, "sector_id", None)
    if explicit:
        return explicit

    text = f"{job.title} {job.description}".lower()
    if any(word in text for word in ["agric", "crop", "farm", "harvest"]):
        return "agriculture"
    if any(word in text for word in ["phone", "mobile", "ict", "software", "technical"]):
        return "ict_services"
    return "general_services"


def _infer_occupation_id(job: Job) -> str:
    explicit = getattr(job, "isco_code", None)
    if explicit:
        return explicit

    text = f"{job.title} {job.description}".lower()
    if any(word in text for word in ["phone", "mobile", "repair"]):
        return "isco_7422"
    if any(word in text for word in ["ict", "technical support", "help desk"]):
        return "isco_3512"
    if any(word in text for word in ["agric", "crop", "farm", "field"]):
        return "isco_3142"
    return "isco_unknown"
