from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Job, JobSkill
from app.schemas import JobCreate, JobResponse
from app.services.extraction_service import extract_skill_objects_from_text

router = APIRouter(prefix="/jobs", tags=["Jobs"])


# CREATE JOB
@router.post("/", response_model=JobResponse)
def create_job(job_data: JobCreate, db: Session = Depends(get_db)):

    job = Job(
        title=job_data.title,
        location=job_data.location,
        country_code=job_data.country_code or "GH",
        description=job_data.description
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    # Extract ESCO-mapped requirements when available.
    skills = extract_skill_objects_from_text(job.description)

    for skill in skills:
        job_skill = JobSkill(
            job_id=job.id,
            skill_name=skill["name"],
            skill_id=skill.get("id"),
            confidence=skill.get("confidence"),
            source=skill.get("source"),
            source_query=skill.get("source_query"),
            importance="required",
        )
        db.add(job_skill)

    db.commit()

    return job


# LIST JOBS
@router.get("/")
def get_jobs(db: Session = Depends(get_db)):
    jobs = db.query(Job).all()
    return jobs

@router.get("/{job_id}/skills")
def get_job_skills(job_id: int, db: Session = Depends(get_db)):
    skills = db.query(JobSkill).filter(
        JobSkill.job_id == job_id
    ).all()

    return {
        "job_id": job_id,
        "skills": [
            {
                "id": skill.skill_id,
                "name": skill.skill_name,
                "confidence": skill.confidence,
                "source": skill.source,
                "source_query": skill.source_query,
                "importance": skill.importance,
            }
            for skill in skills
        ]
    }
