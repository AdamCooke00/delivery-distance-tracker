# File: app/tests/test_history_filtering.py
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from urllib.parse import quote
from app.main import app

client = TestClient(app)


def test_history_date_filtering():
    """Test history filtering by date range"""
    # Get yesterday's date
    yesterday = (datetime.now() - timedelta(days=1)).isoformat()

    response = client.get(f"/api/v1/history?start_date={quote(yesterday)}")
    assert response.status_code == 200

    data = response.json()

    # Verify all returned items are after the start date
    for item in data["items"]:
        item_date = datetime.fromisoformat(item["created_at"].replace("Z", "+00:00"))
        filter_date = datetime.fromisoformat(yesterday)
        assert item_date >= filter_date

    print("✅ History date filtering works")


def test_history_search_filtering():
    """Test history filtering by address search"""
    search_term = "Test"

    response = client.get(f"/api/v1/history?search={search_term}")
    assert response.status_code == 200

    data = response.json()

    # Verify all returned items contain the search term
    for item in data["items"]:
        addresses = item["source_address"] + " " + item["destination_address"]
        assert search_term.lower() in addresses.lower()

    print("✅ History search filtering works")


def test_history_combined_filters():
    """Test history with multiple filters combined"""
    yesterday = (datetime.now() - timedelta(days=1)).isoformat()
    search_term = "Test"

    response = client.get(
        f"/api/v1/history?search={search_term}&start_date={quote(yesterday)}&limit=5"
    )
    assert response.status_code == 200

    data = response.json()
    assert data["limit"] == 5

    # Should respect all filters
    for item in data["items"]:
        addresses = item["source_address"] + " " + item["destination_address"]
        assert search_term.lower() in addresses.lower()

        item_date = datetime.fromisoformat(item["created_at"].replace("Z", "+00:00"))
        filter_date = datetime.fromisoformat(yesterday)
        assert item_date >= filter_date

    print("✅ Combined history filters work")
