"""
Tests for health check endpoints.

This module tests:
- Health endpoint accessibility
- Health response structure
- Database health checks
- Nominatim API health checks
- Individual service health endpoints
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint_exists():
    """Test that health endpoint is accessible."""
    response = client.get("/api/v1/health")
    assert response.status_code in [200, 503]  # Can be 503 if services are unhealthy
    print("✅ Health endpoint accessible")


def test_health_endpoint_response_structure():
    """Test health endpoint returns proper structure."""
    response = client.get("/api/v1/health")
    data = response.json()

    required_fields = ["status", "timestamp", "checks"]
    for field in required_fields:
        assert field in data

    assert data["status"] in ["healthy", "degraded", "unhealthy"]
    assert "database" in data["checks"]
    assert "nominatim_api" in data["checks"]
    print("✅ Health endpoint structure validated")


def test_database_health_check():
    """Test database connectivity in health check."""
    response = client.get("/api/v1/health")
    data = response.json()

    db_check = data["checks"]["database"]
    assert "status" in db_check
    assert "response_time_ms" in db_check
    assert "message" in db_check
    assert db_check["status"] in ["healthy", "unhealthy"]
    print("✅ Database health check working")


def test_nominatim_health_check():
    """Test Nominatim API connectivity in health check."""
    response = client.get("/api/v1/health")
    data = response.json()

    api_check = data["checks"]["nominatim_api"]
    assert "status" in api_check
    assert "response_time_ms" in api_check
    assert "message" in api_check
    assert api_check["status"] in ["healthy", "degraded", "unhealthy"]
    print("✅ Nominatim API health check working")


def test_individual_database_health_endpoint():
    """Test database-specific health check endpoint."""
    response = client.get("/api/v1/health/database")
    assert response.status_code == 200

    data = response.json()
    required_fields = ["status", "message", "timestamp"]
    for field in required_fields:
        assert field in data

    assert data["status"] in ["healthy", "unhealthy"]
    print("✅ Individual database health endpoint working")


def test_individual_nominatim_health_endpoint():
    """Test Nominatim-specific health check endpoint."""
    response = client.get("/api/v1/health/nominatim")
    assert response.status_code == 200

    data = response.json()
    required_fields = ["status", "response_time_ms", "message", "timestamp"]
    for field in required_fields:
        assert field in data

    assert data["status"] in ["healthy", "degraded", "unhealthy"]
    assert isinstance(data["response_time_ms"], (int, float))
    print("✅ Individual Nominatim health endpoint working")


def test_health_endpoint_http_status_codes():
    """Test that health endpoint returns appropriate HTTP status codes."""
    response = client.get("/api/v1/health")

    # Should be 200 for healthy/degraded, 503 for unhealthy
    assert response.status_code in [200, 503]

    data = response.json()
    if data["status"] == "unhealthy":
        assert response.status_code == 503
    else:
        assert response.status_code == 200
    print("✅ Health endpoint HTTP status codes correct")


def test_health_response_timestamps():
    """Test that health responses include valid timestamps."""
    response = client.get("/api/v1/health")
    data = response.json()

    # Check main timestamp
    assert "timestamp" in data
    timestamp = data["timestamp"]
    assert isinstance(timestamp, str)
    # Basic ISO format check
    assert "T" in timestamp

    # Check individual service timestamps
    db_response = client.get("/api/v1/health/database")
    db_data = db_response.json()
    assert "timestamp" in db_data

    nominatim_response = client.get("/api/v1/health/nominatim")
    nominatim_data = nominatim_response.json()
    assert "timestamp" in nominatim_data

    print("✅ Health response timestamps working")


def test_health_check_response_times():
    """Test that health checks include response time information."""
    response = client.get("/api/v1/health")
    data = response.json()

    # Nominatim check should have response time
    nominatim_check = data["checks"]["nominatim_api"]
    assert "response_time_ms" in nominatim_check
    assert isinstance(nominatim_check["response_time_ms"], (int, float))
    assert nominatim_check["response_time_ms"] >= 0

    print("✅ Health check response times working")
