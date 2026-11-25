import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_full_civic_lifecycle_integration():
    """
    Complete end-to-end integration test:
    1. Authenticate Admin and Officer
    2. Upload image & run AI detection
    3. Citizen submits report
    4. Duplicate analysis & Priority estimation verified
    5. Admin views issue details and assigns department/officer
    6. Officer submits resolution with proof
    7. Admin verifies resolution
    """
    # 1. Login as Admin
    admin_login = client.post(
        "/api/v1/auth/login",
        data={"username": "admin@civicsense.org", "password": "Admin123!"}
    )
    assert admin_login.status_code == 200
    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Login as Officer
    officer_login = client.post(
        "/api/v1/auth/login",
        data={"username": "officer@civicsense.org", "password": "Officer123!"}
    )
    assert officer_login.status_code == 200
    officer_token = officer_login.json()["access_token"]
    officer_headers = {"Authorization": f"Bearer {officer_token}"}

    # 2. AI Detection Check
    det_resp = client.post(
        "/api/v1/detect",
        data={"image_url": "/static/samples/road_crack_sample.jpg"}
    )
    assert det_resp.status_code == 200
    det_data = det_resp.json()
    assert len(det_data["detections"]) > 0

    # 3. Citizen Submits Report
    report_resp = client.post(
        "/api/v1/reports",
        json={
            "latitude": 12.9810,
            "longitude": 77.6010,
            "address_text": "Commercial Street Corner Link",
            "image_url": "/static/samples/road_crack_sample.jpg",
            "citizen_category_suggestion": "Road Crack",
            "citizen_comment": "Widening crack along pedestrian crosswalk.",
            "consent_given": True,
            "confirmed_category_code": "road_crack"
        }
    )
    assert report_resp.status_code == 201
    rep = report_resp.json()
    issue_id = rep["issue_id"]
    assert issue_id is not None

    # 4. Priority Breakdown Check
    prio_resp = client.get(f"/api/v1/issues/{issue_id}/priority")
    assert prio_resp.status_code == 200
    prio_data = prio_resp.json()
    assert prio_data["overall_score"] > 0
    assert "factors" in prio_data

    # 5. Department Assignment (Officer/Admin assigns department)
    depts_resp = client.get("/api/v1/departments")
    dept_id = depts_resp.json()[0]["id"]
    assign_resp = client.post(
        f"/api/v1/issues/{issue_id}/assign",
        json={
            "department_id": dept_id,
            "notes": "Emergency road patching crew assigned."
        },
        headers=officer_headers
    )
    assert assign_resp.status_code == 200
    assert assign_resp.json()["status"] == "IN_PROGRESS"

    # 6. Officer Submits Resolution
    res_resp = client.post(
        f"/api/v1/issues/{issue_id}/resolution",
        json={
            "resolution_notes": "Surface resealed with hot-pour bituminous mastic. Quality inspected.",
            "proof_image_url": "/static/samples/road_crack_sample.jpg"
        },
        headers=officer_headers
    )
    assert res_resp.status_code == 200
    resolution = res_resp.json()
    res_id = resolution["id"]
    assert resolution["is_verified"] is False

    # 7. Admin Verifies Resolution
    verify_resp = client.post(
        f"/api/v1/resolution/{res_id}/verify",
        json={
            "is_verified": True,
            "verification_notes": "Supervisor verified smooth surface and compliance with civic standards."
        },
        headers=admin_headers
    )
    assert verify_resp.status_code == 200
    assert verify_resp.json()["is_verified"] is True

    # 8. Verify issue details reflect verified completion
    issue_detail = client.get(f"/api/v1/issues/{issue_id}")
    assert issue_detail.status_code == 200
    detail = issue_detail.json()
    assert detail["status"] == "RESOLVED"
    assert detail["verified_at"] is not None
