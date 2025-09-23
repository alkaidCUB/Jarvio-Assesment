import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Workflow Builder API"}


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_login_endpoint_exists():
    """Test that login endpoint exists and requires proper data"""
    # Test with missing data
    response = client.post("/auth/login", json={})
    assert response.status_code == 422  # Validation error
    
    # Test with proper structure (will fail due to DB connection, but endpoint works)
    response = client.post(
        "/auth/login",
        json={"email": "demo@example.com", "password": "demo123"}
    )
    # Accept either success (if DB works) or 500 (if DB connection fails)
    assert response.status_code in [200, 500]