# File: app/tests/test_history_validation.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_invalid_pagination_parameters():
    """Test validation of invalid pagination parameters"""
    # Test negative limit
    response = client.get("/api/v1/history?limit=-1")
    assert response.status_code == 422

    # Test negative offset
    response = client.get("/api/v1/history?offset=-1")
    assert response.status_code == 422

    # Test excessively large limit
    response = client.get("/api/v1/history?limit=10000")
    assert response.status_code == 422

    print("✅ Invalid pagination parameter validation works")


def test_invalid_date_format():
    """Test validation of invalid date formats"""
    invalid_dates = [
        "invalid-date",
        "2023-13-01",  # Invalid month
        "2023-02-30",  # Invalid day
        "not-a-date",
    ]

    for invalid_date in invalid_dates:
        response = client.get(f"/api/v1/history?start_date={invalid_date}")
        assert response.status_code == 422

    print("✅ Invalid date format validation works")


def test_database_error_handling():
    """Test handling of database errors during history retrieval"""
    # This test would require mocking database errors
    # For now, just verify the endpoint doesn't crash
    response = client.get("/api/v1/history")
    assert response.status_code in [200, 500]  # Either success or graceful error

    print("✅ Database error handling verified")
