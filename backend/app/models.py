from datetime import date
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator


class ProjectType(StrEnum):
    TRANSMISSION = "transmission"
    SUBSTATION = "substation"
    DISTRIBUTION = "distribution"
    UNDERGROUND_UTILITIES = "underground utilities"
    VEGETATION_CLEARING = "vegetation clearing"
    ROAD_EXCAVATION = "road/excavation"
    FIBER_COMMUNICATIONS = "fiber/communications"
    EQUIPMENT_REPLACEMENT = "equipment replacement"
    OTHER = "other"


class Project(BaseModel):
    """Common representation used for every utility construction project."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    utility: str = Field(min_length=1)
    project_name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    project_type: ProjectType
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    location: str = Field(min_length=1)
    state: str = Field(min_length=2, max_length=2)
    start_date: date
    end_date: date
    status: str = Field(min_length=1)
    source_url: HttpUrl

    @model_validator(mode="after")
    def validate_date_range(self) -> "Project":
        if self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        return self
