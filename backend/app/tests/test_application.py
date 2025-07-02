"""
Tests for FastAPI application startup and configuration.

This module tests:
- FastAPI application startup
- OpenAPI documentation accessibility
- Root endpoint functionality
- Application configuration
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_app_startup():
    """Test that FastAPI application starts correctly."""
    response = client.get("/docs")
    assert response.status_code == 200
    print("✅ FastAPI application starts successfully")


def test_openapi_documentation():
    """Test that OpenAPI documentation is accessible."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    openapi_schema = response.json()
    assert openapi_schema["info"]["title"] == "Delivery Distance Tracker API"
    assert openapi_schema["info"]["version"] == "1.0.0"
    print("✅ OpenAPI documentation accessible")


def test_root_endpoint():
    """Test that root endpoint returns proper information."""
    response = client.get("/")
    assert response.status_code == 200

    data = response.json()
    assert "message" in data
    assert data["message"] == "Delivery Distance Tracker API"
    assert "version" in data
    assert data["version"] == "1.0.0"
    assert "docs" in data
    assert data["docs"] == "/docs"
    assert "health" in data
    assert data["health"] == "/api/v1/health"
    print("✅ Root endpoint returns correct information")


def test_redoc_documentation():
    """Test that ReDoc documentation is accessible."""
    response = client.get("/redoc")
    assert response.status_code == 200
    print("✅ ReDoc documentation accessible")


def test_application_metadata():
    """Test that application metadata is properly configured."""
    response = client.get("/openapi.json")
    assert response.status_code == 200

    openapi_schema = response.json()
    info = openapi_schema["info"]

    assert info["title"] == "Delivery Distance Tracker API"
    assert (
        info["description"]
        == "A REST API for calculating distances between delivery addresses"
    )
    assert info["version"] == "1.0.0"
    print("✅ Application metadata configured correctly")


def test_cors_headers():
    """Test that CORS headers are properly configured."""
    response = client.options(
        "/",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )

    # Check that CORS headers are present
    assert "access-control-allow-origin" in response.headers
    print("✅ CORS headers configured correctly")
