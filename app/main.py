from fastapi import FastAPI
from app.routes import workers, jobs, matches
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Unmapped API")

app.include_router(workers.router)
app.include_router(jobs.router)
app.include_router(matches.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # safe for hackathon
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "Unmapped backend running"}

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "unmapped-backend"
    }

