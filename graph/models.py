from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class SkillSource(str, Enum):
    self_reported = "self_reported"
    follow_up_assessment = "follow_up_assessment"
    esco_semantic_search = "esco_semantic_search"
    keyword_fallback = "keyword_fallback"
    credential = "credential"


class SkillImportance(str, Enum):
    required = "required"
    preferred = "preferred"


class ProficiencyLevel(str, Enum):
    unknown = "unknown"
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class WorkerNode(BaseModel):
    worker_id: str
    name: str | None = None
    country_code: str
    location_id: str
    education_level: str | None = None


class JobNode(BaseModel):
    job_id: str
    title: str
    country_code: str
    location_id: str
    sector_id: str | None = None
    occupation_id: str | None = None
    opportunity_type: str = "formal_employment"


class SkillNode(BaseModel):
    esco_id: str
    label: str
    description: str | None = None
    category: str = "esco"


class LocationNode(BaseModel):
    location_id: str
    city: str
    country_code: str
    country_name: str


class SectorNode(BaseModel):
    sector_id: str
    label: str
    classification: str = "local"


class OccupationNode(BaseModel):
    occupation_id: str
    label: str
    taxonomy: str = "ISCO-08"


class LaborSignalNode(BaseModel):
    signal_id: str
    label: str
    value: float | str
    unit: str | None = None
    source: str
    year: int | None = None
    country_code: str | None = None
    sector_id: str | None = None
    occupation_id: str | None = None
    explanation: str | None = None


class AutomationRiskNode(BaseModel):
    risk_id: str
    occupation_id: str
    score: float = Field(ge=0.0, le=1.0)
    level: Literal["low", "medium", "high"]
    source: str
    calibration_note: str | None = None


class WorkerSkillEdge(BaseModel):
    worker_id: str
    esco_id: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    source: SkillSource = SkillSource.esco_semantic_search
    proficiency_level: ProficiencyLevel = ProficiencyLevel.unknown
    evidence: list[str] = Field(default_factory=list)
    assessed_dimensions: dict[str, Any] = Field(default_factory=dict)


class JobSkillEdge(BaseModel):
    job_id: str
    esco_id: str
    importance: SkillImportance = SkillImportance.required


class WorkerProfile(BaseModel):
    worker: WorkerNode
    skills: list[WorkerSkillEdge]
    willing_to_relocate: bool = False


class JobPost(BaseModel):
    job: JobNode
    skills: list[JobSkillEdge]
    remote_ok: bool = False


class SkillGapRecommendation(BaseModel):
    esco_id: str
    label: str
    importance: SkillImportance
    gap_size: Literal["small", "medium", "large"]
    suggested_next_step: str
    reason: str


class MatchResult(BaseModel):
    worker_id: str
    job_id: str
    score: float
    skill_score: float
    location_score: float
    matched_skills: list[str]
    missing_skills: list[SkillGapRecommendation]
    labor_signals: list[LaborSignalNode] = Field(default_factory=list)
    automation_risk: AutomationRiskNode | None = None
    explanation: str
