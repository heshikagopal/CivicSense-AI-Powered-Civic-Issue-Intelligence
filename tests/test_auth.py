import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_login_admin():
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "admin@civicsense.org", "password": "Admin123!"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["role"] == "admin"

def test_login_invalid_password():
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "admin@civicsense.org", "password": "WrongPassword"}
    )
    assert response.status_code == 401

def test_register_new_citizen():
    import uuid
    random_email = f"citizen_{uuid.uuid4().hex[:6]}@civicsense.org"
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": random_email,
            "password": "Password123!",
            "full_name": "Test Citizen User",
            "role": "citizen"
        }
    )
    assert response.status_code == 201
    assert response.json()["email"] == random_email
