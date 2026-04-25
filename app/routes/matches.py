from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import WorkerSkill, JobSkill, Job, Match

router = APIRouter(prefix="/matches", tags=["Matches"])


@router.get("/worker/{worker_id}")
def match_worker(worker_id: int, db: Session = Depends(get_db)):
    worker_skills = db.query(WorkerSkill).filter(
        WorkerSkill.worker_id == worker_id
    ).all()

    worker_skill_names = {skill.skill_name for skill in worker_skills}

    jobs = db.query(Job).all()

    results = []

    for job in jobs:
        job_skills = db.query(JobSkill).filter(
            JobSkill.job_id == job.id
        ).all()

        job_skill_names = {skill.skill_name for skill in job_skills}

        if not job_skill_names:
            continue

        matched_skills = worker_skill_names.intersection(job_skill_names)

        score = len(matched_skills) / len(job_skill_names) * 100

        if score > 0:
            results.append({
                "job_id": job.id,
                "title": job.title,
                "location": job.location,
                "score": round(score, 2),
                "matched_skills": list(matched_skills),
                "reason": f"Matched {len(matched_skills)} of {len(job_skill_names)} required skills"
            })

    results.sort(key=lambda x: x["score"], reverse=True)

    return {
        "worker_id": worker_id,
        "matches": results
    }