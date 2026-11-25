import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_ai_detection_endpoint():
    response = client.post(
        "/api/v1/detect",
        data={"image_url": "/static/samples/pothole_sample.jpg"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "detections" in data
    assert "inference_ms" in data
    assert "model_version" in data
    assert len(data["detections"]) > 0
    top = data["detections"][0]
    assert "bbox" in top
    assert len(top["bbox"]) == 4
    assert 0.0 <= top["confidence"] <= 1.0

def test_ai_detection_missing_image():
    response = client.post(
        "/api/v1/detect",
        data={"image_url": "/static/samples/non_existent_image.jpg"}
    )
    assert response.status_code == 404
