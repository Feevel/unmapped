"""
models.py
---------
All Pydantic models for the UNMAPPED graph system.

Imported by:
  - graph.py      (graph construction)
  - matching.py   (scoring and traversal)
  - Part 2        (LLM extraction — needs WorkerProfile, JobPost)
  - Part 3        (API / DB — needs all models for serialization)
"""

from __future__ import annotations
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field


# ─────────────────────────────────────────────────────────────
# Enums
# ─────────────────────────────────────────────────────────────

class SkillSource(str, Enum):
    formal   = "formal"    # from a recognised credential
    informal = "informal"  # self-taught or gained through work experience
    assessed = "assessed"  # extracted by Part 2 chatbot


class SkillImportance(str, Enum):
    required  = "required"
    preferred = "preferred"


# ─────────────────────────────────────────────────────────────
# Node models
# ─────────────────────────────────────────────────────────────

class WorkerNode(BaseModel):
    worker_id:       str
    name:            str
    education_level: str   # "none" | "primary" | "secondary" | "tertiary"
    country_code:    str   # ISO 3166-1 alpha-2, e.g. "GH", "KE", "PH"


class SkillNode(BaseModel):
    esco_id:  str               # ESCO URI or short ID
    label:    str               # human-readable, e.g. "Python programming"
    category: Optional[str] = None  # ESCO skill group label


class JobNode(BaseModel):
    job_id:    str
    title:     str
    sector:    str              # e.g. "ICT", "Agriculture", "Construction"
    isco_code: Optional[str] = None  # ISCO-08 occupation code


class LocationNode(BaseModel):
    location_id:  str   # stable key, e.g. "GH-ACC". shared across workers & jobs
    city:         str
    country:      str
    country_code: str   # ISO 3166-1 alpha-2


# ─────────────────────────────────────────────────────────────
# Edge models
# ─────────────────────────────────────────────────────────────

class WorkerSkillEdge(BaseModel):
    worker_id:  str
    esco_id:    str
    confidence: float = Field(ge=0.0, le=1.0)  # 0.0 = uncertain, 1.0 = verified
    source:     SkillSource


class JobSkillEdge(BaseModel):
    job_id:     str
    esco_id:    str
    importance: SkillImportance


class WorkerLocationEdge(BaseModel):
    worker_id:           str
    location_id:         str
    willing_to_relocate: bool = False


class JobLocationEdge(BaseModel):
    job_id:      str
    location_id: str
    remote_ok:   bool = False


# ─────────────────────────────────────────────────────────────
# Full profile inputs
# Assembled by Part 2 (extraction) and stored by Part 3 (DB).
# Passed into graph construction functions as a single object.
# ─────────────────────────────────────────────────────────────

class WorkerProfile(BaseModel):
    worker:   WorkerNode
    skills:   list[WorkerSkillEdge]
    location: WorkerLocationEdge


class JobPost(BaseModel):
    job:      JobNode
    skills:   list[JobSkillEdge]
    location: JobLocationEdge


# ─────────────────────────────────────────────────────────────
# Match output
# Returned by matching.py, enriched with econometric signals
# by Part 3 before being sent to the frontend.
# ─────────────────────────────────────────────────────────────

class SkillGap(BaseModel):
    esco_id:    str
    label:      str
    importance: SkillImportance


class MatchResult(BaseModel):
    worker_id:      str
    job_id:         str

    # ── scores ──────────────────────────────────────────────
    score:          float  # final weighted score, 0.0 – 1.0
    skill_score:    float  # skill component, 0.0 – 1.0
    location_score: float  # location component, 0.0 – 1.0

    # ── skill detail ────────────────────────────────────────
    matched_skills: list[str]       # esco_ids that matched
    missing_skills: list[SkillGap]  # gaps with importance level

    # ── human-readable explanation for frontend ──────────────
    # e.g. "Matched 4 of 5 required skills. Same city."
    # Part 3 passes this directly to the UI — keep it plain English.
    explanation: str


class EnrichedMatchResult(MatchResult):
    """
    MatchResult extended by Part 3 with econometric signals.
    Defined here so Part 3 can import and extend without redefining
    the base fields. All econometric fields are Optional — data may
    not exist for every country/sector combination.
    """
    # ── job metadata (from Postgres) ────────────────────────
    job_title:   str = ""
    sector:      str = ""
    city:        str = ""

    # ── econometric signals (from ILO / World Bank / Frey-Osborne) ──
    wage_floor_usd:    Optional[float] = None  # ILO ILOSTAT
    sector_growth_pct: Optional[float] = None  # World Bank WDI
    automation_risk:   Optional[float] = None  # Frey-Osborne, 0.0 – 1.0
    data_year:         Optional[int]   = None  # year the signal data is from