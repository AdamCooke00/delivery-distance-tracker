# File: app/tests/test_history_sorting.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_history_sort_by_id_desc():
    """Test history sorting by ID descending (default)"""
    response = client.get("/api/v1/history?sort_by=id&sort_order=desc")
    assert response.status_code == 200

    data = response.json()

    if len(data["items"]) > 1:
        # Verify items are sorted by ID descending
        for i in range(len(data["items"]) - 1):
            current_id = data["items"][i]["id"]
            next_id = data["items"][i + 1]["id"]
            assert current_id >= next_id

    print("✅ History ID sorting (desc) works")


def test_history_sort_by_id_asc():
    """Test history sorting by ID ascending"""
    response = client.get("/api/v1/history?sort_by=id&sort_order=asc")
    assert response.status_code == 200

    data = response.json()

    if len(data["items"]) > 1:
        # Verify items are sorted by ID ascending
        for i in range(len(data["items"]) - 1):
            current_id = data["items"][i]["id"]
            next_id = data["items"][i + 1]["id"]
            assert current_id <= next_id

    print("✅ History ID sorting (asc) works")


def test_history_sort_by_distance():
    """Test history sorting by distance"""
    response = client.get("/api/v1/history?sort_by=distance_km&sort_order=desc")
    assert response.status_code == 200

    data = response.json()

    if len(data["items"]) > 1:
        # Verify items are sorted by distance descending
        for i in range(len(data["items"]) - 1):
            current_distance = data["items"][i]["distance_km"]
            next_distance = data["items"][i + 1]["distance_km"]
            assert current_distance >= next_distance

    print("✅ History distance sorting works")


def test_invalid_sort_parameters():
    """Test handling of invalid sort parameters"""
    response = client.get("/api/v1/history?sort_by=invalid_field")
    assert response.status_code == 422

    response = client.get("/api/v1/history?sort_order=invalid_order")
    assert response.status_code == 422

    print("✅ Invalid sort parameter validation works")
