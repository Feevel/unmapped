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
    Extract skill names from free text.  Returns human-readable label strings.
    """
    return [skill["name"] for skill in extract_skill_objects_from_text(text)]


def extract_skill_objects_from_text(
    text: str,
    *,
    assess_proficiency: bool = False,
) -> list[dict]:
    """
    Extract skills as structured objects with optional proficiency evidence.
    """
    try:
        skills = _extract_via_esco(text)
    except Exception as exc:
        logger.warning(
            "ESCO extraction failed (%s: %s), falling back to keyword match.",
            type(exc).__name__,
            exc,
        )
        skills = _extract_via_keywords(text)

    if assess_proficiency:
        return [_attach_proficiency_evidence(skill, text) for skill in skills]

    return skills


def _extract_via_esco(text: str) -> list[dict]:
    """Use the FAISS/ESCO semantic search pipeline."""
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
    Fallback keyword matcher. Returns plain skill strings — not ESCO mapped.
    skill_id is None here; the graph adapter will derive a local slug.
    """
    skills = []
    lower = text.lower()

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

    seen: set[str] = set()
    for keyword, skill in keyword_map.items():
        if keyword in lower and skill not in seen:
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
    Attach a provisional proficiency signal derived from the onboarding answers.

    Score composition (max 1.0):
        base          0.35
        frequency     up to +0.15
        duration      up to +0.15
        autonomy      up to +0.15
        complexity    up to +0.10   (capped internally)
        skill-specific up to +0.10

    Total ceiling before clamp: 0.35 + 0.15 + 0.15 + 0.15 + 0.10 + 0.10 = 1.00
    All additive terms are bounded so the raw sum cannot meaningfully exceed 1.0.
    """
    evidence_score, evidence = estimate_proficiency_from_text(text, skill["name"])
    mapping_confidence = skill.get("confidence")

    if mapping_confidence is None:
        final_confidence = evidence_score
    else:
        # Weight evidence (0.65) more strongly than ESCO mapping confidence (0.35).
        final_confidence = 0.35 * float(mapping_confidence) + 0.65 * evidence_score

    enriched = dict(skill)
    enriched["confidence"] = round(min(max(final_confidence, 0.05), 0.95), 3)
    enriched["proficiency_evidence"] = evidence
    enriched["proficiency_basis"] = (
        "Estimated from frequency, duration, autonomy, and complexity evidence in the chat."
    )

    source = enriched.get("source") or "proficiency_assessment"
    enriched["source"] = (
        f"{source}_with_proficiency"
        if source != "proficiency_assessment"
        else source
    )

    return enriched


def estimate_proficiency_from_text(
    text: str,
    skill_name: str | None = None,
) -> tuple[float, list[str]]:
    """
    Lightweight rule-based proficiency estimate.

    Each bonus bucket has a hard cap so the total cannot overflow 1.0.

    Returns:
        score   — 0.0–1.0 confidence/proficiency estimate
        evidence — human-readable reasons for the score
    """
    lower = text.lower()
    skill = (skill_name or "").lower()
    evidence: list[str] = []

    # ── Base ──────────────────────────────────────────────────────────────────
    score = 0.35

    # ── Frequency  (max +0.15) ────────────────────────────────────────────────
    if any(p in lower for p in ["daily", "every day", "each day", "full time", "full-time"]):
        score += 0.15
        evidence.append("performs related work daily")
    elif any(p in lower for p in ["weekly", "every week", "several times a week"]):
        score += 0.10
        evidence.append("performs related work weekly")
    elif any(p in lower for p in ["occasionally", "sometimes", "once in a while"]):
        score += 0.03
        evidence.append("performs related work occasionally")

    # ── Duration  (max +0.15) ─────────────────────────────────────────────────
    years = [int(v) for v in re.findall(r"\b(\d{1,2})\s*\+?\s*years?\b", lower)]
    if years:
        max_years = max(years)
        if max_years >= 5:
            score += 0.15
            evidence.append(f"has {max_years}+ years of related experience")
        elif max_years >= 2:
            score += 0.10
            evidence.append(f"has {max_years} years of related experience")
        else:
            score += 0.05
            evidence.append("has at least one year of related experience")
    elif any(p in lower for p in ["since i was", "since age", "for a long time"]):
        score += 0.08
        evidence.append("describes sustained experience over time")

    # ── Autonomy / ownership  (max +0.15) ────────────────────────────────────
    if any(
        p in lower
        for p in [
            "own business", "my business", "run a business", "running a business",
            "by myself", "myself", "independently", "without help", "manage",
        ]
    ):
        score += 0.15
        evidence.append("shows autonomy or business ownership")

    # ── Complexity  (max +0.10) ───────────────────────────────────────────────
    complexity_terms = [
        "build", "debug", "deploy", "software", "website", "app",
        "diagnose", "troubleshoot", "replace screens", "charging ports",
        "repair", "fix", "install", "inventory", "supplier", "pricing",
        "payments", "complaint", "train", "teach", "coordinate", "records",
        "sales", "store", "shop", "paint", "design",
    ]
    matched_complexity = [t for t in complexity_terms if t in lower]
    if matched_complexity:
        # 0.025 per term, hard-capped at 0.10
        complexity_bonus = min(0.025 * len(matched_complexity), 0.10)
        score += complexity_bonus
        evidence.append(f"mentions complex tasks: {', '.join(matched_complexity[:3])}")

    # ── Skill-specific nudge  (max +0.10) ────────────────────────────────────
    skill_bonus = 0.0
    if "customer" in skill and any(
        t in lower for t in ["customer", "customers", "complaint", "explain", "talk to"]
    ):
        skill_bonus = 0.10
        evidence.append("provides customer-facing evidence")
    elif any(t in skill for t in ["repair", "mobile", "device"]) and any(
        t in lower for t in ["replace screens", "charging ports", "diagnose", "repair", "fix"]
    ):
        skill_bonus = 0.10
        evidence.append("provides hands-on technical repair evidence")
    elif any(t in skill for t in ["payment", "inventory", "record"]) and any(
        t in lower for t in ["payment", "payments", "inventory", "records", "stock", "supplier"]
    ):
        skill_bonus = 0.10
        evidence.append("provides business operations evidence")
    elif any(t in skill for t in ["software", "programming", "web"]) and any(
        t in lower for t in ["software", "engineer", "code", "coding", "program", "debug", "website", "app"]
    ):
        skill_bonus = 0.10
        evidence.append("provides software or digital production evidence")
    elif any(t in skill for t in ["retail", "sales", "entrepreneurship"]) and any(
        t in lower for t in ["grocery", "store", "shop", "sell", "sales", "business", "owner", "customers"]
    ):
        skill_bonus = 0.10
        evidence.append("provides retail or business ownership evidence")
    elif any(t in skill for t in ["painting", "visual", "design"]) and any(
        t in lower for t in ["paint", "painter", "art", "design", "draw"]
    ):
        skill_bonus = 0.10
        evidence.append("provides creative production evidence")

    score += skill_bonus

    if not evidence:
        evidence.append("skill inferred from description, but proficiency evidence is limited")

    return round(min(max(score, 0.05), 0.95), 3), evidence
