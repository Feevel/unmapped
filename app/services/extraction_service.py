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
import re

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
    return [skill["name"] for skill in extract_skill_objects_from_text(text)]


def extract_skill_objects_from_text(
    text: str,
    *,
    assess_proficiency: bool = False,
) -> list[dict]:
    """
    Extract skills as structured objects.

    The graph can use `id` as a portable ESCO node key when present,
    while older callers can still use the `name` field only.
    """
    try:
        skills = _extract_via_esco(text)
    except Exception as e:
        logger.warning(f"ESCO extraction failed ({e}), falling back to keyword match.")
        skills = _extract_via_keywords(text)

    if assess_proficiency:
        return [_attach_proficiency_evidence(skill, text) for skill in skills]

    return skills


def _extract_via_esco(text: str) -> list[dict]:
    """
    Use the FAISS/ESCO semantic search pipeline.
    Returns ESCO skill objects.
    """
    from services.vector_store import search_esco
    result = search_esco(text)
    return [
        {
            "id": skill["id"],
            "name": skill["name"],
            "confidence": skill.get("confidence"),
            "source": "esco_semantic_search",
            "source_query": skill.get("source_query"),
            "description": skill.get("description"),
            "explanation": skill.get("explanation"),
        }
        for skill in result["results"]
    ]


def _extract_via_keywords(text: str) -> list[dict]:
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
        "code":      "basic programming",
        "program":   "basic programming",
        "software":  "software development",
        "engineer":  "software development",
        "developer": "software development",
        "debug":     "troubleshooting",
        "website":   "web development",
        "app":       "software development",
        "crop":      "crop cultivation",
        "harvest":   "crop cultivation",
        "farming":   "crop cultivation",
        "inventory": "manage inventory",
        "stock":     "manage inventory",
        "record":    "record keeping",
        "team":      "team management",
        "grocery":   "retail operations",
        "store":     "retail operations",
        "shop":      "retail operations",
        "sell":      "sales",
        "sales":     "sales",
        "business":  "entrepreneurship",
        "owner":     "entrepreneurship",
        "paint":     "painting",
        "painter":   "painting",
        "art":       "visual design",
        "design":    "visual design",
    }

    seen = set()
    for keyword, skill in keyword_map.items():
        if keyword in text and skill not in seen:
            skills.append({
                "id": None,
                "name": skill,
                "confidence": 0.6,
                "source": "keyword_fallback",
                "source_query": keyword,
                "description": None,
                "explanation": f"Matched fallback keyword '{keyword}'",
            })
            seen.add(skill)

    return skills


def _attach_proficiency_evidence(skill: dict, text: str) -> dict:
    """
    Turn onboarding answers into a provisional proficiency signal.

    This is not certification. It is an explainable confidence estimate based on
    evidence the user provided: frequency, duration, autonomy, and task complexity.
    """
    evidence_score, evidence = estimate_proficiency_from_text(text, skill["name"])
    mapping_confidence = skill.get("confidence")

    if mapping_confidence is None:
        final_confidence = evidence_score
    else:
        # Keep semantic mapping confidence in the loop, but let evidence drive
        # the worker proficiency score more strongly.
        final_confidence = 0.35 * float(mapping_confidence) + 0.65 * evidence_score

    enriched = dict(skill)
    enriched["confidence"] = round(min(max(final_confidence, 0.05), 0.95), 3)
    enriched["proficiency_evidence"] = evidence
    enriched["proficiency_basis"] = (
        "Estimated from frequency, duration, autonomy, and complexity evidence in the chat."
    )

    if enriched.get("source") == "keyword_fallback":
        enriched["source"] = "keyword_fallback_with_proficiency"
    elif enriched.get("source"):
        enriched["source"] = f"{enriched['source']}_with_proficiency"
    else:
        enriched["source"] = "proficiency_assessment"

    return enriched


def estimate_proficiency_from_text(text: str, skill_name: str | None = None) -> tuple[float, list[str]]:
    """
    Lightweight rule-based proficiency estimate.

    Returns:
        score: 0.0-1.0 confidence/proficiency estimate
        evidence: human-readable reasons for the score
    """
    lower = text.lower()
    skill = (skill_name or "").lower()
    score = 0.45
    evidence: list[str] = []

    # Frequency evidence
    if any(phrase in lower for phrase in ["daily", "every day", "each day", "full time", "full-time"]):
        score += 0.18
        evidence.append("performs related work daily")
    elif any(phrase in lower for phrase in ["weekly", "every week", "several times a week"]):
        score += 0.12
        evidence.append("performs related work weekly")
    elif any(phrase in lower for phrase in ["occasionally", "sometimes", "once in a while"]):
        score += 0.03
        evidence.append("performs related work occasionally")

    # Duration evidence
    years = [int(value) for value in re.findall(r"\b(\d{1,2})\s*\+?\s*years?\b", lower)]
    if years:
        max_years = max(years)
        if max_years >= 5:
            score += 0.16
            evidence.append(f"has {max_years}+ years of related experience")
        elif max_years >= 2:
            score += 0.11
            evidence.append(f"has {max_years} years of related experience")
        else:
            score += 0.06
            evidence.append("has at least one year of related experience")
    elif any(phrase in lower for phrase in ["since i was", "since age", "for a long time"]):
        score += 0.10
        evidence.append("describes sustained experience over time")

    # Autonomy/business ownership evidence
    if any(
        phrase in lower
        for phrase in [
            "own business",
            "my business",
            "run a business",
            "running a business",
            "by myself",
            "myself",
            "independently",
            "without help",
            "manage",
        ]
    ):
        score += 0.16
        evidence.append("shows autonomy or business ownership")

    # Complexity evidence, lightly tailored by skill family.
    complexity_terms = [
        "build",
        "debug",
        "deploy",
        "software",
        "website",
        "app",
        "diagnose",
        "troubleshoot",
        "replace screens",
        "charging ports",
        "repair",
        "fix",
        "install",
        "inventory",
        "supplier",
        "pricing",
        "payments",
        "complaint",
        "train",
        "teach",
        "coordinate",
        "records",
        "sales",
        "store",
        "shop",
        "paint",
        "design",
    ]
    matched_complexity = [term for term in complexity_terms if term in lower]
    if matched_complexity:
        score += min(0.16, 0.04 * len(matched_complexity))
        evidence.append(f"mentions complex tasks: {', '.join(matched_complexity[:3])}")

    # Skill-specific evidence nudges.
    if "customer" in skill and any(term in lower for term in ["customer", "customers", "complaint", "explain", "talk to"]):
        score += 0.08
        evidence.append("provides customer-facing evidence")
    if any(term in skill for term in ["repair", "mobile", "device"]) and any(
        term in lower for term in ["replace screens", "charging ports", "diagnose", "repair", "fix"]
    ):
        score += 0.08
        evidence.append("provides hands-on technical repair evidence")
    if any(term in skill for term in ["payment", "inventory", "record"]) and any(
        term in lower for term in ["payment", "payments", "inventory", "records", "stock", "supplier"]
    ):
        score += 0.08
        evidence.append("provides business operations evidence")
    if any(term in skill for term in ["software", "programming", "web"]) and any(
        term in lower for term in ["software", "engineer", "code", "coding", "program", "debug", "website", "app"]
    ):
        score += 0.08
        evidence.append("provides software or digital production evidence")
    if any(term in skill for term in ["retail", "sales", "entrepreneurship"]) and any(
        term in lower for term in ["grocery", "store", "shop", "sell", "sales", "business", "owner", "customers"]
    ):
        score += 0.08
        evidence.append("provides retail or business ownership evidence")
    if any(term in skill for term in ["painting", "visual", "design"]) and any(
        term in lower for term in ["paint", "painter", "art", "design", "draw"]
    ):
        score += 0.08
        evidence.append("provides creative production evidence")

    if not evidence:
        evidence.append("skill inferred from description, but proficiency evidence is limited")

    return min(score, 0.95), evidence
