"""
extraction_service.py
---------------------
Skill extraction for the UNMAPPED API.

Uses the ESCO/FAISS semantic search pipeline (services/vector_store.py)
to extract proper ESCO-mapped skills from free text.

Falls back to keyword matching if the vector store is unavailable
(e.g. during local dev without the FAISS index built yet).
"""

from __future__ import annotations
import logging

logger = logging.getLogger(__name__)


def extract_skills_from_text(text: str) -> list[str]:
    """
    Extract skill names from free text.

    Returns a list of skill label strings (human-readable).
    The caller (worker/job route) stores these as WorkerSkill/JobSkill rows.
    Labels are ESCO-matched when the vector store is available.

    Returns plain skill names — the graph adapter converts these
    to proper esco_ids when building graph nodes.
    """
    try:
        return _extract_via_esco(text)
    except Exception as e:
        logger.warning(f"ESCO extraction failed ({e}), falling back to keyword match.")
        return _extract_via_keywords(text)


def _extract_via_esco(text: str) -> list[str]:
    """
    Use the FAISS/ESCO semantic search pipeline.
    Returns ESCO skill labels (e.g. "repair mobile devices").
    """
    from services.vector_store import search_esco
    result = search_esco(text)
    return [skill["name"] for skill in result["results"]]


def _extract_via_keywords(text: str) -> list[str]:
    """
    Fallback keyword matcher. Used when FAISS index is not built yet.
    Returns plain skill strings — not ESCO mapped.
    """
    skills = []
    text = text.lower()

    keyword_map = {
        "repair":    "repair mobile devices",
        "customer":  "customer service",
        "payment":   "manage payments",
        "coding":    "basic programming",
        "crop":      "crop cultivation",
        "harvest":   "crop cultivation",
        "farming":   "crop cultivation",
        "inventory": "manage inventory",
        "record":    "record keeping",
        "team":      "team management",
    }

    seen = set()
    for keyword, skill in keyword_map.items():
        if keyword in text and skill not in seen:
            skills.append(skill)
            seen.add(skill)

    return skills