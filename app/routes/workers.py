from fastapi import APIRouter, Depends
import json
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Worker, WorkerSkill
from app.schemas import WorkerCreate, WorkerResponse
from app.services.extraction_service import extract_skill_objects_from_text

router = APIRouter(prefix="/workers", tags=["Workers"])


# CREATE WORKER
@router.post("/", response_model=WorkerResponse)
def create_worker(worker_data: WorkerCreate, db: Session = Depends(get_db)):

    worker = Worker(
        name=worker_data.name,
        location=worker_data.location,
        country_code=worker_data.country_code or "GH",
        raw_experience=worker_data.raw_experience
    )

    db.add(worker)
    db.commit()
    db.refresh(worker)

    # Extract ESCO-mapped skills when available.
    skills = extract_skill_objects_from_text(
        worker.raw_experience,
        assess_proficiency=True,
    )

    for skill in skills:
        worker_skill = WorkerSkill(
            worker_id=worker.id,
            skill_name=skill["name"],
            skill_id=skill.get("id"),
            confidence=skill.get("confidence"),
            source=skill.get("source"),
            source_query=skill.get("source_query"),
            evidence=json.dumps(skill.get("proficiency_evidence", [])),
            proficiency_basis=skill.get("proficiency_basis"),
        )
        db.add(worker_skill)

    db.commit()

    return worker


# LIST WORKERS
@router.get("/")
def get_workers(db: Session = Depends(get_db)):
    workers = db.query(Worker).all()
    return workers

@router.get("/{worker_id}/skills")
def get_worker_skills(worker_id: int, db: Session = Depends(get_db)):
    skills = db.query(WorkerSkill).filter(
        WorkerSkill.worker_id == worker_id
    ).all()

    return {
        "worker_id": worker_id,
        "skills": [
            {
                "id": skill.skill_id,
                "name": skill.skill_name,
                "confidence": skill.confidence,
                "source": skill.source,
                "source_query": skill.source_query,
                "evidence": json.loads(skill.evidence or "[]"),
                "proficiency_basis": skill.proficiency_basis,
            }
            for skill in skills
        ]
    }
