"""
graph_adapter.py
----------------
Adapter owned by Person 3.

Purpose:
- Load SQLAlchemy rows from Postgres.
- Convert DB rows into Person A's Pydantic graph models.
- Build a merged NetworkX graph.
- Call Person A's matching engine.

This keeps graph code independent from database code.
"""

from __future__ import annotations

import re
from sqlalchemy.orm import Session

from app.models import Worker, WorkerSkill, Job, JobSkill

from app.graph.graph_models import (
    WorkerNode,
    WorkerProfile,
    WorkerSkillEdge,
    WorkerLocationEdge,
    JobNode,
    JobPost,
    JobSkillEdge,
    JobLocationEdge,
    SkillNode,
    LocationNode,
    SkillSource,
    SkillImportance,
)

from app.graph.graph import create_worker_graph, create_job_graph, merge_graphs

from app.graph.matching import (
    match_worker_to_jobs as graph_match_worker_to_jobs
)


def _safe_id(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_") or "unknown"


def _location_id(location: str, country_code: str = "UK") -> str:
    return f"{country_code}-{_safe_id(location).upper()}"


def _skill_node_from_name(skill_name: str) -> SkillNode:
    esco_id = _safe_id(skill_name)

    return SkillNode(
        esco_id=esco_id,
        label=skill_name,
        category="temporary_skill",
    )


def _build_worker_profile(
    worker: Worker,
    worker_skills: list[WorkerSkill],
) -> tuple[WorkerProfile, LocationNode, list[SkillNode]]:
    country_code = "UK"
    location_id = _location_id(worker.location, country_code)

    skill_nodes = [
        _skill_node_from_name(ws.skill_name)
        for ws in worker_skills
    ]

    profile = WorkerProfile(
        worker=WorkerNode(
            worker_id=str(worker.id),
            name=worker.name or f"Worker {worker.id}",
            education_level="unknown",
            country_code=country_code,
        ),
        skills=[
            WorkerSkillEdge(
                worker_id=str(worker.id),
                esco_id=_safe_id(ws.skill_name),
                confidence=1.0,
                source=SkillSource.assessed,
            )
            for ws in worker_skills
        ],
        location=WorkerLocationEdge(
            worker_id=str(worker.id),
            location_id=location_id,
            willing_to_relocate=False,
        ),
    )

    location = LocationNode(
        location_id=location_id,
        city=worker.location,
        country="United Kingdom",
        country_code=country_code,
    )

    return profile, location, skill_nodes


def _build_job_post(
    job: Job,
    job_skills: list[JobSkill],
) -> tuple[JobPost, LocationNode, list[SkillNode]]:
    country_code = "UK"
    location_id = _location_id(job.location, country_code)

    skill_nodes = [
        _skill_node_from_name(js.skill_name)
        for js in job_skills
    ]

    post = JobPost(
        job=JobNode(
            job_id=str(job.id),
            title=job.title,
            sector="unknown",
            isco_code=None,
        ),
        skills=[
            JobSkillEdge(
                job_id=str(job.id),
                esco_id=_safe_id(js.skill_name),
                importance=SkillImportance.required,
            )
            for js in job_skills
        ],
        location=JobLocationEdge(
            job_id=str(job.id),
            location_id=location_id,
            remote_ok=False,
        ),
    )

    location = LocationNode(
        location_id=location_id,
        city=job.location,
        country="United Kingdom",
        country_code=country_code,
    )

    return post, location, skill_nodes


def get_matches_for_worker(worker_id: int, db: Session) -> list[dict]:
    """
    Public adapter function used by FastAPI route.
    Returns JSON-serializable match results for frontend.
    """
    worker = db.query(Worker).filter(Worker.id == worker_id).first()

    if not worker:
        return []

    worker_skills = db.query(WorkerSkill).filter(
        WorkerSkill.worker_id == worker_id
    ).all()

    worker_profile, worker_location, worker_skill_nodes = _build_worker_profile(
        worker,
        worker_skills,
    )

    worker_graph = create_worker_graph(
        worker_profile,
        worker_location,
        worker_skill_nodes,
    )

    graphs = [worker_graph]
    jobs_by_id: dict[str, Job] = {}

    jobs = db.query(Job).all()

    for job in jobs:
        job_skills = db.query(JobSkill).filter(
            JobSkill.job_id == job.id
        ).all()

        if not job_skills:
            continue

        job_post, job_location, job_skill_nodes = _build_job_post(
            job,
            job_skills,
        )

        job_graph = create_job_graph(
            job_post,
            job_location,
            job_skill_nodes,
        )

        graphs.append(job_graph)
        jobs_by_id[str(job.id)] = job

    merged_graph = merge_graphs(*graphs)

    graph_results = graph_match_worker_to_jobs(
        str(worker_id),
        merged_graph,
    )

    response = []

    for result in graph_results:
        job = jobs_by_id.get(result.job_id)

        if not job:
            continue

        response.append(
            {
                "job_id": int(result.job_id),
                "title": job.title,
                "location": job.location,
                "score": round(result.score * 100, 2),
                "skill_score": round(result.skill_score * 100, 2),
                "location_score": round(result.location_score * 100, 2),
                "matched_skills": [
                    merged_graph.nodes[s].get("label", s)
                    for s in result.matched_skills
                    if s in merged_graph.nodes
                ],
                "missing_skills": [
                    {
                        "skill": gap.label,
                        "importance": gap.importance.value,
                    }
                    for gap in result.missing_skills
                ],
                "reason": result.explanation,
            }
        )

    return response