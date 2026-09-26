from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_projects_and_utilities_endpoints_expose_demo_data():
    projects_response = client.get("/api/projects")
    utilities_response = client.get("/api/utilities")

    assert projects_response.status_code == 200
    assert len(projects_response.json()) == 4
    assert utilities_response.json() == ["Demo Utility North", "Demo Utility South"]


def test_analyze_endpoint_returns_summary_and_opportunities():
    response = client.post(
        "/api/analyze",
        json={"radius_miles": 10, "minimum_overlap_days": 14},
    )

    assert response.status_code == 200
    assert response.json()["projects_analyzed"] == 4
    assert response.json()["high_priority_opportunities"] >= 1