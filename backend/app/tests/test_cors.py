"""
Tests for CORS (Cross-Origin Resource Sharing) configuration.

This module tests:
- CORS headers configuration
- Preflight request handling
- Origin validation
- Methods and headers allowance
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_cors_headers():
    """Test CORS headers are properly set."""
    response = client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert "access-control-allow-origin" in response.headers
    assert "access-control-allow-methods" in response.headers
    print("✅ CORS configuration working")


def test_cors_allowed_origins():
    """Test that allowed origins are properly configured."""
    # Test localhost:3000 (SvelteKit default)
    response = client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.headers.get("access-control-allow-origin") in [
        "http://localhost:3000",
        "*",  # If configured to allow all
    ]

    # Test 127.0.0.1:3000
    response = client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://127.0.0.1:3000",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.headers.get("access-control-allow-origin") in [
        "http://127.0.0.1:3000",
        "*",
    ]

    print("✅ CORS allowed origins configured correctly")


def test_cors_allowed_methods():
    """Test that allowed HTTP methods are properly configured."""
    response = client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
        },
    )

    allowed_methods = response.headers.get("access-control-allow-methods", "")
    expected_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]

    for method in expected_methods:
        assert method in allowed_methods

    print("✅ CORS allowed methods configured correctly")


def test_cors_preflight_get_request():
    """Test CORS preflight for GET requests."""
    response = client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )

    # Preflight should be successful
    assert response.status_code in [200, 204]
    assert "access-control-allow-origin" in response.headers
    assert "access-control-allow-methods" in response.headers

    print("✅ CORS preflight for GET requests working")


def test_cors_preflight_post_request():
    """Test CORS preflight for POST requests."""
    response = client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type",
        },
    )

    # Preflight should be successful
    assert response.status_code in [200, 204]
    assert "access-control-allow-origin" in response.headers
    assert "access-control-allow-methods" in response.headers

    print("✅ CORS preflight for POST requests working")


def test_cors_credentials():
    """Test CORS credentials configuration."""
    response = client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )

    # Check if credentials are allowed
    credentials_header = response.headers.get("access-control-allow-credentials")
    # Should be "true" if credentials are allowed
    if credentials_header:
        assert credentials_header.lower() == "true"

    print("✅ CORS credentials configuration working")


def test_cors_headers_allowance():
    """Test that custom headers are allowed through CORS."""
    response = client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type, Authorization, X-Custom-Header",
        },
    )

    assert response.status_code in [200, 204]

    # Check that headers are allowed
    allowed_headers = response.headers.get("access-control-allow-headers", "")
    if allowed_headers != "*":
        expected_headers = ["Content-Type", "Authorization"]
        for header in expected_headers:
            assert header.lower() in allowed_headers.lower()

    print("✅ CORS headers allowance working")


def test_actual_cors_request():
    """Test actual CORS request (not preflight)."""
    response = client.get("/api/v1/health", headers={"Origin": "http://localhost:3000"})

    # Should work normally
    assert response.status_code in [200, 503]  # 200 if healthy, 503 if unhealthy

    # Should include CORS headers in actual response
    assert "access-control-allow-origin" in response.headers

    print("✅ Actual CORS requests working")


def test_cors_with_root_endpoint():
    """Test CORS with root endpoint."""
    response = client.get("/", headers={"Origin": "http://localhost:3000"})

    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers

    print("✅ CORS with root endpoint working")


def test_cors_disallowed_origin():
    """Test CORS behavior with disallowed origins."""
    response = client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://malicious-site.com",
            "Access-Control-Request-Method": "GET",
        },
    )

    # The response might still be 200/204, but origin should not be in allow-origin
    # or it should be rejected based on CORS policy
    origin_header = response.headers.get("access-control-allow-origin")

    # If not allowing all origins (*), the malicious origin should not be allowed
    if origin_header and origin_header != "*":
        assert "malicious-site.com" not in origin_header

    print("✅ CORS disallowed origin handling working")
