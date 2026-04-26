# UNMAPPED Backend

FastAPI backend for ESCO-backed skill extraction, graph matching, visible labor-market signals, and demo automation-risk context.

## Setup

```bash
pip install -r requirements.txt
python -m app.create_tables
python -m app.scripts.seed_demo_data
python -m uvicorn app.main:app --reload
```

For optional FAISS/sentence-transformers ESCO semantic search:

```bash
pip install -r requirements-ml.txt
```

API docs:

```text
http://127.0.0.1:8000/docs
```

## Demo Endpoints

```text
POST /workers/
GET /workers/
GET /workers/{worker_id}/skills

POST /jobs/
GET /jobs/
GET /jobs/{job_id}/skills

GET /matches/worker/{worker_id}
```

`GET /matches/worker/{worker_id}` returns graph match scores, matched skills, skill-gap next steps, visible labor market signals, and automation-risk context.

## Notes

The ESCO vector search uses `data/faiss.index` and `data/id_map.json`. If the optional ML dependencies or Ollama/Mistral are not available, the API falls back to keyword matching so the demo can still run.
