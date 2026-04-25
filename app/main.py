from fastapi import FastAPI
from app.routes import workers, jobs, matches

app = FastAPI(title="Unmapped API")

app.include_router(workers.router)
app.include_router(jobs.router)
app.include_router(matches.router)

@app.get("/")
def root():
    return {"status": "Unmapped backend running"}



