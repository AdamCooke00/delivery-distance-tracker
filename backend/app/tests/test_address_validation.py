"""
Test cases for address validation functionality.

This module tests the address validation and sanitization utilities
with both valid and malicious input patterns.
"""

import pytest
from app.utils.validation import (
    validate_address,
    sanitize_address,
    ValidationError,
    validate_coordinates,
    normalize_coordinates,
)


class TestAddressValidation:
    """Test address validation functionality."""

    def test_valid_address_validation(self):
        """Test validation of properly formatted addresses"""
        valid_addresses = [
            "1600 Amphitheatre Parkway, Mountain View, CA, USA",
            "123 Main Street, New York, NY",
            "Big Ben, London, UK",
            "Times Square, New York City",
            "Golden Gate Bridge, San Francisco",
            "Eiffel Tower, Paris, France",
            "10 Downing Street, London, UK",
            "Brandenburg Gate, Berlin, Germany",
        ]

        for address in valid_addresses:
            assert (
                validate_address(address) is True
            ), f"Valid address failed validation: {address}"
            sanitized = sanitize_address(address)
            assert len(sanitized) > 0, f"Sanitization made address empty: {address}"
            # Sanitized should be same or cleaner version
            assert len(sanitized) <= len(address) or sanitized == address

        print("✅ Valid address validation works")

    def test_invalid_address_validation(self):
        """Test rejection of invalid addresses"""
        invalid_addresses = [
            "",  # Empty string
            "   ",  # Only whitespace
            "a",  # Too short
            "xy",  # Too short
            "123",  # Only numbers, too short
            None,  # None value
            123,  # Not a string
            [],  # Wrong type
        ]

        for address in invalid_addresses:
            assert (
                validate_address(address) is False
            ), f"Invalid address passed validation: {address}"

        print("✅ Invalid address validation works")

    def test_malicious_address_validation(self):
        """Test rejection of malicious content"""
        malicious_addresses = [
            "SELECT * FROM users",  # SQL injection
            "'; DROP TABLE users; --",  # SQL injection
            "<script>alert('xss')</script>",  # XSS
            "javascript:alert('hack')",  # JavaScript injection
            "onload=alert('xss')",  # Event handler
            "123 Main St<script>alert('xss')</script>",  # Mixed content
            "123 Main St'; DROP TABLE distance_queries; --",  # SQL in address
            "<iframe src='evil.com'></iframe>",  # iframe injection
        ]

        for address in malicious_addresses:
            assert (
                validate_address(address) is False
            ), f"Malicious address passed validation: {address}"

        print("✅ Malicious address validation works")

    def test_address_sanitization(self):
        """Test address sanitization removes dangerous content"""
        test_cases = [
            {
                "input": "123 Main St<script>alert('xss')</script>",
                "should_contain": "123 Main St",
                "should_not_contain": "<script>",
            },
            {
                "input": "123 Main St'; DROP TABLE users; --",
                "should_contain": "123 Main St",
                "should_not_contain": "DROP TABLE",
            },
            {
                "input": "123 Main St\n\r\t   ",
                "should_contain": "123 Main St",
                "should_not_contain": "\n",
            },
            {
                "input": "  123   Main   Street  ",
                "should_contain": "123 Main Street",
                "should_not_contain": "  ",  # Multiple spaces
            },
        ]

        for test_case in test_cases:
            sanitized = sanitize_address(test_case["input"])

            assert (
                test_case["should_contain"] in sanitized
            ), f"Sanitized address missing expected content: {sanitized}"

            assert (
                test_case["should_not_contain"] not in sanitized
            ), f"Sanitized address contains dangerous content: {sanitized}"

        print("✅ Address sanitization works")

    def test_address_sanitization_errors(self):
        """Test sanitization error cases"""
        error_cases = [
            None,  # None input
            "",  # Empty string
            "   ",  # Only whitespace
            123,  # Wrong type
            "xy",  # Too short after sanitization
        ]

        for address in error_cases:
            with pytest.raises(ValidationError):
                sanitize_address(address)

        print("✅ Address sanitization error handling works")

    def test_very_long_address_validation(self):
        """Test validation of extremely long addresses"""
        # Create a very long address (over 500 characters)
        long_address = "A" * 501
        assert validate_address(long_address) is False

        # Test at the boundary
        boundary_address = "A" * 500
        assert (
            validate_address(boundary_address) is False
        )  # Still too long without meaningful content

        # Test reasonable long address
        reasonable_long = (
            "123 Very Long Street Name That Goes On And On, "
            + "A" * 50
            + " City, State"
        )
        if len(reasonable_long) <= 500:
            assert validate_address(reasonable_long) is True

        print("✅ Long address validation works")


class TestCoordinateValidation:
    """Test coordinate validation functionality."""

    def test_valid_coordinates(self):
        """Test validation of valid coordinates"""
        valid_coords = [
            (0.0, 0.0),  # Equator, Prime Meridian
            (90.0, 180.0),  # North Pole, Date Line
            (-90.0, -180.0),  # South Pole, Date Line
            (37.7749, -122.4194),  # San Francisco
            (40.7128, -74.0060),  # New York
            (51.5074, -0.1278),  # London
            (-33.8688, 151.2093),  # Sydney
        ]

        for lat, lng in valid_coords:
            assert (
                validate_coordinates(lat, lng) is True
            ), f"Valid coordinates failed: ({lat}, {lng})"

            # Test normalization
            norm_lat, norm_lng = normalize_coordinates(lat, lng)
            assert isinstance(norm_lat, float)
            assert isinstance(norm_lng, float)
            assert -90 <= norm_lat <= 90
            assert -180 <= norm_lng <= 180

        print("✅ Valid coordinate validation works")

    def test_invalid_coordinates(self):
        """Test rejection of invalid coordinates"""
        invalid_coords = [
            (91.0, 0.0),  # Latitude too high
            (-91.0, 0.0),  # Latitude too low
            (0.0, 181.0),  # Longitude too high
            (0.0, -181.0),  # Longitude too low
            (float("inf"), 0.0),  # Infinity
            (0.0, float("nan")),  # NaN
            ("40.7", "-74.0"),  # String coordinates
            (None, 0.0),  # None values
        ]

        for lat, lng in invalid_coords:
            assert (
                validate_coordinates(lat, lng) is False
            ), f"Invalid coordinates passed: ({lat}, {lng})"

        print("✅ Invalid coordinate validation works")

    def test_coordinate_normalization_errors(self):
        """Test coordinate normalization error handling"""
        error_coords = [
            (91.0, 0.0),
            (0.0, 181.0),
            (float("inf"), 0.0),
            (0.0, float("nan")),
        ]

        for lat, lng in error_coords:
            with pytest.raises(ValidationError):
                normalize_coordinates(lat, lng)

        print("✅ Coordinate normalization error handling works")

    def test_coordinate_precision(self):
        """Test coordinate precision normalization"""
        # Test high precision coordinates
        high_precision_coords = [
            (37.77493123456789, -122.41941987654321),
            (40.71280000000001, -74.00600000000001),
        ]

        for lat, lng in high_precision_coords:
            norm_lat, norm_lng = normalize_coordinates(lat, lng)

            # Should be rounded to 7 decimal places
            assert len(str(norm_lat).split(".")[-1]) <= 7
            assert len(str(norm_lng).split(".")[-1]) <= 7

            # Should be close to original
            assert abs(norm_lat - lat) < 0.0000001
            assert abs(norm_lng - lng) < 0.0000001

        print("✅ Coordinate precision normalization works")


class TestValidationUtilities:
    """Test additional validation utilities."""

    def test_distance_unit_validation(self):
        """Test distance unit validation"""
        from app.utils.validation import validate_distance_unit, normalize_distance_unit

        valid_units = ["km", "kilometers", "mi", "miles", "meter", "meters", "m"]
        for unit in valid_units:
            assert validate_distance_unit(unit) is True
            normalized = normalize_distance_unit(unit)
            assert normalized in ["km", "miles"]

        invalid_units = ["yards", "feet", "inches", "lightyears", ""]
        for unit in invalid_units:
            assert validate_distance_unit(unit) is False

        print("✅ Distance unit validation works")

    def test_pagination_validation(self):
        """Test pagination parameter validation"""
        from app.utils.validation import validate_pagination_params

        # Test valid parameters
        limit, offset = validate_pagination_params(10, 20)
        assert limit == 10
        assert offset == 20

        # Test defaults
        limit, offset = validate_pagination_params(None, None)
        assert limit == 10
        assert offset == 0

        # Test limits - should raise error for values over 100
        with pytest.raises(ValidationError):
            validate_pagination_params(150, 0)  # Over max should raise error

        # Test errors
        with pytest.raises(ValidationError):
            validate_pagination_params(-1, 0)  # Negative limit

        with pytest.raises(ValidationError):
            validate_pagination_params(10, -1)  # Negative offset

        print("✅ Pagination validation works")
