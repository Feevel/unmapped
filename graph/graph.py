from __future__ import annotations

import networkx as nx

from graph.models import (
    AutomationRiskNode,
    JobPost,
    LaborSignalNode,
    LocationNode,
    OccupationNode,
    SectorNode,
    SkillNode,
    WorkerProfile,
)


def create_worker_graph(
    profile: WorkerProfile,
    location: LocationNode,
    skill_nodes: list[SkillNode],
) -> nx.DiGraph:
    graph = nx.DiGraph()
    skill_meta = {skill.esco_id: skill for skill in skill_nodes}

    graph.add_node(
        profile.worker.worker_id,
        node_type="worker",
        **profile.worker.model_dump(),
    )
    graph.add_node(
        location.location_id,
        node_type="location",
        **location.model_dump(),
    )
    graph.add_edge(
        profile.worker.worker_id,
        location.location_id,
        edge_type="LOCATED_IN",
        willing_to_relocate=profile.willing_to_relocate,
    )

    for skill_edge in profile.skills:
        meta = skill_meta.get(skill_edge.esco_id)
        graph.add_node(
            skill_edge.esco_id,
            node_type="skill",
            label=meta.label if meta else skill_edge.esco_id,
            description=meta.description if meta else None,
            category=meta.category if meta else "esco",
        )
        graph.add_edge(
            profile.worker.worker_id,
            skill_edge.esco_id,
            edge_type="HAS_SKILL",
            **skill_edge.model_dump(exclude={"worker_id", "esco_id"}),
        )

    return graph


def create_job_graph(
    post: JobPost,
    location: LocationNode,
    skill_nodes: list[SkillNode],
    sector: SectorNode | None = None,
    occupation: OccupationNode | None = None,
    labor_signals: list[LaborSignalNode] | None = None,
    automation_risk: AutomationRiskNode | None = None,
) -> nx.DiGraph:
    graph = nx.DiGraph()
    skill_meta = {skill.esco_id: skill for skill in skill_nodes}

    graph.add_node(
        post.job.job_id,
        node_type="job",
        **post.job.model_dump(),
    )
    graph.add_node(
        location.location_id,
        node_type="location",
        **location.model_dump(),
    )
    graph.add_edge(
        post.job.job_id,
        location.location_id,
        edge_type="BASED_IN",
        remote_ok=post.remote_ok,
    )

    if sector:
        graph.add_node(sector.sector_id, node_type="sector", **sector.model_dump())
        graph.add_edge(post.job.job_id, sector.sector_id, edge_type="IN_SECTOR")

    if occupation:
        graph.add_node(
            occupation.occupation_id,
            node_type="occupation",
            **occupation.model_dump(),
        )
        graph.add_edge(
            post.job.job_id,
            occupation.occupation_id,
            edge_type="HAS_OCCUPATION",
        )

    for skill_edge in post.skills:
        meta = skill_meta.get(skill_edge.esco_id)
        graph.add_node(
            skill_edge.esco_id,
            node_type="skill",
            label=meta.label if meta else skill_edge.esco_id,
            description=meta.description if meta else None,
            category=meta.category if meta else "esco",
        )
        graph.add_edge(
            post.job.job_id,
            skill_edge.esco_id,
            edge_type="REQUIRES_SKILL",
            **skill_edge.model_dump(exclude={"job_id", "esco_id"}),
        )

    for signal in labor_signals or []:
        graph.add_node(
            signal.signal_id,
            node_type="labor_signal",
            **signal.model_dump(),
        )
        if signal.sector_id and signal.sector_id in graph:
            graph.add_edge(signal.sector_id, signal.signal_id, edge_type="HAS_SIGNAL")
        elif signal.occupation_id and signal.occupation_id in graph:
            graph.add_edge(
                signal.occupation_id,
                signal.signal_id,
                edge_type="HAS_SIGNAL",
            )
        else:
            graph.add_edge(post.job.job_id, signal.signal_id, edge_type="HAS_SIGNAL")

    if automation_risk and occupation:
        graph.add_node(
            automation_risk.risk_id,
            node_type="automation_risk",
            **automation_risk.model_dump(),
        )
        graph.add_edge(
            occupation.occupation_id,
            automation_risk.risk_id,
            edge_type="HAS_AUTOMATION_RISK",
        )

    return graph


def merge_graphs(*graphs: nx.DiGraph) -> nx.DiGraph:
    merged = nx.DiGraph()
    for graph in graphs:
        merged.add_nodes_from(graph.nodes(data=True))
        merged.add_edges_from(graph.edges(data=True))
    return merged
