from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey
from app.database import Base


class Worker(Base):
    __tablename__ = "workers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    location = Column(String, nullable=False)
    raw_experience = Column(Text, nullable=False)


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    location = Column(String, nullable=False)
    description = Column(Text, nullable=False)


class WorkerSkill(Base):
    __tablename__ = "worker_skills"

    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("workers.id"))
    skill_name = Column(String, nullable=False)


class JobSkill(Base):
    __tablename__ = "job_skills"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    skill_name = Column(String, nullable=False)


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("workers.id"))
    job_id = Column(Integer, ForeignKey("jobs.id"))
    score = Column(Float, nullable=False)
    reason = Column(Text, nullable=True)