# File: app/tests/test_history_endpoint.py
from fastapi.testclient import TestClient
from app.main import app
from app.models.distance_query import DistanceQuery
from app.models.database import SessionLocal

client = TestClient(app)


def setup_test_data():
    """Create test data for history endpoint testing"""
    db = SessionLocal()

    # Clear existing test data
    db.query(DistanceQuery).filter(DistanceQuery.source_address.like("Test%")).delete()

    # Create test queries
    test_queries = [
        {
            "source_address": "Test Address 1",
            "destination_address": "Test Destination 1",
            "source_lat": 40.7128,
            "source_lng": -74.0060,
            "destination_lat": 34.0522,
            "destination_lng": -118.2437,
            "distance_km": 3944.0,
        },
        {
            "source_address": "Test Address 2",
            "destination_address": "Test Destination 2",
            "source_lat": 51.5074,
            "source_lng": -0.1278,
            "destination_lat": 48.8566,
            "destination_lng": 2.3522,
            "distance_km": 344.0,
        },
        {
            "source_address": "Test Address 3",
            "destination_address": "Test Destination 3",
            "source_lat": 35.6762,
            "source_lng": 139.6503,
            "destination_lat": 37.7749,
            "destination_lng": -122.4194,
            "distance_km": 8280.0,
        },
    ]

    for query_data in test_queries:
        query = DistanceQuery(**query_data)
        db.add(query)

    db.commit()
    db.close()


def test_get_history_basic():
    """Test basic history retrieval without parameters"""
    setup_test_data()

    response = client.get("/api/v1/history")
    assert response.status_code == 200

    data = response.json()

    # Verify response structure
    required_fields = ["items", "total", "limit", "offset", "has_more"]
    for field in required_fields:
        assert field in data

    # Verify items structure
    assert len(data["items"]) > 0
    item = data["items"][0]
    item_fields = [
        "id",
        "source_address",
        "destination_address",
        "distance_km",
    ]
    for field in item_fields:
        assert field in item

    print("✅ Basic history retrieval works")


def test_get_history_with_limit():
    """Test history retrieval with limit parameter"""
    setup_test_data()

    response = client.get("/api/v1/history?limit=2")
    assert response.status_code == 200

    data = response.json()
    assert len(data["items"]) <= 2
    assert data["limit"] == 2

    print("✅ History limit parameter works")


def test_get_history_with_pagination():
    """Test history retrieval with pagination"""
    setup_test_data()

    # Get first page
    response1 = client.get("/api/v1/history?limit=1&offset=0")
    assert response1.status_code == 200
    data1 = response1.json()

    # Get second page
    response2 = client.get("/api/v1/history?limit=1&offset=1")
    assert response2.status_code == 200
    data2 = response2.json()

    # Items should be different
    if len(data1["items"]) > 0 and len(data2["items"]) > 0:
        assert data1["items"][0]["id"] != data2["items"][0]["id"]

    print("✅ History pagination works")
