# File: app/tests/test_history_sorting.py
from fastapi.testclient import TestClient
from datetime import datetime
from app.main import app

client = TestClient(app)


def test_history_sort_by_date_desc():
    """Test history sorting by date descending (default)"""
    response = client.get("/api/v1/history?sort_by=created_at&sort_order=desc")
    assert response.status_code == 200

    data = response.json()

    if len(data["items"]) > 1:
        # Verify items are sorted by date descending
        for i in range(len(data["items"]) - 1):
            current_date = datetime.fromisoformat(
                data["items"][i]["created_at"].replace("Z", "+00:00")
            )
            next_date = datetime.fromisoformat(
                data["items"][i + 1]["created_at"].replace("Z", "+00:00")
            )
            assert current_date >= next_date

    print("✅ History date sorting (desc) works")


def test_history_sort_by_date_asc():
    """Test history sorting by date ascending"""
    response = client.get("/api/v1/history?sort_by=created_at&sort_order=asc")
    assert response.status_code == 200

    data = response.json()

    if len(data["items"]) > 1:
        # Verify items are sorted by date ascending
        for i in range(len(data["items"]) - 1):
            current_date = datetime.fromisoformat(
                data["items"][i]["created_at"].replace("Z", "+00:00")
            )
            next_date = datetime.fromisoformat(
                data["items"][i + 1]["created_at"].replace("Z", "+00:00")
            )
            assert current_date <= next_date

    print("✅ History date sorting (asc) works")


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
