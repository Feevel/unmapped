from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Worker, WorkerSkill
from app.schemas import WorkerCreate, WorkerResponse
from app.services.extraction_service import extract_skills_from_text

router = APIRouter(prefix="/workers", tags=["Workers"])


# CREATE WORKER
@router.post("/", response_model=WorkerResponse)
def create_worker(worker_data: WorkerCreate, db: Session = Depends(get_db)):

    worker = Worker(
        name=worker_data.name,
        location=worker_data.location,
        raw_experience=worker_data.raw_experience
    )

    db.add(worker)
    db.commit()
    db.refresh(worker)

    # Extract skills
    skills = extract_skills_from_text(worker.raw_experience)

    for skill in skills:
        worker_skill = WorkerSkill(
            worker_id=worker.id,
            skill_name=skill
        )
        db.add(worker_skill)

    db.commit()

    return worker


# LIST WORKERS
@router.get("/")
def get_workers(db: Session = Depends(get_db)):
    workers = db.query(Worker).all()
    return workers