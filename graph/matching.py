from __future__ import annotations

from dataclasses import dataclass

import networkx as nx

from graph.models import (
    AutomationRiskNode,
    LaborSignalNode,
    MatchResult,
    SkillGapRecommendation,
    SkillImportance,
)


@dataclass(frozen=True)
class ScoringConfig:
    skill_weight: float = 0.80
    location_weight: float = 0.20
    required_weight: float = 1.0
    preferred_weight: float = 0.5
    score_threshold: float = 0.0


def _out_edges_by_type(graph: nx.DiGraph, node_id: str, edge_type: str) -> dict[str, dict]:
    return {
        target: data
        for _, target, data in graph.out_edges(node_id, data=True)
        if data.get("edge_type") == edge_type
    }


def _first_target_by_type(graph: nx.DiGraph, node_id: str, edge_type: str) -> str | None:
    for _, target, data in graph.out_edges(node_id, data=True):
        if data.get("edge_type") == edge_type:
            return target
    return None


def _score_skills(
    worker_skills: dict[str, dict],
    job_skills: dict[str, dict],
    config: ScoringConfig,
) -> tuple[float, list[str], list[tuple[str, SkillImportance]]]:
    possible = 0.0
    earned = 0.0
    matched: list[str] = []
    gaps: list[tuple[str, SkillImportance]] = []

    for esco_id, job_edge in job_skills.items():
        importance = SkillImportance(job_edge.get("importance", SkillImportance.required))
        weight = config.required_weight if importance == SkillImportance.required else config.preferred_weight
        possible += weight

        if esco_id in worker_skills:
            earned += float(worker_skills[esco_id].get("confidence", 1.0)) * weight
            matched.append(esco_id)
        else:
            gaps.append((esco_id, importance))

    if possible == 0:
        return 0.0, matched, gaps
    return earned / possible, matched, gaps


def _score_location(graph: nx.DiGraph, worker_id: str, job_id: str) -> float:
    worker_location = _first_target_by_type(graph, worker_id, "LOCATED_IN")
    job_location = _first_target_by_type(graph, job_id, "BASED_IN")
    if not worker_location or not job_location:
        return 0.5
    return 1.0 if worker_location == job_location else 0.0


def _labor_signals_for_job(graph: nx.DiGraph, job_id: str) -> list[LaborSignalNode]:
    signal_ids: set[str] = set(_out_edges_by_type(graph, job_id, "HAS_SIGNAL"))

    sector_id = _first_target_by_type(graph, job_id, "IN_SECTOR")
    if sector_id:
        signal_ids.update(_out_edges_by_type(graph, sector_id, "HAS_SIGNAL"))

    occupation_id = _first_target_by_type(graph, job_id, "HAS_OCCUPATION")
    if occupation_id:
        signal_ids.update(_out_edges_by_type(graph, occupation_id, "HAS_SIGNAL"))

    return [
        LaborSignalNode(**graph.nodes[signal_id])
        for signal_id in signal_ids
        if graph.nodes[signal_id].get("node_type") == "labor_signal"
    ]


def _automation_risk_for_job(graph: nx.DiGraph, job_id: str) -> AutomationRiskNode | None:
    occupation_id = _first_target_by_type(graph, job_id, "HAS_OCCUPATION")
    if not occupation_id:
        return None

    risk_id = _first_target_by_type(graph, occupation_id, "HAS_AUTOMATION_RISK")
    if not risk_id:
        return None

    return AutomationRiskNode(**graph.nodes[risk_id])


def _gap_recommendations(
    graph: nx.DiGraph,
    gaps: list[tuple[str, SkillImportance]],
    matched_count: int,
) -> list[SkillGapRecommendation]:
    recommendations = []
    for esco_id, importance in gaps:
        label = graph.nodes[esco_id].get("label", esco_id) if esco_id in graph else esco_id
        gap_size = "small" if matched_count >= 2 else "medium"
        if importance == SkillImportance.required and matched_count == 0:
            gap_size = "large"

        recommendations.append(
            SkillGapRecommendation(
                esco_id=esco_id,
                label=label,
                importance=importance,
                gap_size=gap_size,
                suggested_next_step=f"Build evidence for {label} through a short practical task or training module.",
                reason="This skill appears in the job requirements but not yet in the worker profile.",
            )
        )
    return recommendations


def _explain(
    matched_skills: list[str],
    missing_skills: list[SkillGapRecommendation],
    labor_signals: list[LaborSignalNode],
    automation_risk: AutomationRiskNode | None,
    graph: nx.DiGraph,
) -> str:
    matched_labels = [
        graph.nodes[esco_id].get("label", esco_id)
        for esco_id in matched_skills[:3]
    ]
    parts = [f"Matched {len(matched_skills)} skill(s)."]

    if matched_labels:
        parts.append(f"Strongest evidence: {', '.join(matched_labels)}.")
    if missing_skills:
        parts.append(f"Main next step: build evidence for {missing_skills[0].label}.")
    if labor_signals:
        parts.append(f"Includes {len(labor_signals)} local labor market signal(s).")
    if automation_risk:
        parts.append(f"Automation exposure is {automation_risk.level}.")

    return " ".join(parts)


def _score_match(
    graph: nx.DiGraph,
    worker_id: str,
    job_id: str,
    config: ScoringConfig,
) -> MatchResult:
    worker_skills = _out_edges_by_type(graph, worker_id, "HAS_SKILL")
    job_skills = _out_edges_by_type(graph, job_id, "REQUIRES_SKILL")

    skill_score, matched_skills, gaps = _score_skills(worker_skills, job_skills, config)
    location_score = _score_location(graph, worker_id, job_id)
    score = config.skill_weight * skill_score + config.location_weight * location_score

    missing_skills = _gap_recommendations(graph, gaps, len(matched_skills))
    labor_signals = _labor_signals_for_job(graph, job_id)
    automation_risk = _automation_risk_for_job(graph, job_id)

    return MatchResult(
        worker_id=worker_id,
        job_id=job_id,
        score=round(score, 4),
        skill_score=round(skill_score, 4),
        location_score=round(location_score, 4),
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        labor_signals=labor_signals,
        automation_risk=automation_risk,
        explanation=_explain(
            matched_skills,
            missing_skills,
            labor_signals,
            automation_risk,
            graph,
        ),
    )


def match_worker_to_jobs(
    worker_id: str,
    graph: nx.DiGraph,
    config: ScoringConfig | None = None,
) -> list[MatchResult]:
    config = config or ScoringConfig()
    job_ids = [
        node_id
        for node_id, data in graph.nodes(data=True)
        if data.get("node_type") == "job"
    ]
    results = [_score_match(graph, worker_id, job_id, config) for job_id in job_ids]
    return sorted(
        [result for result in results if result.score >= config.score_threshold],
        key=lambda result: result.score,
        reverse=True,
    )


def match_job_to_workers(
    job_id: str,
    graph: nx.DiGraph,
    config: ScoringConfig | None = None,
) -> list[MatchResult]:
    config = config or ScoringConfig()
    worker_ids = [
        node_id
        for node_id, data in graph.nodes(data=True)
        if data.get("node_type") == "worker"
    ]
    results = [_score_match(graph, worker_id, job_id, config) for worker_id in worker_ids]
    return sorted(
        [result for result in results if result.score >= config.score_threshold],
        key=lambda result: result.score,
        reverse=True,
    )
