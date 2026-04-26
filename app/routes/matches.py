from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.graph_adapter import get_matches_for_worker

router = APIRouter(prefix="/matches", tags=["Matches"])


@router.get("/worker/{worker_id}")
def match_worker(worker_id: int, db: Session = Depends(get_db)):
    results = get_matches_for_worker(worker_id, db)

    return {
        "worker_id": worker_id,
        "engine": "graph",
        "matches": results,
    }