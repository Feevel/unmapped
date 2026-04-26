"""
seed_demo_data.py
-----------------
Populates the DB with multi-country demo contexts.
Run before demoing:
    python -m app.scripts.seed_demo_data
"""

from app.database import SessionLocal
from app.models import Worker, WorkerSkill, Job, JobSkill

db = SessionLocal()


def add_worker(name: str, location: str, country_code: str, raw_experience: str, skills: list[tuple[str, float, str]]) -> Worker:
    worker = Worker(
        name=name,
        location=location,
        country_code=country_code,
        raw_experience=raw_experience,
    )
    db.add(worker)
    db.commit()
    db.refresh(worker)
    for skill_name, confidence, source in skills:
        db.add(
            WorkerSkill(
                worker_id=worker.id,
                skill_name=skill_name,
                confidence=confidence,
                source=source,
            )
        )
    return worker


def add_job(title: str, location: str, country_code: str, description: str, skills: list[tuple[str, str]]) -> Job:
    job = Job(
        title=title,
        location=location,
        country_code=country_code,
        description=description,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    for skill_name, importance in skills:
        db.add(
            JobSkill(
                job_id=job.id,
                skill_name=skill_name,
                importance=importance,
            )
        )
    return job


# Clear existing data.
db.query(WorkerSkill).delete()
db.query(JobSkill).delete()
db.query(Worker).delete()
db.query(Job).delete()
db.commit()

# Workers.
add_worker(
    "Amara",
    "Accra",
    "GH",
    "I have repaired phones for 5 years. I replace screens, fix charging ports, install apps, talk to customers, buy spare parts, manage payments, and learned basic coding from YouTube.",
    [
        ("repair mobile devices", 0.90, "follow_up_assessment"),
        ("customer service", 0.78, "follow_up_assessment"),
        ("basic programming", 0.62, "self_reported"),
        ("manage payments", 0.74, "follow_up_assessment"),
    ],
)

add_worker(
    "Kwame",
    "Kumasi",
    "GH",
    "I grow maize and cassava, sell produce at the market, manage a small team during harvest season, and keep basic records.",
    [
        ("crop cultivation", 0.86, "follow_up_assessment"),
        ("team management", 0.72, "self_reported"),
        ("record keeping", 0.68, "self_reported"),
    ],
)

add_worker(
    "Sita",
    "Rural Maharashtra",
    "IN",
    "I help my family grow vegetables, track crop sales, coordinate seasonal workers, use a phone for payments, and teach other women how to keep records.",
    [
        ("crop cultivation", 0.84, "follow_up_assessment"),
        ("record keeping", 0.76, "follow_up_assessment"),
        ("team management", 0.70, "self_reported"),
        ("manage payments", 0.66, "self_reported"),
    ],
)

# Jobs by country/context.
for country_code, repair_location, field_location in [
    ("GH", "Accra", "Kumasi"),
    ("IN", "Pune", "Rural Maharashtra"),
    ("KE", "Nakuru", "Nakuru"),
    ("BD", "Dhaka", "Rangpur"),
    ("NG", "Lagos", "Kano"),
]:
    add_job(
        "Mobile Phone Repair Technician",
        repair_location,
        country_code,
        "Diagnose and repair smartphones and mobile devices. Assist customers, manage spare parts inventory, and handle mobile payments.",
        [
            ("repair mobile devices", "required"),
            ("customer service", "required"),
            ("manage inventory", "preferred"),
            ("manage payments", "preferred"),
        ],
    )

    add_job(
        "ICT Support Assistant",
        repair_location,
        country_code,
        "Provide technical support, basic troubleshooting, software installation, and customer-facing help desk support.",
        [
            ("basic programming", "preferred"),
            ("customer service", "required"),
            ("repair mobile devices", "required"),
        ],
    )

    add_job(
        "Junior Software Support Associate",
        repair_location,
        country_code,
        "Maintain simple business software, update websites, troubleshoot user issues, document bugs, and explain technical fixes to non-technical customers.",
        [
            ("software development", "required"),
            ("basic programming", "required"),
            ("troubleshooting", "preferred"),
            ("customer service", "preferred"),
        ],
    )

    add_job(
        "Retail Store Operations Assistant",
        repair_location,
        country_code,
        "Support a small grocery or retail store with sales, customer service, stock tracking, payments, supplier coordination, and daily records.",
        [
            ("retail operations", "required"),
            ("customer service", "required"),
            ("manage inventory", "required"),
            ("manage payments", "preferred"),
            ("sales", "preferred"),
        ],
    )

    add_job(
        "Community Creative Services Assistant",
        repair_location,
        country_code,
        "Produce signs, posters, simple visual designs, murals, and customer-requested painting work for local businesses and community programs.",
        [
            ("painting", "required"),
            ("visual design", "preferred"),
            ("customer service", "preferred"),
        ],
    )

    add_job(
        "Agricultural Field Officer",
        field_location,
        country_code,
        "Support smallholder farmers with crop planning, record keeping, seasonal labor coordination, and field reports.",
        [
            ("crop cultivation", "required"),
            ("record keeping", "required"),
            ("team management", "preferred"),
        ],
    )

db.commit()
print("Demo data seeded - 5 countries, 3 workers, 30 jobs.")
