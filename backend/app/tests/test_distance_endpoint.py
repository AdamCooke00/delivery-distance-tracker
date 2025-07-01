"""
Test cases for distance calculation API endpoint.

This module tests the POST /distance endpoint for successful distance calculations
including various scenarios like same location, different locations, and edge cases.
"""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from app.main import app
from app.services.geocoding import GeocodingResult

client = TestClient(app)


class TestDistanceEndpointSuccess:
    """Test successful distance calculation scenarios."""

    @patch("app.services.geocoding.GeocodingService.geocode_address")
    def test_successful_distance_calculation(self, mock_geocode):
        """Test successful distance calculation between two addresses"""
        # Mock geocoding responses for Google and Apple headquarters
        mock_geocode.side_effect = [
            GeocodingResult(
                latitude=37.4224764,
                longitude=-122.0842499,
                display_name="1600 Amphitheatre Parkway, Mountain View, CA, USA",
                place_id=123456,
                importance=0.8,
            ),
            GeocodingResult(
                latitude=37.3349,
                longitude=-122.009,
                display_name="1 Apple Park Way, Cupertino, CA, USA",
                place_id=789012,
                importance=0.8,
            ),
        ]

        request_data = {
            "source_address": "1600 Amphitheatre Parkway, Mountain View, CA",
            "destination_address": "1 Apple Park Way, Cupertino, CA",
        }

        response = client.post("/api/v1/distance", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        required_fields = [
            "id",
            "source_address",
            "destination_address",
            "source_lat",
            "source_lng",
            "destination_lat",
            "destination_lng",
            "source_coords",
            "destination_coords",
            "distance_km",
            "created_at",
        ]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

        # Verify data types and ranges
        assert isinstance(data["distance_km"], (int, float))
        assert data["distance_km"] > 0
        assert len(data["source_coords"]) == 2
        assert len(data["destination_coords"]) == 2
        assert (
            data["timestamp"] is not None
            if "timestamp" in data
            else data["created_at"] is not None
        )

        # Verify geocoding data
        assert data["source_lat"] == 37.4224764
        assert data["source_lng"] == -122.0842499
        assert data["destination_lat"] == 37.3349
        assert data["destination_lng"] == -122.009

        # Verify coordinate arrays
        assert data["source_coords"] == [37.4224764, -122.0842499]
        assert data["destination_coords"] == [37.3349, -122.009]

        # Verify addresses are stored
        assert "Mountain View" in data["source_address"]
        assert "Cupertino" in data["destination_address"]

        # Verify reasonable distance (should be around 11-12 km)
        assert 10 <= data["distance_km"] <= 15

        print("✅ Successful distance calculation works")

    @patch("app.services.geocoding.GeocodingService.geocode_address")
    def test_distance_calculation_same_location(self, mock_geocode):
        """Test distance calculation for same location returns 0"""
        # Mock same geocoding response for both addresses
        same_location = GeocodingResult(
            latitude=37.4224764,
            longitude=-122.0842499,
            display_name="1600 Amphitheatre Parkway, Mountain View, CA, USA",
            place_id=123456,
            importance=0.8,
        )
        mock_geocode.side_effect = [same_location, same_location]

        request_data = {
            "source_address": "1600 Amphitheatre Parkway, Mountain View, CA",
            "destination_address": "1600 Amphitheatre Parkway, Mountain View, CA",
        }

        response = client.post("/api/v1/distance", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["distance_km"] == 0.0

        # Verify same coordinates
        assert data["source_coords"] == data["destination_coords"]
        assert data["source_lat"] == data["destination_lat"]
        assert data["source_lng"] == data["destination_lng"]

        print("✅ Same location distance calculation works")

    @patch("app.services.geocoding.GeocodingService.geocode_address")
    def test_distance_calculation_international(self, mock_geocode):
        """Test distance calculation between international locations"""
        # Mock geocoding responses for New York and London
        mock_geocode.side_effect = [
            GeocodingResult(
                latitude=40.7128,
                longitude=-74.0060,
                display_name="New York, NY, USA",
                place_id=111111,
                importance=0.9,
            ),
            GeocodingResult(
                latitude=51.5074,
                longitude=-0.1278,
                display_name="London, UK",
                place_id=222222,
                importance=0.9,
            ),
        ]

        request_data = {
            "source_address": "New York, NY, USA",
            "destination_address": "London, UK",
        }

        response = client.post("/api/v1/distance", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # Verify large international distance (should be around 5500-5600 km)
        assert 5000 <= data["distance_km"] <= 6000

        # Verify coordinates are in expected ranges
        assert 40 <= data["source_lat"] <= 41  # New York latitude
        assert -75 <= data["source_lng"] <= -73  # New York longitude
        assert 51 <= data["destination_lat"] <= 52  # London latitude
        assert -1 <= data["destination_lng"] <= 1  # London longitude

        print("✅ International distance calculation works")

    @patch("app.services.geocoding.GeocodingService.geocode_address")
    def test_distance_calculation_precision(self, mock_geocode):
        """Test distance calculation precision with close locations"""
        # Mock geocoding responses for very close locations (same city)
        mock_geocode.side_effect = [
            GeocodingResult(
                latitude=37.7749,
                longitude=-122.4194,
                display_name="San Francisco City Hall, CA, USA",
                place_id=333333,
                importance=0.7,
            ),
            GeocodingResult(
                latitude=37.7849,
                longitude=-122.4094,
                display_name="San Francisco Union Square, CA, USA",
                place_id=444444,
                importance=0.7,
            ),
        ]

        request_data = {
            "source_address": "San Francisco City Hall",
            "destination_address": "San Francisco Union Square",
        }

        response = client.post("/api/v1/distance", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # Verify small distance (should be around 1-3 km within city)
        assert 0.5 <= data["distance_km"] <= 5

        # Verify precision (should have decimal places)
        assert isinstance(data["distance_km"], float)

        print("✅ Distance calculation precision works")

    @patch("app.services.geocoding.GeocodingService.geocode_address")
    def test_distance_endpoint_response_format(self, mock_geocode):
        """Test that response follows exact API specification format"""
        mock_geocode.side_effect = [
            GeocodingResult(
                latitude=40.7128,
                longitude=-74.0060,
                display_name="Test Source Location",
                place_id=111,
                importance=0.5,
            ),
            GeocodingResult(
                latitude=34.0522,
                longitude=-118.2437,
                display_name="Test Destination Location",
                place_id=222,
                importance=0.5,
            ),
        ]

        request_data = {
            "source_address": "Test Source",
            "destination_address": "Test Destination",
        }

        response = client.post("/api/v1/distance", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # Verify exact field presence and types
        assert isinstance(data["id"], int)
        assert isinstance(data["source_address"], str)
        assert isinstance(data["destination_address"], str)
        assert isinstance(data["source_lat"], (int, float))
        assert isinstance(data["source_lng"], (int, float))
        assert isinstance(data["destination_lat"], (int, float))
        assert isinstance(data["destination_lng"], (int, float))
        assert isinstance(data["source_coords"], list)
        assert isinstance(data["destination_coords"], list)
        assert isinstance(data["distance_km"], (int, float))
        assert isinstance(data["created_at"], str)

        # Verify coordinate arrays format
        assert len(data["source_coords"]) == 2
        assert len(data["destination_coords"]) == 2
        assert data["source_coords"][0] == data["source_lat"]
        assert data["source_coords"][1] == data["source_lng"]
        assert data["destination_coords"][0] == data["destination_lat"]
        assert data["destination_coords"][1] == data["destination_lng"]

        # Verify timestamp format (ISO format)
        from datetime import datetime

        try:
            datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
        except ValueError:
            pytest.fail("created_at timestamp is not in valid ISO format")

        print("✅ Response format validation works")

    @patch("app.services.geocoding.GeocodingService.geocode_address")
    def test_distance_calculation_with_long_addresses(self, mock_geocode):
        """Test distance calculation with long, detailed addresses"""
        mock_geocode.side_effect = [
            GeocodingResult(
                latitude=40.7589,
                longitude=-73.9851,
                display_name="350 Fifth Avenue, Empire State Building, Midtown Manhattan, New York County, New York, 10118, United States",
                place_id=555555,
                importance=0.8,
            ),
            GeocodingResult(
                latitude=40.7484,
                longitude=-73.9857,
                display_name="One World Trade Center, West Street, Financial District, Manhattan, New York County, New York, 10007, United States",
                place_id=666666,
                importance=0.8,
            ),
        ]

        request_data = {
            "source_address": "350 Fifth Avenue, Empire State Building, Midtown Manhattan, New York County, New York, 10118, United States",
            "destination_address": "One World Trade Center, West Street, Financial District, Manhattan, New York County, New York, 10007, United States",
        }

        response = client.post("/api/v1/distance", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # Verify addresses are preserved (though may be cleaned)
        assert (
            "Empire State" in data["source_address"] or "350" in data["source_address"]
        )
        assert (
            "World Trade" in data["destination_address"]
            or "One World" in data["destination_address"]
        )

        # Verify reasonable distance for Manhattan locations (should be small)
        assert 0.1 <= data["distance_km"] <= 10

        print("✅ Long address handling works")


class TestDistanceEndpointHealthCheck:
    """Test distance service health check endpoint."""

    def test_distance_service_health_check(self):
        """Test distance service health check endpoint"""
        response = client.get("/api/v1/distance/health")

        assert response.status_code == 200
        data = response.json()

        # Verify health check response structure
        required_fields = ["status", "service", "timestamp", "dependencies"]
        for field in required_fields:
            assert field in data

        # Verify health check values
        assert data["status"] in ["healthy", "unhealthy"]
        assert data["service"] == "distance_calculation"
        assert "dependencies" in data
        assert isinstance(data["dependencies"], dict)

        # Verify timestamp format
        from datetime import datetime

        try:
            datetime.fromisoformat(data["timestamp"])
        except ValueError:
            pytest.fail("Health check timestamp is not in valid ISO format")

        print("✅ Distance service health check works")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
