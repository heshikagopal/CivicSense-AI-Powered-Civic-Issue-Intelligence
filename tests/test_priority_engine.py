import pytest
from backend.app.utils.geo import haversine_distance_meters, compute_spatial_similarity
from backend.app.services.embedding_service import embedding_service
from backend.app.services.priority_service import priority_service

def test_haversine_distance():
    # MG Road to Indiranagar (approx 3.5 - 4.0 km)
    d = haversine_distance_meters(12.9716, 77.5946, 12.9784, 77.6408)
    assert 3500 <= d <= 6000

def test_spatial_similarity():
    sim_exact = compute_spatial_similarity(0.0)
    assert sim_exact == 1.0
    sim_50m = compute_spatial_similarity(50.0, 200.0)
    assert 0.70 <= sim_50m <= 0.80
    sim_far = compute_spatial_similarity(250.0, 200.0)
    assert sim_far == 0.0

def test_cosine_similarity():
    v1 = [1.0, 0.0, 0.0]
    v2 = [1.0, 0.0, 0.0]
    v3 = [0.0, 1.0, 0.0]
    assert embedding_service.cosine_similarity(v1, v2) == 1.0
    assert embedding_service.cosine_similarity(v1, v3) == 0.0

def test_priority_engine_factors():
    prio = priority_service.compute_priority(
        base_risk_score=75.0,
        ward_density_level="HIGH",
        report_count=3,
        detection_bboxes=[[0.2, 0.2, 0.6, 0.6]]
    )
    assert 0 <= prio["overall_score"] <= 100
    assert prio["priority_band"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    factors = prio["factors"]
    assert "base_risk" in factors
    assert "damage_extent" in factors
    assert "location_context" in factors
    assert "supporting_reports" in factors
    assert "evidence_quality" in factors
