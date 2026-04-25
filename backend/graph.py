"""
graph.py
--------
Graph construction functions for the UNMAPPED matching system.

Takes WorkerProfile and JobPost objects (from models.py) and builds
NetworkX directed graphs. Graphs are merged during matching in matching.py.

No database access here — Part 3 loads data from Postgres and passes
it in as Pydantic objects.
"""

from __future__ import annotations
import networkx as nx
from models import (
    WorkerProfile,
    JobPost,
    SkillNode,
    LocationNode,
)


def create_worker_graph(
    profile: WorkerProfile,
    location: LocationNode,
    skill_nodes: list[SkillNode],
) -> nx.DiGraph:
    """
    Build a directed graph for a single worker.

    Nodes:
        - 1 Worker node
        - N Skill nodes (one per skill the worker has)
        - 1 Location node

    Edges:
        - Worker → Skill   (HAS_SKILL, with confidence + source)
        - Worker → Location (LOCATED_IN, with willing_to_relocate)

    Args:
        profile:     WorkerProfile assembled by Part 2 / Part 3.
        location:    Full LocationNode for this worker (from Part 3 / Postgres).
        skill_nodes: Full SkillNode objects for label/category enrichment.

    Returns:
        nx.DiGraph with node_type attributes on every node.
    """
    G = nx.DiGraph()

    skill_meta = {s.esco_id: s for s in skill_nodes}

    # ── Worker node ──────────────────────────────────────────
    G.add_node(
        profile.worker.worker_id,
        node_type="worker",
        **profile.worker.model_dump(),
    )

    # ── Location node ────────────────────────────────────────
    # Use location_id as the node key so the same city node is
    # shared when worker and job graphs are merged in matching.py.
    G.add_node(
        location.location_id,
        node_type="location",
        **location.model_dump(),
    )
    G.add_edge(
        profile.worker.worker_id,
        location.location_id,
        edge_type="LOCATED_IN",
        willing_to_relocate=profile.location.willing_to_relocate,
    )

    # ── Skill nodes + edges ───────────────────────────────────
    for skill_edge in profile.skills:
        meta = skill_meta.get(skill_edge.esco_id)
        G.add_node(
            skill_edge.esco_id,
            node_type="skill",
            label=meta.label    if meta else skill_edge.esco_id,
            category=meta.category if meta else None,
        )
        G.add_edge(
            profile.worker.worker_id,
            skill_edge.esco_id,
            edge_type="HAS_SKILL",
            confidence=skill_edge.confidence,
            source=skill_edge.source.value,
        )

    return G


def create_job_graph(
    job_post: JobPost,
    location: LocationNode,
    skill_nodes: list[SkillNode],
) -> nx.DiGraph:
    """
    Build a directed graph for a single job posting.

    Nodes:
        - 1 Job node
        - N Skill nodes (one per skill the job requires/prefers)
        - 1 Location node

    Edges:
        - Job → Skill    (REQUIRES_SKILL, with importance)
        - Job → Location (BASED_IN, with remote_ok)

    Args:
        job_post:    JobPost assembled by Part 3.
        location:    Full LocationNode for this job (from Part 3 / Postgres).
        skill_nodes: Full SkillNode objects for label/category enrichment.

    Returns:
        nx.DiGraph with node_type attributes on every node.
    """
    G = nx.DiGraph()

    skill_meta = {s.esco_id: s for s in skill_nodes}

    # ── Job node ─────────────────────────────────────────────
    G.add_node(
        job_post.job.job_id,
        node_type="job",
        **job_post.job.model_dump(),
    )

    # ── Location node ────────────────────────────────────────
    G.add_node(
        location.location_id,
        node_type="location",
        **location.model_dump(),
    )
    G.add_edge(
        job_post.job.job_id,
        location.location_id,
        edge_type="BASED_IN",
        remote_ok=job_post.location.remote_ok,
    )

    # ── Skill nodes + edges ───────────────────────────────────
    for skill_edge in job_post.skills:
        meta = skill_meta.get(skill_edge.esco_id)
        G.add_node(
            skill_edge.esco_id,
            node_type="skill",
            label=meta.label       if meta else skill_edge.esco_id,
            category=meta.category if meta else None,
        )
        G.add_edge(
            job_post.job.job_id,
            skill_edge.esco_id,
            edge_type="REQUIRES_SKILL",
            importance=skill_edge.importance.value,
        )

    return G


def merge_graphs(*graphs: nx.DiGraph) -> nx.DiGraph:
    """
    Merge multiple worker/job graphs into one combined graph.

    Shared nodes (same skill esco_id, same location_id) are
    automatically unified — this is what enables traversal across
    workers and jobs that share skills or locations.

    Used by matching.py to build the full graph before traversal.
    """
    combined = nx.DiGraph()
    for G in graphs:
        combined.add_nodes_from(G.nodes(data=True))
        combined.add_edges_from(G.edges(data=True))
    return combined