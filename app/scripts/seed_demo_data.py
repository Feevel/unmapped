"""
seed_demo_data.py
-----------------
Populates the DB with a realistic demo scenario set in Accra, Ghana.
Run once before demoing:
    python -m app.scripts.seed_demo_data
"""

from app.database import SessionLocal
from app.models import Worker, WorkerSkill, Job, JobSkill

db = SessionLocal()

# ── Clear existing data ───────────────────────────────────────
db.query(WorkerSkill).delete()
db.query(JobSkill).delete()
db.query(Worker).delete()
db.query(Job).delete()
db.commit()

# ── Workers ───────────────────────────────────────────────────

amara = Worker(
    name="Amara",
    location="Accra",
    raw_experience=(
        "I have repaired phones for 5 years. I replace screens, fix charging ports, "
        "install apps, talk to customers, buy spare parts, and manage payments. "
        "I also learned basic coding from YouTube."
    )
)
db.add(amara)
db.commit()
db.refresh(amara)

db.add_all([
    WorkerSkill(worker_id=amara.id, skill_name="repair mobile devices"),
    WorkerSkill(worker_id=amara.id, skill_name="customer service"),
    WorkerSkill(worker_id=amara.id, skill_name="basic programming"),
    WorkerSkill(worker_id=amara.id, skill_name="manage payments"),
])

kwame = Worker(
    name="Kwame",
    location="Kumasi",
    raw_experience=(
        "I grow maize and cassava and sell produce at the local market. "
        "I manage a small team during harvest season and keep basic records."
    )
)
db.add(kwame)
db.commit()
db.refresh(kwame)

db.add_all([
    WorkerSkill(worker_id=kwame.id, skill_name="crop cultivation"),
    WorkerSkill(worker_id=kwame.id, skill_name="team management"),
    WorkerSkill(worker_id=kwame.id, skill_name="record keeping"),
])

# ── Jobs ──────────────────────────────────────────────────────

job1 = Job(
    title="Mobile Phone Repair Technician",
    location="Accra",
    description=(
        "Diagnose and repair smartphones and mobile devices. "
        "Assist customers and manage spare parts inventory."
    )
)
db.add(job1)
db.commit()
db.refresh(job1)

db.add_all([
    JobSkill(job_id=job1.id, skill_name="repair mobile devices"),
    JobSkill(job_id=job1.id, skill_name="customer service"),
    JobSkill(job_id=job1.id, skill_name="manage inventory"),
])

job2 = Job(
    title="ICT Support Assistant",
    location="Accra",
    description=(
        "Provide technical support to office staff. "
        "Basic troubleshooting, software installation, and customer-facing help desk."
    )
)
db.add(job2)
db.commit()
db.refresh(job2)

db.add_all([
    JobSkill(job_id=job2.id, skill_name="basic programming"),
    JobSkill(job_id=job2.id, skill_name="customer service"),
    JobSkill(job_id=job2.id, skill_name="repair mobile devices"),
])

job3 = Job(
    title="Agricultural Field Officer",
    location="Kumasi",
    description=(
        "Support smallholder farmers with crop planning and record keeping. "
        "Coordinate seasonal labour and maintain field reports."
    )
)
db.add(job3)
db.commit()
db.refresh(job3)

db.add_all([
    JobSkill(job_id=job3.id, skill_name="crop cultivation"),
    JobSkill(job_id=job3.id, skill_name="record keeping"),
    JobSkill(job_id=job3.id, skill_name="team management"),
])

db.commit()
print("Demo data seeded — Ghana context, 2 workers, 3 jobs.")