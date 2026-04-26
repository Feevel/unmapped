"""
seed_demo_data.py
-----------------
Populates the DB with multi-country demo contexts.
Run before demoing:
    python -m app.scripts.seed_demo_data

ESCO skill IDs use a consistent synthetic URI scheme so the graph
matching engine compares stable IDs rather than slugified label strings.
Real ESCO URIs can be swapped in here once the FAISS index is built.
"""

from app.database import SessionLocal
from app.models import Worker, WorkerSkill, Job, JobSkill

db = SessionLocal()

# ---------------------------------------------------------------------------
# Canonical ESCO skill registry
# Each skill gets one stable URI used across workers AND jobs so the graph
# matching engine can join them correctly.  Replace values with real ESCO
# concept URIs (e.g. http://data.europa.eu/esco/skill/...) once available.
# ---------------------------------------------------------------------------

ESCO = {
    "repair_mobile_devices":  "http://data.europa.eu/esco/skill/demo-repair-mobile-devices",
    "customer_service":       "http://data.europa.eu/esco/skill/demo-customer-service",
    "manage_payments":        "http://data.europa.eu/esco/skill/demo-manage-payments",
    "basic_programming":      "http://data.europa.eu/esco/skill/demo-basic-programming",
    "software_development":   "http://data.europa.eu/esco/skill/demo-software-development",
    "troubleshooting":        "http://data.europa.eu/esco/skill/demo-troubleshooting",
    "web_development":        "http://data.europa.eu/esco/skill/demo-web-development",
    "crop_cultivation":       "http://data.europa.eu/esco/skill/demo-crop-cultivation",
    "manage_inventory":       "http://data.europa.eu/esco/skill/demo-manage-inventory",
    "record_keeping":         "http://data.europa.eu/esco/skill/demo-record-keeping",
    "team_management":        "http://data.europa.eu/esco/skill/demo-team-management",
    "retail_operations":      "http://data.europa.eu/esco/skill/demo-retail-operations",
    "sales":                  "http://data.europa.eu/esco/skill/demo-sales",
    "entrepreneurship":       "http://data.europa.eu/esco/skill/demo-entrepreneurship",
    "painting":               "http://data.europa.eu/esco/skill/demo-painting",
    "visual_design":          "http://data.europa.eu/esco/skill/demo-visual-design",
}

# Human-readable labels for each URI (used by the graph for display)
ESCO_LABELS = {v: k.replace("_", " ") for k, v in ESCO.items()}


def add_worker(
    name: str,
    location: str,
    country_code: str,
    raw_experience: str,
    skills: list[tuple[str, float, str]],   # (skill_key, confidence, source)
) -> Worker:
    worker = Worker(
        name=name,
        location=location,
        country_code=country_code,
        raw_experience=raw_experience,
    )
    db.add(worker)
    db.commit()
    db.refresh(worker)
    for skill_key, confidence, source in skills:
        db.add(
            WorkerSkill(
                worker_id=worker.id,
                skill_name=ESCO_LABELS.get(ESCO[skill_key], skill_key.replace("_", " ")),
                skill_id=ESCO[skill_key],          # ← stable URI now populated
                confidence=confidence,
                source=source,
            )
        )
    return worker


def add_job(
    title: str,
    location: str,
    country_code: str,
    description: str,
    skills: list[tuple[str, str]],          # (skill_key, importance)
) -> Job:
    job = Job(
        title=title,
        location=location,
        country_code=country_code,
        description=description,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    for skill_key, importance in skills:
        db.add(
            JobSkill(
                job_id=job.id,
                skill_name=ESCO_LABELS.get(ESCO[skill_key], skill_key.replace("_", " ")),
                skill_id=ESCO[skill_key],          # ← stable URI now populated
                importance=importance,
            )
        )
    return job


# ---------------------------------------------------------------------------
# Clear existing data
# ---------------------------------------------------------------------------

db.query(WorkerSkill).delete()
db.query(JobSkill).delete()
db.query(Worker).delete()
db.query(Job).delete()
db.commit()

# ---------------------------------------------------------------------------
# Workers
# ---------------------------------------------------------------------------

add_worker(
    "Amara",
    "Accra",
    "GH",
    "I have repaired phones for 5 years. I replace screens, fix charging ports, "
    "install apps, talk to customers, buy spare parts, manage payments, and learned "
    "basic coding from YouTube.",
    [
        ("repair_mobile_devices", 0.90, "follow_up_assessment"),
        ("customer_service",      0.78, "follow_up_assessment"),
        ("basic_programming",     0.62, "self_reported"),
        ("manage_payments",       0.74, "follow_up_assessment"),
    ],
)

add_worker(
    "Kwame",
    "Kumasi",
    "GH",
    "I grow maize and cassava, sell produce at the market, manage a small team "
    "during harvest season, and keep basic records.",
    [
        ("crop_cultivation", 0.86, "follow_up_assessment"),
        ("team_management",  0.72, "self_reported"),
        ("record_keeping",   0.68, "self_reported"),
    ],
)

add_worker(
    "Sita",
    "Rural Maharashtra",
    "IN",
    "I help my family grow vegetables, track crop sales, coordinate seasonal workers, "
    "use a phone for payments, and teach other women how to keep records.",
    [
        ("crop_cultivation", 0.84, "follow_up_assessment"),
        ("record_keeping",   0.76, "follow_up_assessment"),
        ("team_management",  0.70, "self_reported"),
        ("manage_payments",  0.66, "self_reported"),
    ],
)

# ---------------------------------------------------------------------------
# Jobs — one set per country
# ---------------------------------------------------------------------------

for country_code, repair_location, field_location in [
    ("GH", "Accra",   "Kumasi"),
    ("IN", "Pune",    "Rural Maharashtra"),
    ("KE", "Nakuru",  "Nakuru"),
    ("BD", "Dhaka",   "Rangpur"),
    ("NG", "Lagos",   "Kano"),
]:
    add_job(
        "Mobile Phone Repair Technician",
        repair_location,
        country_code,
        "Diagnose and repair smartphones and mobile devices. Assist customers, "
        "manage spare parts inventory, and handle mobile payments.",
        [
            ("repair_mobile_devices", "required"),
            ("customer_service",      "required"),
            ("manage_inventory",      "preferred"),
            ("manage_payments",       "preferred"),
        ],
    )

    add_job(
        "ICT Support Assistant",
        repair_location,
        country_code,
        "Provide technical support, basic troubleshooting, software installation, "
        "and customer-facing help desk support.",
        [
            ("basic_programming",    "preferred"),
            ("customer_service",     "required"),
            ("repair_mobile_devices","required"),
        ],
    )

    add_job(
        "Junior Software Support Associate",
        repair_location,
        country_code,
        "Maintain simple business software, update websites, troubleshoot user issues, "
        "document bugs, and explain technical fixes to non-technical customers.",
        [
            ("software_development", "required"),
            ("basic_programming",    "required"),
            ("troubleshooting",      "preferred"),
            ("customer_service",     "preferred"),
        ],
    )

    add_job(
        "Retail Store Operations Assistant",
        repair_location,
        country_code,
        "Support a small grocery or retail store with sales, customer service, stock "
        "tracking, payments, supplier coordination, and daily records.",
        [
            ("retail_operations", "required"),
            ("customer_service",  "required"),
            ("manage_inventory",  "required"),
            ("manage_payments",   "preferred"),
            ("sales",             "preferred"),
        ],
    )

    add_job(
        "Community Creative Services Assistant",
        repair_location,
        country_code,
        "Produce signs, posters, simple visual designs, murals, and customer-requested "
        "painting work for local businesses and community programs.",
        [
            ("painting",       "required"),
            ("visual_design",  "preferred"),
            ("customer_service","preferred"),
        ],
    )

    add_job(
        "Agricultural Field Officer",
        field_location,
        country_code,
        "Support smallholder farmers with crop planning, record keeping, seasonal "
        "labour coordination, and field reports.",
        [
            ("crop_cultivation", "required"),
            ("record_keeping",   "required"),
            ("team_management",  "preferred"),
        ],
    )

db.commit()
print("Demo data seeded — 5 countries, 3 workers, 30 jobs, with stable ESCO URIs.")
