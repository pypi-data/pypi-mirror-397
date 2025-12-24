"""Tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient

from nostromo_api.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_health_check(client: TestClient):
    """Test health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "OPERATIONAL"
    assert "MU-TH-UR" in data["system"]


def test_root_endpoint(client: TestClient):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ONLINE"
    assert "docs" in data


def test_chat_requires_auth(client: TestClient):
    """Test that chat endpoint requires authentication."""
    response = client.post(
        "/api/chat",
        json={"message": "Hello"},
    )
    assert response.status_code == 401


def test_docs_available(client: TestClient):
    """Test that OpenAPI docs are available."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_get_token(client: TestClient):
    """Test token generation."""
    response = client.post(
        "/api/auth/token",
        data={"username": "test", "password": "test"},
    )
    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
