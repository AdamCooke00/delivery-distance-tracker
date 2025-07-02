# File: app/tests/test_history_filtering.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


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


def test_history_basic_filters():
    """Test history with basic filters"""
    response = client.get("/api/v1/history?limit=5")
    assert response.status_code == 200

    data = response.json()
    assert data["limit"] == 5
    assert len(data["items"]) <= 5

    print("✅ Basic history filters work")
