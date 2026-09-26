from dataclasses import dataclass

from app.models import Project
from app.services.classifier import are_compatible, classify_priority
from app.services.distance import haversine_distance_miles
from app.services.scheduling import overlapping_days, starts_within_days


@dataclass(frozen=True)
class Opportunity:
    project_a_id: str
    project_b_id: str
    utility_a: str
    utility_b: str
    distance_miles: float
    overlap_days: int
    nearby_start: bool
    compatible: bool
    priority: str
    reasons: list[str]


def find_opportunities(
    projects: list[Project],
    radius_miles: float = 25,
    minimum_overlap_days: int = 7,
    nearby_start_days: int = 30,
) -> list[Opportunity]:
    """Compare each cross-utility project pair using configurable thresholds."""
    opportunities = []
    for index, project_a in enumerate(projects):
        for project_b in projects[index + 1 :]:
            if project_a.utility == project_b.utility:
                continue

            distance_miles = haversine_distance_miles(
                project_a.latitude,
                project_a.longitude,
                project_b.latitude,
                project_b.longitude,
            )
            if distance_miles > radius_miles:
                continue

            overlap_days = overlapping_days(
                project_a.start_date,
                project_a.end_date,
                project_b.start_date,
                project_b.end_date,
            )
            nearby_start = starts_within_days(
                project_a.start_date,
                project_b.start_date,
                nearby_start_days,
            )
            if overlap_days < minimum_overlap_days and not nearby_start:
                continue

            compatible = are_compatible(project_a.project_type, project_b.project_type)
            priority, reasons = classify_priority(distance_miles, overlap_days, compatible)
            opportunities.append(
                Opportunity(
                    project_a_id=project_a.id,
                    project_b_id=project_b.id,
                    utility_a=project_a.utility,
                    utility_b=project_b.utility,
                    distance_miles=round(distance_miles, 2),
                    overlap_days=overlap_days,
                    nearby_start=nearby_start,
                    compatible=compatible,
                    priority=priority,
                    reasons=reasons,
                )
            )
    return opportunities