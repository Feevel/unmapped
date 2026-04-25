"""
matching.py
-----------
Graph traversal and match scoring for the UNMAPPED system.

Core logic:
  - Skill score: weighted by importance (required > preferred)
    and confidence (credentialed > informal > assessed).
  - Location score: exact match > flexible (relocate/remote) > mismatch.
  - Final score: skill (80%) + location (20%).

Weights are configurable via ScoringConfig so deployers can
tune for different country/program contexts without changing code.

Public API (called by Part 3):
  match_worker_to_jobs(worker_id, G) -> list[MatchResult]
  match_job_to_workers(job_id, G)    -> list[MatchResult]
"""

from __future__ import annotations
from dataclasses import dataclass, field
import networkx as nx
from models import MatchResult, SkillGap, SkillImportance


# ─────────────────────────────────────────────────────────────
# Scoring configuration
# Passed in by Part 3 — different values per country/program.
# ─────────────────────────────────────────────────────────────

@dataclass
class ScoringConfig:
    # Final score weights — must sum to 1.0
    skill_weight:    float = 0.80
    location_weight: float = 0.20

    # Skill importance weights
    required_weight:  float = 1.0
    preferred_weight: float = 0.5

    # Location score values
    location_exact:    float = 1.0  # same location_id
    location_flexible: float = 0.5  # willing_to_relocate or remote_ok
    location_mismatch: float = 0.0  # different location, no flexibility

    # Minimum score to include in results
    score_threshold: float = 0.0


# ─────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────

def _get_worker_skills(G: nx.DiGraph, worker_id: str) -> dict[str, dict]:
    """
    Return {esco_id: edge_data} for all skills a worker has.
    Edge data includes: confidence, source.
    """
    return {
        target: data
        for _, target, data in G.out_edges(worker_id, data=True)
        if data.get("edge_type") == "HAS_SKILL"
    }


def _get_job_skills(G: nx.DiGraph, job_id: str) -> dict[str, dict]:
    """
    Return {esco_id: edge_data} for all skills a job requires.
    Edge data includes: importance.
    """
    return {
        target: data
        for _, target, data in G.out_edges(job_id, data=True)
        if data.get("edge_type") == "REQUIRES_SKILL"
    }


def _get_location_id(G: nx.DiGraph, node_id: str, edge_type: str) -> tuple[str | None, dict]:
    """
    Return (location_id, edge_data) for a worker or job node.
    edge_type is "LOCATED_IN" for workers, "BASED_IN" for jobs.
    """
    for _, target, data in G.out_edges(node_id, data=True):
        if data.get("edge_type") == edge_type:
            return target, data
    return None, {}


def _score_skills(
    worker_skills: dict[str, dict],
    job_skills: dict[str, dict],
    config: ScoringConfig,
) -> tuple[float, list[str], list[tuple[str, str]]]:
    """
    Compute skill score, matched skill ids, and missing skill gaps.

    For each job skill:
      - If worker has it: earn (confidence × importance_weight)
      - If worker lacks it: lose (importance_weight) — added to gaps

    Returns:
        skill_score:    float 0.0 – 1.0
        matched_skills: list of esco_ids that matched
        gaps:           list of (esco_id, importance) for missing skills
    """
    total_possible = 0.0
    total_earned   = 0.0
    matched_skills = []
    gaps           = []

    for esco_id, job_edge in job_skills.items():
        importance = job_edge.get("importance", SkillImportance.required.value)
        imp_weight = (
            config.required_weight
            if importance == SkillImportance.required.value
            else config.preferred_weight
        )
        total_possible += imp_weight

        if esco_id in worker_skills:
            confidence = worker_skills[esco_id].get("confidence", 1.0)
            total_earned += confidence * imp_weight
            matched_skills.append(esco_id)
        else:
            gaps.append((esco_id, importance))

    if total_possible == 0:
        return 0.0, [], []

    return total_earned / total_possible, matched_skills, gaps


def _score_location(
    G: nx.DiGraph,
    worker_id: str,
    job_id: str,
    config: ScoringConfig,
) -> float:
    """
    Compute location score based on proximity and flexibility.

      1.0 — same location_id
      0.5 — different location, but worker willing_to_relocate OR job remote_ok
      0.0 — different location, no flexibility on either side
    """
    worker_loc, worker_edge = _get_location_id(G, worker_id, "LOCATED_IN")
    job_loc,    job_edge    = _get_location_id(G, job_id,    "BASED_IN")

    if worker_loc is None or job_loc is None:
        # Missing location data — neutral, don't penalise
        return config.location_flexible

    if worker_loc == job_loc:
        return config.location_exact

    willing_to_relocate = worker_edge.get("willing_to_relocate", False)
    remote_ok           = job_edge.get("remote_ok", False)

    if willing_to_relocate or remote_ok:
        return config.location_flexible

    return config.location_mismatch


def _build_explanation(
    matched_skills: list[str],
    gaps: list[tuple[str, str]],
    skill_score: float,
    location_score: float,
    G: nx.DiGraph,
    config: ScoringConfig,
) -> str:
    """
    Build a plain-English explanation for the frontend.
    Amara should be able to read this without any technical knowledge.
    """
    required_gaps  = [g for g in gaps if g[1] == SkillImportance.required.value]
    preferred_gaps = [g for g in gaps if g[1] == SkillImportance.preferred.value]

    total_job_skills = len(matched_skills) + len(gaps)
    parts = []

    # Skill summary
    parts.append(
        f"Matched {len(matched_skills)} of {total_job_skills} skills."
    )

    # Required gaps — named if labels are available
    if required_gaps:
        gap_labels = []
        for esco_id, _ in required_gaps[:3]:  # cap at 3 for readability
            label = G.nodes[esco_id].get("label", esco_id) if esco_id in G else esco_id
            gap_labels.append(label)
        more = len(required_gaps) - len(gap_labels)
        label_str = ", ".join(gap_labels)
        if more > 0:
            label_str += f" and {more} more"
        parts.append(f"Missing required skills: {label_str}.")

    # Preferred gaps — just count
    if preferred_gaps:
        parts.append(f"Missing {len(preferred_gaps)} preferred skill(s).")

    # Location summary
    if location_score == config.location_exact:
        parts.append("Same city.")
    elif location_score == config.location_flexible:
        parts.append("Different city, but open to remote or relocation.")
    else:
        parts.append("Different city with no flexibility indicated.")

    return " ".join(parts)


def _score_match(
    G: nx.DiGraph,
    worker_id: str,
    job_id: str,
    config: ScoringConfig,
) -> MatchResult:
    """
    Compute a full MatchResult for one worker–job pair.
    """
    worker_skills = _get_worker_skills(G, worker_id)
    job_skills    = _get_job_skills(G, job_id)

    skill_score, matched_skills, gaps = _score_skills(
        worker_skills, job_skills, config
    )
    location_score = _score_location(G, worker_id, job_id, config)

    final_score = (
        skill_score    * config.skill_weight +
        location_score * config.location_weight
    )

    # Build SkillGap objects with human-readable labels
    missing_skills = []
    for esco_id, importance in gaps:
        label = G.nodes[esco_id].get("label", esco_id) if esco_id in G else esco_id
        missing_skills.append(SkillGap(
            esco_id=esco_id,
            label=label,
            importance=SkillImportance(importance),
        ))

    explanation = _build_explanation(
        matched_skills, gaps, skill_score, location_score, G, config
    )

    return MatchResult(
        worker_id=worker_id,
        job_id=job_id,
        score=round(final_score, 4),
        skill_score=round(skill_score, 4),
        location_score=round(location_score, 4),
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        explanation=explanation,
    )


# ─────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────

def match_worker_to_jobs(
    worker_id: str,
    G: nx.DiGraph,
    config: ScoringConfig | None = None,
) -> list[MatchResult]:
    """
    Find and rank all jobs in the graph for a given worker.

    Args:
        worker_id: ID of the worker node in G.
        G:         Merged graph containing worker, job, skill,
                   and location nodes (built via graph.merge_graphs).
        config:    ScoringConfig — pass a custom one for different
                   country/program contexts. Defaults to ScoringConfig().

    Returns:
        List of MatchResult, sorted by score descending.
        Results below config.score_threshold are excluded.
    """
    if config is None:
        config = ScoringConfig()

    job_ids = [
        n for n, d in G.nodes(data=True)
        if d.get("node_type") == "job"
    ]

    results = []
    for job_id in job_ids:
        result = _score_match(G, worker_id, job_id, config)
        if result.score >= config.score_threshold:
            results.append(result)

    return sorted(results, key=lambda r: r.score, reverse=True)


def match_job_to_workers(
    job_id: str,
    G: nx.DiGraph,
    config: ScoringConfig | None = None,
) -> list[MatchResult]:
    """
    Find and rank all workers in the graph for a given job.

    Args:
        job_id: ID of the job node in G.
        G:      Merged graph containing worker, job, skill,
                and location nodes.
        config: ScoringConfig — pass a custom one for different
                country/program contexts. Defaults to ScoringConfig().

    Returns:
        List of MatchResult, sorted by score descending.
        Results below config.score_threshold are excluded.
    """
    if config is None:
        config = ScoringConfig()

    worker_ids = [
        n for n, d in G.nodes(data=True)
        if d.get("node_type") == "worker"
    ]

    results = []
    for worker_id in worker_ids:
        result = _score_match(G, worker_id, job_id, config)
        if result.score >= config.score_threshold:
            results.append(result)

    return sorted(results, key=lambda r: r.score, reverse=True)