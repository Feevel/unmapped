from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from graph.graph import create_job_graph, create_worker_graph, merge_graphs
from graph.matching import match_worker_to_jobs
from graph.models import (
    AutomationRiskNode,
    JobNode,
    JobPost,
    JobSkillEdge,
    LaborSignalNode,
    LocationNode,
    OccupationNode,
    ProficiencyLevel,
    SectorNode,
    SkillImportance,
    SkillNode,
    SkillSource,
    WorkerNode,
    WorkerProfile,
    WorkerSkillEdge,
)


PHONE_REPAIR_SKILL = "http://data.europa.eu/esco/skill/demo-repair-mobile-devices"
CUSTOMER_SERVICE_SKILL = "http://data.europa.eu/esco/skill/demo-customer-service"
INVENTORY_SKILL = "http://data.europa.eu/esco/skill/demo-manage-inventory"


def build_demo_graph():
    accra = LocationNode(
        location_id="GH-ACC",
        city="Accra",
        country_code="GH",
        country_name="Ghana",
    )

    skills = [
        SkillNode(esco_id=PHONE_REPAIR_SKILL, label="repair mobile devices"),
        SkillNode(esco_id=CUSTOMER_SERVICE_SKILL, label="provide customer service"),
        SkillNode(esco_id=INVENTORY_SKILL, label="manage inventory"),
    ]

    worker = WorkerProfile(
        worker=WorkerNode(
            worker_id="amara",
            name="Amara",
            country_code="GH",
            location_id="GH-ACC",
            education_level="secondary",
        ),
        skills=[
            WorkerSkillEdge(
                worker_id="amara",
                esco_id=PHONE_REPAIR_SKILL,
                confidence=0.90,
                source=SkillSource.follow_up_assessment,
                proficiency_level=ProficiencyLevel.advanced,
                evidence=[
                    "Has repaired phones for five years",
                    "Replaces screens and charging ports independently",
                ],
                assessed_dimensions={
                    "autonomy": "high",
                    "complexity": "medium",
                    "frequency": "daily",
                },
            ),
            WorkerSkillEdge(
                worker_id="amara",
                esco_id=CUSTOMER_SERVICE_SKILL,
                confidence=0.78,
                source=SkillSource.follow_up_assessment,
                proficiency_level=ProficiencyLevel.intermediate,
                evidence=[
                    "Talks to repair customers directly",
                    "Explains prices and repair options",
                ],
                assessed_dimensions={
                    "communication": "strong",
                    "complaint_handling": "some_evidence",
                },
            ),
        ],
    )

    job = JobPost(
        job=JobNode(
            job_id="job_1",
            title="Mobile Phone Repair Assistant",
            country_code="GH",
            location_id="GH-ACC",
            sector_id="ict_services",
            occupation_id="isco_7422",
            opportunity_type="formal_employment",
        ),
        skills=[
            JobSkillEdge(
                job_id="job_1",
                esco_id=PHONE_REPAIR_SKILL,
                importance=SkillImportance.required,
            ),
            JobSkillEdge(
                job_id="job_1",
                esco_id=CUSTOMER_SERVICE_SKILL,
                importance=SkillImportance.required,
            ),
            JobSkillEdge(
                job_id="job_1",
                esco_id=INVENTORY_SKILL,
                importance=SkillImportance.preferred,
            ),
        ],
    )

    worker_graph = create_worker_graph(worker, accra, skills)
    job_graph = create_job_graph(
        job,
        accra,
        skills,
        sector=SectorNode(sector_id="ict_services", label="ICT services"),
        occupation=OccupationNode(
            occupation_id="isco_7422",
            label="ICT installers and servicers",
        ),
        labor_signals=[
            LaborSignalNode(
                signal_id="gh_ict_employment_share",
                label="Employment in ICT services",
                value="demo value",
                source="World Bank / ILOSTAT placeholder",
                year=2024,
                country_code="GH",
                sector_id="ict_services",
                explanation="Replace this with the real signal from Person 3's data layer.",
            ),
            LaborSignalNode(
                signal_id="gh_wage_employment_share",
                label="Wage and salaried employment share",
                value="demo value",
                source="ILO modelled estimate placeholder",
                year=2024,
                country_code="GH",
                sector_id="ict_services",
                explanation="Visible econometric signal for the frontend.",
            ),
        ],
        automation_risk=AutomationRiskNode(
            risk_id="risk_isco_7422",
            occupation_id="isco_7422",
            score=0.42,
            level="medium",
            source="Frey-Osborne / O*NET-derived placeholder",
            calibration_note="Demo value. Calibrate by country context before production use.",
        ),
    )

    return merge_graphs(worker_graph, job_graph)


if __name__ == "__main__":
    graph = build_demo_graph()
    for result in match_worker_to_jobs("amara", graph):
        print(result.model_dump_json(indent=2))
