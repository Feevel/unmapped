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
    JobLocationEdge,
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

    skill_nodes = [_skill_node_from_name(ws.skill_name) for ws in worker_skills]

    profile = WorkerProfile(
        worker=WorkerNode(
            worker_id=str(worker.id),
            name=worker.name or f"Worker {worker.id}",
            country_code=country_code,
            location_id=location_id,
            education_level=getattr(worker, "education_level", None),
        ),
        skills=[
            WorkerSkillEdge(
                worker_id=str(worker.id),
                esco_id=_safe_id(ws.skill_name),
                confidence=getattr(ws, "confidence", 1.0),
                source=SkillSource(getattr(ws, "source", SkillSource.assessed)),
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

    skill_nodes = [_skill_node_from_name(js.skill_name) for js in job_skills]

    post = JobPost(
        job=JobNode(
            job_id=str(job.id),
            title=job.title,
            country_code=country_code,
            location_id=location_id,
            sector_id=getattr(job, "sector_id", None),
            occupation_id=getattr(job, "isco_code", None),
            opportunity_type=getattr(job, "opportunity_type", "formal_employment"),
        ),
        skills=[
            JobSkillEdge(
                job_id=str(job.id),
                esco_id=_safe_id(js.skill_name),
                importance=SkillImportance(
                    getattr(js, "importance", SkillImportance.required)
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
        jobs_by_id[str(job.id)] = job

    merged = merge_graphs(*graphs)
    results = graph_match_worker_to_jobs(str(worker_id), merged)

    response = []
    for result in results:
        job = jobs_by_id.get(result.job_id)
        if not job:
            continue

        response.append({
            "job_id":         int(result.job_id),
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
    Return labor signals for this job's sector/occupation.
    Currently returns an empty list — Part 3 wires in real data here.
    """
    return []


def _load_automation_risk(job: Job, db: Session) -> AutomationRiskNode | None:
    """
    Return automation risk for this job's occupation.
    Currently returns None — Part 3 wires in Frey-Osborne data here.
    """
    return None


def _load_sector(job: Job) -> SectorNode | None:
    sector_id = getattr(job, "sector_id", None)
    if not sector_id:
        return None
    return SectorNode(sector_id=sector_id, label=sector_id)


def _load_occupation(job: Job) -> OccupationNode | None:
    occupation_id = getattr(job, "isco_code", None)
    if not occupation_id:
        return None
    return OccupationNode(occupation_id=occupation_id, label=occupation_id)