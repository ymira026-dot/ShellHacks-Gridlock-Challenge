from dataclasses import asdict
from datetime import date

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from app.ingestion.demo_data import load_demo_projects
from app.models import Project, ProjectType
from app.services.analyzer import Opportunity, find_opportunities


app = FastAPI(title="GridSync API", version="0.1.0")
PROJECTS = load_demo_projects()


class AnalysisRequest(BaseModel):
    radius_miles: float = Field(default=25, gt=0)
    minimum_overlap_days: int = Field(default=7, ge=0)
    nearby_start_days: int = Field(default=30, ge=0)


def serialize_opportunity(opportunity: Opportunity) -> dict:
    return asdict(opportunity)


def get_opportunities(request: AnalysisRequest | None = None) -> list[Opportunity]:
    settings = request or AnalysisRequest()
    return find_opportunities(
        PROJECTS,
        radius_miles=settings.radius_miles,
        minimum_overlap_days=settings.minimum_overlap_days,
        nearby_start_days=settings.nearby_start_days,
    )


@app.get("/api/projects", response_model=list[Project])
def list_projects(
    utility: str | None = None,
    project_type: ProjectType | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[Project]:
    projects = PROJECTS
    if utility:
        projects = [project for project in projects if project.utility == utility]
    if project_type:
        projects = [project for project in projects if project.project_type == project_type]
    if start_date:
        projects = [project for project in projects if project.end_date >= start_date]
    if end_date:
        projects = [project for project in projects if project.start_date <= end_date]
    return projects


@app.get("/api/utilities", response_model=list[str])
def list_utilities() -> list[str]:
    return sorted({project.utility for project in PROJECTS})


@app.get("/api/opportunities")
def list_opportunities(
    priority: str | None = Query(default=None, pattern="^(HIGH|MEDIUM|LOW)$"),
    radius_miles: float = Query(default=25, gt=0),
    minimum_overlap_days: int = Query(default=7, ge=0),
) -> list[dict]:
    opportunities = get_opportunities(
        AnalysisRequest(
            radius_miles=radius_miles,
            minimum_overlap_days=minimum_overlap_days,
        )
    )
    if priority:
        opportunities = [opportunity for opportunity in opportunities if opportunity.priority == priority]
    return [serialize_opportunity(opportunity) for opportunity in opportunities]


@app.get("/api/opportunities/{opportunity_id}")
def get_opportunity(opportunity_id: str) -> dict:
    opportunity = next(
        (
            opportunity
            for opportunity in get_opportunities()
            if f"{opportunity.project_a_id}-{opportunity.project_b_id}" == opportunity_id
        ),
        None,
    )
    if opportunity is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return serialize_opportunity(opportunity)


@app.post("/api/analyze")
def analyze_projects(request: AnalysisRequest) -> dict:
    opportunities = get_opportunities(request)
    return {
        "projects_analyzed": len(PROJECTS),
        "utilities_compared": len({project.utility for project in PROJECTS}),
        "opportunities_found": len(opportunities),
        "high_priority_opportunities": sum(
            opportunity.priority == "HIGH" for opportunity in opportunities
        ),
        "opportunities": [serialize_opportunity(opportunity) for opportunity in opportunities],
    }