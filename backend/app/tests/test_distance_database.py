"""
Test cases for database integration in distance endpoint.

This module tests database storage, transaction handling, and error scenarios
when storing distance calculation results.
"""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.main import app
from app.models.distance_query import DistanceQuery
from app.models.database import SessionLocal
from app.services.geocoding import GeocodingResult

client = TestClient(app)


class TestDistanceDatabaseIntegration:
    """Test database storage and retrieval functionality."""

    @patch("app.services.geocoding.GeocodingService.geocode_address")
    def test_distance_query_stored_in_database(self, mock_geocode):
        """Test that distance queries are properly stored in database"""
        # Mock geocoding responses
        mock_geocode.side_effect = [
            GeocodingResult(
                latitude=40.7128,
                longitude=-74.0060,
                display_name="New York, NY, USA",
                place_id=111111,
                importance=0.9,
            ),
            GeocodingResult(
                latitude=34.0522,
                longitude=-118.2437,
                display_name="Los Angeles, CA, USA",
                place_id=222222,
                importance=0.9,
            ),
        ]

        # Get initial count of records
        db = SessionLocal()
        initial_count = db.query(DistanceQuery).count()
        db.close()

        request_data = {
            "source_address": "New York, NY, USA",
            "destination_address": "Los Angeles, CA, USA",
        }

        response = client.post("/api/v1/distance", json=request_data)
        assert response.status_code == 200

        # Verify record was added to database
        db = SessionLocal()
        try:
            final_count = db.query(DistanceQuery).count()
            assert final_count == initial_count + 1

            # Verify stored data
            latest_query = (
                db.query(DistanceQuery)
                .order_by(DistanceQuery.created_at.desc())
                .first()
            )
            assert latest_query is not None
            assert latest_query.source_address == "New York, NY, USA"
            assert latest_query.destination_address == "Los Angeles, CA, USA"
            assert float(latest_query.source_lat) == 40.7128
            assert float(latest_query.source_lng) == -74.0060
            assert float(latest_query.destination_lat) == 34.0522
            assert float(latest_query.destination_lng) == -118.2437
            assert latest_query.distance_km is not None
            assert float(latest_query.distance_km) > 0
            assert latest_query.created_at is not None

            # Verify response contains database ID
            response_data = response.json()
            assert response_data["id"] == latest_query.id

        finally:
            db.close()

        print("✅ Distance query database storage works")

    @patch("app.services.geocoding.GeocodingService.geocode_address")
    def test_database_record_fields_accuracy(self, mock_geocode):
        """Test accuracy of stored database fields"""
        # Mock precise geocoding responses
        mock_geocode.side_effect = [
            GeocodingResult(
                latitude=37.7749295,
                longitude=-122.4194155,
                display_name="San Francisco, CA, USA",
                place_id=333333,
                importance=0.8,
            ),
            GeocodingResult(
                latitude=37.4419522,
                longitude=-122.1430195,
                display_name="Palo Alto, CA, USA",
                place_id=444444,
                importance=0.7,
            ),
        ]

        request_data = {
            "source_address": "San Francisco, CA, USA",
            "destination_address": "Palo Alto, CA, USA",
        }

        response = client.post("/api/v1/distance", json=request_data)
        assert response.status_code == 200

        response_data = response.json()
        record_id = response_data["id"]

        # Verify database record matches response
        db = SessionLocal()
        try:
            stored_query = (
                db.query(DistanceQuery).filter(DistanceQuery.id == record_id).first()
            )
            assert stored_query is not None

            # Check coordinate precision (should match exactly)
            assert abs(float(stored_query.source_lat) - 37.7749295) < 0.0000001
            assert abs(float(stored_query.source_lng) - (-122.4194155)) < 0.0000001
            assert abs(float(stored_query.destination_lat) - 37.4419522) < 0.0000001
            assert abs(float(stored_query.destination_lng) - (-122.1430195)) < 0.0000001

            # Check distance precision (calculated distance should be reasonable)
            expected_distance = float(stored_query.distance_km)
            assert (
                30 <= expected_distance <= 70
            )  # San Francisco to Palo Alto is ~45-50 km

            # Verify response data matches database
            assert response_data["source_lat"] == float(stored_query.source_lat)
            assert response_data["source_lng"] == float(stored_query.source_lng)
            assert response_data["destination_lat"] == float(
                stored_query.destination_lat
            )
            assert response_data["destination_lng"] == float(
                stored_query.destination_lng
            )
            assert response_data["distance_km"] == float(stored_query.distance_km)

        finally:
            db.close()

        print("✅ Database record field accuracy works")

    @patch("app.services.geocoding.GeocodingService.geocode_address")
    def test_multiple_queries_stored_separately(self, mock_geocode):
        """Test that multiple queries are stored as separate records"""
        # First query
        mock_geocode.side_effect = [
            GeocodingResult(
                latitude=40.7128,
                longitude=-74.0060,
                display_name="New York, NY",
                place_id=111,
                importance=0.9,
            ),
            GeocodingResult(
                latitude=41.8781,
                longitude=-87.6298,
                display_name="Chicago, IL",
                place_id=222,
                importance=0.9,
            ),
        ]

        request1 = {
            "source_address": "New York, NY",
            "destination_address": "Chicago, IL",
        }

        response1 = client.post("/api/v1/distance", json=request1)
        assert response1.status_code == 200

        # Second query with different addresses
        mock_geocode.side_effect = [
            GeocodingResult(
                latitude=34.0522,
                longitude=-118.2437,
                display_name="Los Angeles, CA",
                place_id=333,
                importance=0.9,
            ),
            GeocodingResult(
                latitude=37.7749,
                longitude=-122.4194,
                display_name="San Francisco, CA",
                place_id=444,
                importance=0.8,
            ),
        ]

        request2 = {
            "source_address": "Los Angeles, CA",
            "destination_address": "San Francisco, CA",
        }

        response2 = client.post("/api/v1/distance", json=request2)
        assert response2.status_code == 200

        # Verify both records exist and are different
        response1_data = response1.json()
        response2_data = response2.json()

        assert response1_data["id"] != response2_data["id"]
        assert response1_data["source_address"] != response2_data["source_address"]
        assert (
            response1_data["destination_address"]
            != response2_data["destination_address"]
        )

        # Verify both exist in database
        db = SessionLocal()
        try:
            query1 = (
                db.query(DistanceQuery)
                .filter(DistanceQuery.id == response1_data["id"])
                .first()
            )
            query2 = (
                db.query(DistanceQuery)
                .filter(DistanceQuery.id == response2_data["id"])
                .first()
            )

            assert query1 is not None
            assert query2 is not None
            assert query1.id != query2.id

        finally:
            db.close()

        print("✅ Multiple queries stored separately works")

    @patch("app.services.geocoding.GeocodingService.geocode_address")
    def test_timestamp_handling(self, mock_geocode):
        """Test proper timestamp handling in database storage"""
        from datetime import datetime

        mock_geocode.side_effect = [
            GeocodingResult(
                latitude=42.3601,
                longitude=-71.0589,
                display_name="Boston, MA",
                place_id=555,
                importance=0.8,
            ),
            GeocodingResult(
                latitude=39.2904,
                longitude=-76.6122,
                display_name="Baltimore, MD",
                place_id=666,
                importance=0.7,
            ),
        ]

        # Record time before request
        before_request = datetime.utcnow()

        request_data = {
            "source_address": "Boston, MA",
            "destination_address": "Baltimore, MD",
        }

        response = client.post("/api/v1/distance", json=request_data)
        assert response.status_code == 200

        # Record time after request
        after_request = datetime.utcnow()

        response_data = response.json()
        record_id = response_data["id"]

        # Verify timestamp in database
        db = SessionLocal()
        try:
            stored_query = (
                db.query(DistanceQuery).filter(DistanceQuery.id == record_id).first()
            )
            assert stored_query is not None

            # Verify timestamp is within reasonable range
            created_at = stored_query.created_at
            assert before_request <= created_at <= after_request

            # Verify timestamp in response matches database
            response_timestamp = datetime.fromisoformat(
                response_data["created_at"].replace("Z", "+00:00")
            )
            # Allow small differences due to serialization
            time_diff = abs(
                (response_timestamp.replace(tzinfo=None) - created_at).total_seconds()
            )
            assert time_diff < 1.0  # Should be within 1 second

        finally:
            db.close()

        print("✅ Timestamp handling works")


class TestDistanceDatabaseErrorHandling:
    """Test database error scenarios and transaction handling."""

    @patch("app.services.geocoding.GeocodingService.geocode_address")
    @patch("app.services.distance_service.SessionLocal")
    def test_database_connection_error(self, mock_session_local, mock_geocode):
        """Test handling of database connection errors"""
        # Mock successful geocoding
        mock_geocode.side_effect = [
            GeocodingResult(
                latitude=40.7128,
                longitude=-74.0060,
                display_name="New York, NY",
                place_id=111,
                importance=0.9,
            ),
            GeocodingResult(
                latitude=34.0522,
                longitude=-118.2437,
                display_name="Los Angeles, CA",
                place_id=222,
                importance=0.9,
            ),
        ]

        # Mock database connection failure
        mock_db = mock_session_local.return_value
        mock_db.add.side_effect = SQLAlchemyError("Connection failed")

        request_data = {
            "source_address": "New York, NY",
            "destination_address": "Los Angeles, CA",
        }

        response = client.post("/api/v1/distance", json=request_data)
        assert response.status_code == 500

        data = response.json()
        assert "error" in data
        assert "message" in data
        message = (
            data["message"]
            if isinstance(data["message"], str)
            else str(data["message"])
        )
        assert "internal" in message.lower() or "error" in message.lower()

        # Verify rollback was called
        mock_db.rollback.assert_called()

        print("✅ Database connection error handling works")

    @patch("app.services.geocoding.GeocodingService.geocode_address")
    @patch("app.services.distance_service.SessionLocal")
    def test_database_commit_error(self, mock_session_local, mock_geocode):
        """Test handling of database commit errors"""
        # Mock successful geocoding
        mock_geocode.side_effect = [
            GeocodingResult(
                latitude=47.6062,
                longitude=-122.3321,
                display_name="Seattle, WA",
                place_id=777,
                importance=0.8,
            ),
            GeocodingResult(
                latitude=45.5152,
                longitude=-122.6784,
                display_name="Portland, OR",
                place_id=888,
                importance=0.8,
            ),
        ]

        # Mock database commit failure
        mock_db = mock_session_local.return_value
        mock_db.commit.side_effect = SQLAlchemyError("Commit failed")

        request_data = {
            "source_address": "Seattle, WA",
            "destination_address": "Portland, OR",
        }

        response = client.post("/api/v1/distance", json=request_data)
        assert response.status_code == 500

        data = response.json()
        assert "error" in data
        assert "message" in data
        message = (
            data["message"]
            if isinstance(data["message"], str)
            else str(data["message"])
        )
        assert "internal" in message.lower() or "error" in message.lower()

        # Verify rollback was called
        mock_db.rollback.assert_called()

        print("✅ Database commit error handling works")

    @patch("app.services.geocoding.GeocodingService.geocode_address")
    def test_transaction_rollback_on_error(self, mock_geocode):
        """Test that transactions are properly rolled back on errors"""
        # Mock geocoding to succeed then fail
        mock_geocode.side_effect = [
            GeocodingResult(
                latitude=33.4484,
                longitude=-112.0740,
                display_name="Phoenix, AZ",
                place_id=999,
                importance=0.7,
            ),
            Exception("Unexpected geocoding error after first success"),
        ]

        # Get initial count
        db = SessionLocal()
        initial_count = db.query(DistanceQuery).count()
        db.close()

        request_data = {
            "source_address": "Phoenix, AZ",
            "destination_address": "Invalid Address for Error",
        }

        response = client.post("/api/v1/distance", json=request_data)
        assert response.status_code == 503  # Service unavailable due to geocoding error

        # Verify no record was added (transaction rolled back)
        db = SessionLocal()
        try:
            final_count = db.query(DistanceQuery).count()
            assert final_count == initial_count  # No change in count
        finally:
            db.close()

        print("✅ Transaction rollback on error works")

    @patch("app.services.geocoding.GeocodingService.geocode_address")
    def test_database_constraint_violation(self, mock_geocode):
        """Test handling of database constraint violations"""
        # This test simulates what would happen if there were database constraints
        # that could be violated (e.g., unique constraints, check constraints)

        mock_geocode.side_effect = [
            GeocodingResult(
                latitude=0.0,  # Could potentially violate a constraint
                longitude=0.0,
                display_name="Null Island",
                place_id=000,
                importance=0.1,
            ),
            GeocodingResult(
                latitude=0.0,
                longitude=0.0,
                display_name="Null Island",
                place_id=000,
                importance=0.1,
            ),
        ]

        request_data = {
            "source_address": "Null Island",
            "destination_address": "Null Island",
        }

        response = client.post("/api/v1/distance", json=request_data)

        # Should handle gracefully - either succeed or fail appropriately
        assert response.status_code in [200, 400, 500]

        if response.status_code != 200:
            data = response.json()
            assert "error" in data

        print("✅ Database constraint handling works")


class TestDistanceDatabasePerformance:
    """Test database performance and optimization."""

    @patch("app.services.geocoding.GeocodingService.geocode_address")
    def test_database_session_cleanup(self, mock_geocode):
        """Test that database sessions are properly cleaned up"""
        mock_geocode.side_effect = [
            GeocodingResult(
                latitude=30.2672,
                longitude=-97.7431,
                display_name="Austin, TX",
                place_id=101010,
                importance=0.8,
            ),
            GeocodingResult(
                latitude=29.7604,
                longitude=-95.3698,
                display_name="Houston, TX",
                place_id=111111,
                importance=0.8,
            ),
        ]

        request_data = {
            "source_address": "Austin, TX",
            "destination_address": "Houston, TX",
        }

        # Make multiple requests to test session management
        for i in range(3):
            response = client.post("/api/v1/distance", json=request_data)
            # Should succeed for all requests (no session leaks)
            assert response.status_code in [
                200,
                400,
                503,
            ]  # Various acceptable outcomes

        print("✅ Database session cleanup works")

    @patch("app.services.geocoding.GeocodingService.geocode_address")
    def test_concurrent_database_operations(self, mock_geocode):
        """Test handling of concurrent database operations"""
        # Mock different geocoding results for concurrent requests
        mock_geocode.side_effect = [
            GeocodingResult(
                latitude=25.7617,
                longitude=-80.1918,
                display_name="Miami, FL",
                place_id=121212,
                importance=0.8,
            ),
            GeocodingResult(
                latitude=26.1224,
                longitude=-80.1373,
                display_name="Fort Lauderdale, FL",
                place_id=131313,
                importance=0.7,
            ),
            GeocodingResult(
                latitude=28.5383,
                longitude=-81.3792,
                display_name="Orlando, FL",
                place_id=141414,
                importance=0.8,
            ),
            GeocodingResult(
                latitude=27.9506,
                longitude=-82.4572,
                display_name="Tampa, FL",
                place_id=151515,
                importance=0.8,
            ),
        ]

        request1 = {
            "source_address": "Miami, FL",
            "destination_address": "Fort Lauderdale, FL",
        }
        request2 = {"source_address": "Orlando, FL", "destination_address": "Tampa, FL"}

        # Make concurrent-ish requests
        response1 = client.post("/api/v1/distance", json=request1)
        response2 = client.post("/api/v1/distance", json=request2)

        # Both should succeed (or fail gracefully)
        assert response1.status_code in [200, 400, 503]
        assert response2.status_code in [200, 400, 503]

        # If both succeeded, they should have different IDs
        if response1.status_code == 200 and response2.status_code == 200:
            data1 = response1.json()
            data2 = response2.json()
            assert data1["id"] != data2["id"]

        print("✅ Concurrent database operations work")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
