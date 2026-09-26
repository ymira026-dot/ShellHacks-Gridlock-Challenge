from app.models import ProjectType


COMPATIBLE_PROJECT_TYPES = {
    frozenset({ProjectType.SUBSTATION, ProjectType.EQUIPMENT_REPLACEMENT}),
    frozenset({ProjectType.SUBSTATION, ProjectType.DISTRIBUTION}),
    frozenset({ProjectType.TRANSMISSION, ProjectType.VEGETATION_CLEARING}),
    frozenset({ProjectType.TRANSMISSION, ProjectType.ROAD_EXCAVATION}),
    frozenset({ProjectType.DISTRIBUTION, ProjectType.VEGETATION_CLEARING}),
    frozenset({ProjectType.DISTRIBUTION, ProjectType.ROAD_EXCAVATION}),
    frozenset({ProjectType.FIBER_COMMUNICATIONS, ProjectType.ROAD_EXCAVATION}),
    frozenset({ProjectType.UNDERGROUND_UTILITIES, ProjectType.ROAD_EXCAVATION}),
}


def are_compatible(project_type_a: ProjectType, project_type_b: ProjectType) -> bool:
    return project_type_a == project_type_b or frozenset(
        {project_type_a, project_type_b}
    ) in COMPATIBLE_PROJECT_TYPES


def classify_priority(
    distance_miles: float,
    overlap_days: int,
    compatible: bool,
) -> tuple[str, list[str]]:
    """Apply transparent proximity, schedule, and compatibility rules."""
    reasons = []
    if distance_miles <= 10:
        reasons.append(f"sites are {distance_miles:.1f} miles apart")
    elif distance_miles <= 25:
        reasons.append(f"sites are {distance_miles:.1f} miles apart")

    if overlap_days > 0:
        reasons.append(f"schedules overlap for {overlap_days} days")
    else:
        reasons.append("project start dates are nearby")

    if compatible:
        reasons.append("project types may share construction resources")
    else:
        reasons.append("project types have limited direct compatibility")

    if distance_miles <= 10 and overlap_days >= 30 and compatible:
        return "HIGH", reasons
    if distance_miles <= 25 and (overlap_days >= 7 or compatible):
        return "MEDIUM", reasons
    return "LOW", reasons