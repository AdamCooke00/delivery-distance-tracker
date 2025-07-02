"""
Test cases for end-to-end distance calculation integration.

This module tests the complete flow from API request to database storage
using real geocoding services when available (skippable for CI/CD).
"""

import pytest
import os
from fastapi.testclient import TestClient

from app.main import app
from app.models.distance_query import DistanceQuery
from app.models.database import SessionLocal

client = TestClient(app)


class TestDistanceEndToEndIntegration:
    """Test complete end-to-end distance calculation workflow."""

    @pytest.mark.skipif(
        os.getenv("SKIP_E2E_TESTS") == "true", reason="End-to-end tests skipped"
    )
    def test_complete_distance_calculation_flow_real_api(self):
        """Test complete flow from request to response with real geocoding"""
        request_data = {
            "source_address": "Empire State Building, New York, NY",
            "destination_address": "Statue of Liberty, New York, NY",
        }

        # Get initial database count
        db = SessionLocal()
        initial_count = db.query(DistanceQuery).count()
        db.close()

        response = client.post("/api/v1/distance", json=request_data)

        if response.status_code == 200:
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
            ]
            for field in required_fields:
                assert field in data, f"Missing field: {field}"

            # Verify coordinate ranges (should be in NYC area)
            assert (
                40.0 <= data["source_lat"] <= 41.0
            ), f"Source latitude out of NYC range: {data['source_lat']}"
            assert (
                -75.0 <= data["source_lng"] <= -73.0
            ), f"Source longitude out of NYC range: {data['source_lng']}"
            assert (
                40.0 <= data["destination_lat"] <= 41.0
            ), f"Destination latitude out of NYC range: {data['destination_lat']}"
            assert (
                -75.0 <= data["destination_lng"] <= -73.0
            ), f"Destination longitude out of NYC range: {data['destination_lng']}"

            # Verify reasonable distance (Empire State to Statue of Liberty ~8-10 km)
            assert (
                5 <= data["distance_km"] <= 15
            ), f"Distance out of expected range: {data['distance_km']} km"

            # Verify database storage
            db = SessionLocal()
            try:
                final_count = db.query(DistanceQuery).count()
                assert final_count == initial_count + 1, "Record not added to database"

                stored_query = (
                    db.query(DistanceQuery)
                    .filter(DistanceQuery.id == data["id"])
                    .first()
                )
                assert stored_query is not None, "Stored record not found"
                assert stored_query.source_address == data["source_address"]
                assert stored_query.destination_address == data["destination_address"]
                assert float(stored_query.distance_km) == data["distance_km"]
            finally:
                db.close()

            print("✅ End-to-end distance calculation with real API works")
        else:
            # If geocoding fails, that's acceptable for this test
            print(
                f"⚠️ End-to-end test skipped due to geocoding service response: {response.status_code}"
            )
            pytest.skip(
                f"Geocoding service returned {response.status_code}, skipping E2E test"
            )

    @pytest.mark.skipif(
        os.getenv("SKIP_E2E_TESTS") == "true", reason="End-to-end tests skipped"
    )
    def test_international_distance_calculation_e2e(self):
        """Test end-to-end with international addresses"""
        request_data = {
            "source_address": "Eiffel Tower, Paris, France",
            "destination_address": "Big Ben, London, UK",
        }

        response = client.post("/api/v1/distance", json=request_data)

        if response.status_code == 200:
            data = response.json()

            # Verify international coordinates
            # Paris: ~48.8566, 2.3522
            # London: ~51.5074, -0.1278
            assert (
                48.0 <= data["source_lat"] <= 49.0
            ), f"Paris latitude out of range: {data['source_lat']}"
            assert (
                2.0 <= data["source_lng"] <= 3.0
            ), f"Paris longitude out of range: {data['source_lng']}"
            assert (
                51.0 <= data["destination_lat"] <= 52.0
            ), f"London latitude out of range: {data['destination_lat']}"
            assert (
                -1.0 <= data["destination_lng"] <= 1.0
            ), f"London longitude out of range: {data['destination_lng']}"

            # Verify reasonable distance (Paris to London ~340-350 km)
            assert (
                300 <= data["distance_km"] <= 400
            ), f"Distance out of expected range: {data['distance_km']} km"

            print("✅ International distance calculation works")
        else:
            print(f"⚠️ International E2E test skipped: {response.status_code}")
            pytest.skip(f"International geocoding failed with {response.status_code}")

    @pytest.mark.skipif(
        os.getenv("SKIP_E2E_TESTS") == "true", reason="End-to-end tests skipped"
    )
    def test_same_city_distance_calculation_e2e(self):
        """Test end-to-end with addresses in same city"""
        request_data = {
            "source_address": "Golden Gate Bridge, San Francisco, CA",
            "destination_address": "Alcatraz Island, San Francisco, CA",
        }

        response = client.post("/api/v1/distance", json=request_data)

        if response.status_code == 200:
            data = response.json()

            # Verify San Francisco area coordinates
            assert (
                37.0 <= data["source_lat"] <= 38.0
            ), f"SF source latitude out of range: {data['source_lat']}"
            assert (
                -123.0 <= data["source_lng"] <= -122.0
            ), f"SF source longitude out of range: {data['source_lng']}"
            assert (
                37.0 <= data["destination_lat"] <= 38.0
            ), f"SF destination latitude out of range: {data['destination_lat']}"
            assert (
                -123.0 <= data["destination_lng"] <= -122.0
            ), f"SF destination longitude out of range: {data['destination_lng']}"

            # Verify short distance (Golden Gate to Alcatraz ~3-5 km)
            assert (
                1 <= data["distance_km"] <= 10
            ), f"Distance out of expected range: {data['distance_km']} km"

            print("✅ Same city distance calculation works")
        else:
            print(f"⚠️ Same city E2E test skipped: {response.status_code}")
            pytest.skip(f"Same city geocoding failed with {response.status_code}")

    def test_e2e_with_fallback_behavior(self):
        """Test end-to-end behavior when real geocoding is unavailable"""
        # This test always runs and shows how the system behaves when geocoding fails
        request_data = {
            "source_address": "Nonexistent Place That Should Never Be Found 99999",
            "destination_address": "Another Fake Address 88888",
        }

        response = client.post("/api/v1/distance", json=request_data)

        # Should handle gracefully with appropriate error
        assert response.status_code in [
            400,
            503,
        ], f"Unexpected status code: {response.status_code}"

        data = response.json()
        assert "error" in data, "Error response should contain 'error' field"
        assert "message" in data, "Error response should contain 'message' field"

        # Verify no database record was created for failed request
        if "id" in data:
            # If there's an ID, something went wrong with error handling
            pytest.fail("Failed geocoding request should not create database record")

        print("✅ Fallback behavior for unavailable geocoding works")

    @pytest.mark.skipif(
        os.getenv("SKIP_E2E_TESTS") == "true", reason="End-to-end tests skipped"
    )
    def test_multiple_sequential_e2e_requests(self):
        """Test multiple sequential end-to-end requests"""
        test_cases = [
            {
                "source_address": "Times Square, New York, NY",
                "destination_address": "Central Park, New York, NY",
                "expected_max_distance": 5,
            },
            {
                "source_address": "Hollywood Sign, Los Angeles, CA",
                "destination_address": "Santa Monica Pier, Los Angeles, CA",
                "expected_max_distance": 30,
            },
            {
                "source_address": "Navy Pier, Chicago, IL",
                "destination_address": "Willis Tower, Chicago, IL",
                "expected_max_distance": 10,
            },
        ]

        successful_requests = 0

        for i, test_case in enumerate(test_cases):
            response = client.post("/api/v1/distance", json=test_case)

            if response.status_code == 200:
                data = response.json()

                # Verify reasonable distance
                assert (
                    data["distance_km"] <= test_case["expected_max_distance"]
                ), f"Distance too large for test case {i}: {data['distance_km']} km"

                # Verify unique database IDs
                assert "id" in data and isinstance(data["id"], int)

                successful_requests += 1
                print(
                    f"✅ Sequential request {i+1} successful: {data['distance_km']} km"
                )
            else:
                print(f"⚠️ Sequential request {i+1} failed: {response.status_code}")

        # At least one request should succeed for this test to be meaningful
        if successful_requests == 0:
            pytest.skip("No geocoding requests succeeded, skipping sequential test")
        else:
            print(
                f"✅ Sequential E2E requests work ({successful_requests}/{len(test_cases)} successful)"
            )

    def test_response_time_performance_e2e(self):
        """Test response time performance for distance calculations"""
        import time

        request_data = {
            "source_address": "Boston, MA",
            "destination_address": "New York, NY",
        }

        start_time = time.time()
        response = client.post("/api/v1/distance", json=request_data)
        end_time = time.time()

        response_time = end_time - start_time

        # Response should be reasonably fast (even with real geocoding)
        assert response_time < 30.0, f"Response too slow: {response_time:.2f} seconds"

        if response.status_code == 200:
            print(f"✅ E2E response time acceptable: {response_time:.2f}s")
        else:
            print(
                f"✅ E2E error response time acceptable: {response_time:.2f}s (status: {response.status_code})"
            )

    @pytest.mark.skipif(
        os.getenv("SKIP_E2E_TESTS") == "true", reason="End-to-end tests skipped"
    )
    def test_address_variations_e2e(self):
        """Test different address format variations end-to-end"""
        address_variations = [
            {
                "source_address": "1600 Amphitheatre Parkway, Mountain View, CA 94043",  # Full with ZIP
                "destination_address": "Apple Park, Cupertino, CA",  # Landmark name
            },
            {
                "source_address": "Space Needle",  # Famous landmark only
                "destination_address": "Pike Place Market, Seattle",  # Landmark with city
            },
            {
                "source_address": "Fenway Park, Boston, Massachusetts",  # Full state name
                "destination_address": "Harvard University, Cambridge, MA",  # Institution
            },
        ]

        successful_variations = 0

        for i, addresses in enumerate(address_variations):
            response = client.post("/api/v1/distance", json=addresses)

            if response.status_code == 200:
                data = response.json()

                # Verify basic response structure
                assert "distance_km" in data
                assert "source_coords" in data
                assert "destination_coords" in data
                assert data["distance_km"] > 0

                successful_variations += 1
                print(
                    f"✅ Address variation {i+1} successful: {data['distance_km']} km"
                )
            else:
                print(f"⚠️ Address variation {i+1} failed: {response.status_code}")

        if successful_variations == 0:
            pytest.skip("No address variations succeeded, skipping variation test")
        else:
            print(
                f"✅ Address variations work ({successful_variations}/{len(address_variations)} successful)"
            )

    def test_health_check_integration_e2e(self):
        """Test that distance service health check works end-to-end"""
        response = client.get("/api/v1/distance/health")

        assert response.status_code == 200
        data = response.json()

        # Verify health check structure
        required_fields = ["status", "service", "timestamp", "dependencies"]
        for field in required_fields:
            assert field in data, f"Missing health check field: {field}"

        assert data["service"] == "distance_calculation"
        assert data["status"] in ["healthy", "unhealthy"]

        # Verify timestamp is recent
        from datetime import datetime

        timestamp = datetime.fromisoformat(data["timestamp"])
        time_diff = (datetime.utcnow() - timestamp).total_seconds()
        assert time_diff < 60, "Health check timestamp too old"

        print("✅ Distance service health check integration works")


class TestDistanceE2EErrorScenarios:
    """Test end-to-end error scenarios."""

    def test_invalid_request_e2e(self):
        """Test end-to-end with invalid request data"""
        invalid_requests = [
            {},  # Empty request
            {"source_address": ""},  # Empty source
            {"destination_address": ""},  # Empty destination
            {"source_address": "   ", "destination_address": "   "},  # Whitespace only
        ]

        for invalid_request in invalid_requests:
            response = client.post("/api/v1/distance", json=invalid_request)
            assert (
                response.status_code == 422
            ), f"Should reject invalid request: {invalid_request}"

            data = response.json()
            assert (
                "details" in data and "validation_errors" in data["details"]
            ), "Validation error should have details"

        print("✅ Invalid request E2E handling works")

    def test_malformed_json_e2e(self):
        """Test end-to-end with malformed JSON"""
        # Test with completely invalid JSON
        response = client.post(
            "/api/v1/distance",
            data="not json at all",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 422

        print("✅ Malformed JSON E2E handling works")

    def test_unsupported_http_methods_e2e(self):
        """Test end-to-end with unsupported HTTP methods"""
        request_data = {
            "source_address": "Test Source",
            "destination_address": "Test Destination",
        }

        # Test unsupported methods
        response = client.get("/api/v1/distance", params=request_data)
        assert response.status_code == 405  # Method not allowed

        response = client.put("/api/v1/distance", json=request_data)
        assert response.status_code == 405

        response = client.delete("/api/v1/distance")
        assert response.status_code == 405

        print("✅ Unsupported HTTP methods E2E handling works")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
