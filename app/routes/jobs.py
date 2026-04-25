from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Job, JobSkill
from app.schemas import JobCreate, JobResponse
from app.services.extraction_service import extract_skills_from_text

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post("/", response_model=JobResponse)
def create_job(job_data: JobCreate, db: Session = Depends(get_db)):
    # Create job
    job = Job(
        title=job_data.title,
        location=job_data.location,
        description=job_data.description
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    # Extract skills from job description
    skills = extract_skills_from_text(job.description)

    # Store job skills
    for skill in skills:
        job_skill = JobSkill(
            job_id=job.id,
            skill_name=skill
        )

        db.add(job_skill)

    db.commit()

    return job