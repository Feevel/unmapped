from app.database import SessionLocal
from app.models import Worker, WorkerSkill, Job, JobSkill

db = SessionLocal()

db.query(WorkerSkill).delete()
db.query(JobSkill).delete()
db.query(Worker).delete()
db.query(Job).delete()

worker = Worker(
    name="Amara",
    location="London",
    raw_experience="I repair phones and help customers"
)

db.add(worker)
db.commit()
db.refresh(worker)

db.add_all([
    WorkerSkill(worker_id=worker.id, skill_name="phone repair"),
    WorkerSkill(worker_id=worker.id, skill_name="customer service")
])

job = Job(
    title="Phone Repair Technician",
    location="London",
    description="Repair smartphones and assist customers"
)

db.add(job)
db.commit()
db.refresh(job)

db.add_all([
    JobSkill(job_id=job.id, skill_name="phone repair"),
    JobSkill(job_id=job.id, skill_name="customer service")
])

db.commit()

print("Demo data ready.")