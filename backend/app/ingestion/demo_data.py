import json
from pathlib import Path

from app.models import Project


DEFAULT_DATA_PATH = Path(__file__).resolve().parents[3] / "data" / "demo_projects.json"


def load_demo_projects(data_path: Path = DEFAULT_DATA_PATH) -> list[Project]:
    """Load and validate the clearly labeled demo records."""
    with data_path.open(encoding="utf-8") as data_file:
        raw_projects = json.load(data_file)

    return [Project.model_validate(raw_project) for raw_project in raw_projects]