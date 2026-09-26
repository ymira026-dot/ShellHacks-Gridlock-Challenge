from datetime import date

from app.ingestion.demo_data import load_demo_projects
from app.services.analyzer import find_opportunities
from app.services.distance import haversine_distance_miles
from app.services.scheduling import overlapping_days, starts_within_days


def test_haversine_distance_is_reasonable_for_one_degree_of_longitude():
    distance = haversine_distance_miles(0, 0, 0, 1)

    assert 68 < distance < 70


def test_schedule_calculations_are_inclusive_and_detect_nearby_starts():
    assert overlapping_days(
        date(2027, 1, 1), date(2027, 1, 10), date(2027, 1, 10), date(2027, 1, 20)
    ) == 1
    assert starts_within_days(date(2027, 1, 1), date(2027, 1, 20), 19)


def test_analyzer_compares_only_cross_utility_projects():
    opportunities = find_opportunities(load_demo_projects())

    assert opportunities
    assert all(opportunity.utility_a != opportunity.utility_b for opportunity in opportunities)
    assert any(opportunity.priority == "HIGH" for opportunity in opportunities)