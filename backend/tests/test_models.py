from datetime import date

import pytest
from pydantic import ValidationError

from app.models import Project, ProjectType


VALID_PROJECT = {
    "id": "demo-001",
    "utility": "Demo Utility North",
    "project_name": "North Ridge Substation Expansion",
    "description": "Expansion of an existing substation.",
    "project_type": "substation",
    "latitude": 26.12,
    "longitude": -80.15,
    "location": "North Ridge",
    "state": "FL",
    "start_date": "2027-01-15",
    "end_date": "2027-06-30",
    "status": "planned",
    "source_url": "https://example.com/projects/demo-001",
}


def test_project_normalizes_dates_and_project_type():
    project = Project.model_validate(VALID_PROJECT)

    assert project.start_date == date(2027, 1, 15)
    assert project.end_date == date(2027, 6, 30)
    assert project.project_type is ProjectType.SUBSTATION


def test_project_rejects_invalid_date_range():
    invalid_project = {**VALID_PROJECT, "end_date": "2026-12-01"}

    with pytest.raises(ValidationError, match="end_date must be on or after start_date"):
        Project.model_validate(invalid_project)


def test_project_rejects_coordinates_outside_earth():
    invalid_project = {**VALID_PROJECT, "latitude": 91}

    with pytest.raises(ValidationError):
        Project.model_validate(invalid_project)
