import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_get_categories():
    response = client.get("/api/v1/categories")
    assert response.status_code == 200
    cats = response.json()
    assert len(cats) >= 5
    codes = [c["code"] for c in cats]
    assert "pothole" in codes
    assert "road_crack" in codes

def test_get_departments():
    response = client.get("/api/v1/departments")
    assert response.status_code == 200
    depts = response.json()
    assert len(depts) >= 4

def test_submit_citizen_report():
    report_payload = {
        "latitude": 12.9716,
        "longitude": 77.5946,
        "address_text": "Mahatma Gandhi Road, Near Metro Station",
        "image_url": "/static/samples/pothole_sample.jpg",
        "citizen_category_suggestion": "Pothole",
        "citizen_comment": "Dangerous road depression causing traffic slowdown.",
        "consent_given": True,
        "confirmed_category_code": "pothole"
    }
    response = client.post("/api/v1/reports", json=report_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["report_code"].startswith("REP-2026-")
    assert data["status"] == "LINKED_TO_ISSUE"
    assert data["issue_id"] is not None
