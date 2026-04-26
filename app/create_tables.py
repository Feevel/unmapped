from app.database import engine
from app.models import Base
from sqlalchemy import inspect, text

Base.metadata.create_all(bind=engine)

SKILL_METADATA_COLUMNS = [
    ("skill_id", "VARCHAR"),
    ("confidence", "FLOAT"),
    ("source", "VARCHAR"),
    ("source_query", "VARCHAR"),
]

JOB_SKILL_METADATA_COLUMNS = SKILL_METADATA_COLUMNS + [
    ("importance", "VARCHAR"),
]

def _existing_columns(table_name: str) -> set[str]:
    return {column["name"] for column in inspect(engine).get_columns(table_name)}


with engine.begin() as conn:
    worker_columns = _existing_columns("worker_skills")
    for column_name, column_type in SKILL_METADATA_COLUMNS:
        if column_name not in worker_columns:
            conn.execute(text(
                f"ALTER TABLE worker_skills ADD COLUMN {column_name} {column_type}"
            ))

    job_columns = _existing_columns("job_skills")
    for column_name, column_type in JOB_SKILL_METADATA_COLUMNS:
        if column_name not in job_columns:
            conn.execute(text(
                f"ALTER TABLE job_skills ADD COLUMN {column_name} {column_type}"
            ))

print("Tables created successfully")
