# File: app/tests/test_history_performance.py
import time
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_history_response_time():
    """Test that history endpoint responds within acceptable time"""
    start_time = time.time()

    response = client.get("/api/v1/history?limit=50")

    end_time = time.time()
    response_time = end_time - start_time

    assert response.status_code == 200
    assert response_time < 2.0  # Should respond within 2 seconds

    print(f"✅ History response time: {response_time:.3f}s")


def test_large_result_set_handling():
    """Test handling of requests for large result sets"""
    # Test with maximum allowed limit
    response = client.get("/api/v1/history?limit=100")
    assert response.status_code == 200

    data = response.json()
    assert "items" in data
    assert len(data["items"]) <= 100

    print("✅ Large result set handling works")


def test_pagination_metadata_accuracy():
    """Test accuracy of pagination metadata"""
    response = client.get("/api/v1/history?limit=5&offset=0")
    assert response.status_code == 200

    data = response.json()

    # Verify metadata fields exist and are logical
    assert "total" in data
    assert "has_more" in data
    assert data["total"] >= len(data["items"])

    if data["total"] > 5:
        assert data["has_more"] is True
    else:
        assert data["has_more"] is False

    print("✅ Pagination metadata accuracy verified")
