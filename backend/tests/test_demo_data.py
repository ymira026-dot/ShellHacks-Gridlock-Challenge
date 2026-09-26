from app.ingestion.demo_data import load_demo_projects


def test_demo_data_loads_through_normalized_schema():
    projects = load_demo_projects()

    assert len(projects) == 4
    assert {project.utility for project in projects} == {
        "Demo Utility North",
        "Demo Utility South",
    }
    assert all(project.source_url for project in projects)