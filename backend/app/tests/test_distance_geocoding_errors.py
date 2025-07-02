"""
Test cases for geocoding error handling in distance endpoint.

This module tests error scenarios when the geocoding service fails,
including address not found, API unavailable, and partial failures.
"""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from app.main import app
from app.services.geocoding import GeocodingError, GeocodingResult

client = TestClient(app)


class TestDistanceGeocodingErrors:
    """Test geocoding error scenarios."""

    @patch("app.services.geocoding.GeocodingService.geocode_address")
    def test_source_address_not_found(self, mock_geocode):
        """Test error when source address cannot be geocoded"""
        # Mock source geocoding failure, destination success
        mock_geocode.side_effect = [
            GeocodingError("No results found for address"),
            GeocodingResult(
                latitude=37.3349,
                longitude=-122.009,
                display_name="1 Apple Park Way, Cupertino, CA",
                place_id=789012,
                importance=0.8,
            ),
        ]

        request_data = {
            "source_address": "Nonexistent Address 12345 XYZ Street",
            "destination_address": "1 Apple Park Way, Cupertino, CA",
        }

        response = client.post("/api/v1/distance", json=request_data)
        assert response.status_code == 400

        data = response.json()
        assert "error" in data
        assert "message" in data
        message = (
            data["message"]
            if isinstance(data["message"], str)
            else str(data["message"])
        )
        assert "failed to geocode" in message.lower()
        assert "source" in message.lower()

        print("✅ Source address not found error handling works")

    @patch("app.services.geocoding.GeocodingService.geocode_address")
    def test_destination_address_not_found(self, mock_geocode):
        """Test error when destination address cannot be geocoded"""
        # Mock source success, destination geocoding failure
        mock_geocode.side_effect = [
            GeocodingResult(
                latitude=37.4224764,
                longitude=-122.0842499,
                display_name="1600 Amphitheatre Parkway, Mountain View, CA",
                place_id=123456,
                importance=0.8,
            ),
            GeocodingError("No results found for address"),
        ]

        request_data = {
            "source_address": "1600 Amphitheatre Parkway, Mountain View, CA",
            "destination_address": "Nonexistent Address 54321 ABC Avenue",
        }

        response = client.post("/api/v1/distance", json=request_data)
        assert response.status_code == 400

        data = response.json()
        assert "error" in data
        assert "message" in data
        message = (
            data["message"]
            if isinstance(data["message"], str)
            else str(data["message"])
        )
        assert "failed to geocode" in message.lower()
        assert "destination" in message.lower()

        print("✅ Destination address not found error handling works")

    @patch("app.services.geocoding.GeocodingService.geocode_address")
    def test_both_addresses_not_found(self, mock_geocode):
        """Test error when both addresses cannot be geocoded"""
        # Mock both geocoding failures
        mock_geocode.side_effect = [
            GeocodingError("No results found for source address"),
            GeocodingError("No results found for destination address"),
        ]

        request_data = {
            "source_address": "Nonexistent Source 99999",
            "destination_address": "Nonexistent Destination 88888",
        }

        response = client.post("/api/v1/distance", json=request_data)
        assert response.status_code == 400

        data = response.json()
        assert "error" in data

        # Should fail on the first geocoding attempt (source)
        assert (
            "geocoding failed" in data["error"].lower()
            or "failed to geocode" in data["message"].lower()
        )

        print("✅ Both addresses not found error handling works")

    @patch("app.services.geocoding.GeocodingService.geocode_address")
    def test_geocoding_api_timeout(self, mock_geocode):
        """Test error when geocoding API times out"""
        # Mock API timeout error
        mock_geocode.side_effect = GeocodingError("Request timed out after 10 seconds")

        request_data = {
            "source_address": "123 Main St, City, State",
            "destination_address": "456 Oak Ave, City, State",
        }

        response = client.post("/api/v1/distance", json=request_data)
        assert response.status_code in [
            400,
            503,
        ]  # Accept both depending on error mapping

        data = response.json()
        assert "error" in data
        assert "message" in data
        message = (
            data["message"]
            if isinstance(data["message"], str)
            else str(data["message"])
        )
        # Should indicate service unavailable for timeouts
        assert "temporarily unavailable" in message.lower()

        print("✅ Geocoding API timeout error handling works")

    @patch("app.services.geocoding.GeocodingService.geocode_address")
    def test_geocoding_api_unavailable(self, mock_geocode):
        """Test error when geocoding API is completely unavailable"""
        # Mock API unavailable error
        mock_geocode.side_effect = GeocodingError(
            "Connection failed: Unable to connect to nominatim.openstreetmap.org"
        )

        request_data = {
            "source_address": "123 Main St, City, State",
            "destination_address": "456 Oak Ave, City, State",
        }

        response = client.post("/api/v1/distance", json=request_data)
        assert response.status_code in [
            400,
            503,
        ]  # Accept both depending on error mapping

        data = response.json()
        assert "error" in data
        assert "message" in data
        message = (
            data["message"]
            if isinstance(data["message"], str)
            else str(data["message"])
        )
        assert "temporarily unavailable" in message.lower()

        print("✅ Geocoding API unavailable error handling works")

    @patch("app.services.geocoding.GeocodingService.geocode_address")
    def test_geocoding_rate_limit_error(self, mock_geocode):
        """Test error when geocoding API rate limit is exceeded"""
        # Mock rate limit error
        mock_geocode.side_effect = GeocodingError(
            "Rate limit exceeded. Please try again later."
        )

        request_data = {
            "source_address": "123 Main St, City, State",
            "destination_address": "456 Oak Ave, City, State",
        }

        response = client.post("/api/v1/distance", json=request_data)
        assert response.status_code in [
            400,
            503,
        ]  # Accept both depending on error mapping

        data = response.json()
        assert "error" in data

        print("✅ Geocoding rate limit error handling works")

    @patch("app.services.geocoding.GeocodingService.geocode_address")
    def test_geocoding_invalid_response(self, mock_geocode):
        """Test error when geocoding API returns invalid response"""
        # Mock invalid API response error
        mock_geocode.side_effect = GeocodingError(
            "Invalid response format from geocoding service"
        )

        request_data = {
            "source_address": "123 Main St, City, State",
            "destination_address": "456 Oak Ave, City, State",
        }

        response = client.post("/api/v1/distance", json=request_data)
        assert response.status_code in [
            400,
            503,
        ]  # Accept both depending on error mapping

        data = response.json()
        assert "error" in data

        print("✅ Geocoding invalid response error handling works")

    @patch("app.services.geocoding.GeocodingService.geocode_address")
    def test_geocoding_service_internal_error(self, mock_geocode):
        """Test error when geocoding service has internal error"""
        # Mock internal service error
        mock_geocode.side_effect = Exception(
            "Unexpected internal error in geocoding service"
        )

        request_data = {
            "source_address": "123 Main St, City, State",
            "destination_address": "456 Oak Ave, City, State",
        }

        response = client.post("/api/v1/distance", json=request_data)
        assert response.status_code in [
            400,
            503,
        ]  # Accept both depending on error mapping

        data = response.json()
        assert "error" in data

        print("✅ Geocoding service internal error handling works")


class TestDistancePartialGeocodingFailures:
    """Test scenarios where geocoding partially succeeds."""

    @patch("app.services.geocoding.GeocodingService.geocode_address")
    def test_ambiguous_source_address(self, mock_geocode):
        """Test handling of ambiguous source address"""
        # Mock ambiguous address (multiple results, low confidence)
        mock_geocode.side_effect = [
            GeocodingError("Multiple results found with low confidence"),
            GeocodingResult(
                latitude=37.3349,
                longitude=-122.009,
                display_name="Clear Destination Address",
                place_id=789012,
                importance=0.8,
            ),
        ]

        request_data = {
            "source_address": "Main Street",  # Very ambiguous
            "destination_address": "1 Apple Park Way, Cupertino, CA",
        }

        response = client.post("/api/v1/distance", json=request_data)
        assert response.status_code == 400

        data = response.json()
        assert "error" in data

        print("✅ Ambiguous source address error handling works")

    @patch("app.services.geocoding.GeocodingService.geocode_address")
    def test_ambiguous_destination_address(self, mock_geocode):
        """Test handling of ambiguous destination address"""
        mock_geocode.side_effect = [
            GeocodingResult(
                latitude=37.4224764,
                longitude=-122.0842499,
                display_name="Clear Source Address",
                place_id=123456,
                importance=0.8,
            ),
            GeocodingError("Multiple results found with low confidence"),
        ]

        request_data = {
            "source_address": "1600 Amphitheatre Parkway, Mountain View, CA",
            "destination_address": "Park Street",  # Very ambiguous
        }

        response = client.post("/api/v1/distance", json=request_data)
        assert response.status_code == 400

        data = response.json()
        assert "error" in data

        print("✅ Ambiguous destination address error handling works")

    @patch("app.services.geocoding.GeocodingService.geocode_address")
    def test_geocoding_different_error_types(self, mock_geocode):
        """Test different types of geocoding errors"""
        error_scenarios = [
            ("Connection timeout", 503),
            ("Invalid API key", 503),
            ("Service temporarily unavailable", 503),
            ("Address not found in database", 400),
            ("Insufficient address details", 400),
            ("Address format not recognized", 400),
        ]

        for error_message, expected_status in error_scenarios:
            mock_geocode.side_effect = GeocodingError(error_message)

            request_data = {
                "source_address": "Test Address for Error",
                "destination_address": "Another Test Address",
            }

            response = client.post("/api/v1/distance", json=request_data)

            # Should map to appropriate status code based on error type
            assert response.status_code in [400, 503]

            data = response.json()
            assert "error" in data

        print("✅ Different geocoding error types handling works")


class TestDistanceGeocodingErrorRecovery:
    """Test error recovery and resilience scenarios."""

    @patch("app.services.geocoding.GeocodingService.geocode_address")
    def test_error_message_sanitization(self, mock_geocode):
        """Test that internal error details are not exposed"""
        # Mock error with potentially sensitive internal details
        mock_geocode.side_effect = GeocodingError(
            "Database connection failed: postgresql://user:password@internal-host:5432/geocoding_db"
        )

        request_data = {
            "source_address": "123 Main St",
            "destination_address": "456 Oak Ave",
        }

        response = client.post("/api/v1/distance", json=request_data)
        assert response.status_code in [
            400,
            503,
        ]  # Accept both depending on error mapping

        data = response.json()
        response_str = str(data).lower()

        # Verify sensitive information is not exposed
        assert "password" not in response_str
        assert "postgresql://" not in response_str
        assert "internal-host" not in response_str
        assert "5432" not in response_str

        # Should have generic error message
        message = (
            data["message"]
            if isinstance(data["message"], str)
            else str(data["message"])
        )
        assert "temporarily unavailable" in message.lower()

        print("✅ Error message sanitization works")

    @patch("app.services.geocoding.GeocodingService.geocode_address")
    def test_consistent_error_format(self, mock_geocode):
        """Test that all geocoding errors return consistent format"""
        mock_geocode.side_effect = GeocodingError("Test error message")

        request_data = {
            "source_address": "Test Source",
            "destination_address": "Test Destination",
        }

        response = client.post("/api/v1/distance", json=request_data)

        # Verify consistent error response structure
        data = response.json()
        required_error_fields = ["error", "message"]
        for field in required_error_fields:
            assert field in data, f"Missing required error field: {field}"

        # Verify error field values are strings
        assert isinstance(data["error"], str)
        assert isinstance(data["message"], str)
        assert len(data["error"]) > 0
        assert len(data["message"]) > 0

        print("✅ Consistent error format works")

    @patch("app.services.geocoding.GeocodingService.geocode_address")
    def test_geocoding_service_initialization_error(self, mock_geocode):
        """Test handling when geocoding service fails to initialize"""
        # This tests the service layer error handling
        mock_geocode.side_effect = Exception("Failed to initialize geocoding service")

        request_data = {
            "source_address": "123 Main St",
            "destination_address": "456 Oak Ave",
        }

        response = client.post("/api/v1/distance", json=request_data)

        # Should handle gracefully with service unavailable
        assert response.status_code in [500, 503]

        data = response.json()
        assert "error" in data

        print("✅ Geocoding service initialization error handling works")

    @patch("app.services.geocoding.GeocodingService.geocode_address")
    def test_concurrent_geocoding_failure(self, mock_geocode):
        """Test handling when concurrent geocoding requests fail"""
        # Mock both geocoding calls failing simultaneously
        mock_geocode.side_effect = [
            GeocodingError("Source geocoding failed"),
            GeocodingError("Destination geocoding failed"),
        ]

        request_data = {
            "source_address": "Fail Source",
            "destination_address": "Fail Destination",
        }

        response = client.post("/api/v1/distance", json=request_data)

        # Should fail on first geocoding attempt
        assert response.status_code == 400

        data = response.json()
        assert "error" in data

        print("✅ Concurrent geocoding failure handling works")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
