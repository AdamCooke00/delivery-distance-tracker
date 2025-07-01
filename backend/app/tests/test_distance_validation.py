"""
Test cases for distance endpoint request validation.

This module tests input validation, malicious input handling, and request
format validation for the POST /distance endpoint.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestDistanceValidationErrors:
    """Test request validation and error handling."""

    def test_missing_source_address(self):
        """Test validation error when source address is missing"""
        request_data = {"destination_address": "123 Main St, City, State"}

        response = client.post("/api/v1/distance", json=request_data)
        assert response.status_code == 422

        data = response.json()
        assert "details" in data and "validation_errors" in data["details"]

        # Check that the error mentions the missing source field
        error_details = str(data["details"]["validation_errors"])
        assert (
            "source" in error_details.lower()
            or "source_address" in error_details.lower()
        )

        print("✅ Missing source address validation works")

    def test_missing_destination_address(self):
        """Test validation error when destination address is missing"""
        request_data = {"source_address": "123 Main St, City, State"}

        response = client.post("/api/v1/distance", json=request_data)
        assert response.status_code == 422

        data = response.json()
        assert "details" in data and "validation_errors" in data["details"]

        # Check that the error mentions the missing destination field
        error_details = str(data["details"]["validation_errors"])
        assert (
            "destination" in error_details.lower()
            or "destination_address" in error_details.lower()
        )

        print("✅ Missing destination address validation works")

    def test_both_addresses_missing(self):
        """Test validation error when both addresses are missing"""
        request_data = {}

        response = client.post("/api/v1/distance", json=request_data)
        assert response.status_code == 422

        data = response.json()
        assert "details" in data and "validation_errors" in data["details"]

        # Should have errors for both fields
        error_details = str(data["details"]["validation_errors"])
        assert (
            "source" in error_details.lower()
            or "source_address" in error_details.lower()
        ) and (
            "destination" in error_details.lower()
            or "destination_address" in error_details.lower()
        )

        print("✅ Both addresses missing validation works")

    def test_empty_source_address(self):
        """Test validation error for empty source address"""
        request_data = {
            "source_address": "",
            "destination_address": "123 Main St, City, State",
        }

        response = client.post("/api/v1/distance", json=request_data)
        assert response.status_code == 422

        data = response.json()
        assert "details" in data and "validation_errors" in data["details"]

        print("✅ Empty source address validation works")

    def test_empty_destination_address(self):
        """Test validation error for empty destination address"""
        request_data = {
            "source_address": "123 Main St, City, State",
            "destination_address": "",
        }

        response = client.post("/api/v1/distance", json=request_data)
        assert response.status_code == 422

        data = response.json()
        assert "details" in data and "validation_errors" in data["details"]

        print("✅ Empty destination address validation works")

    def test_whitespace_only_addresses(self):
        """Test validation error for whitespace-only addresses"""
        whitespace_variations = [
            "   ",  # spaces
            "\t\t",  # tabs
            "\n\n",  # newlines
            " \t\n ",  # mixed whitespace
        ]

        for whitespace_addr in whitespace_variations:
            request_data = {
                "source_address": whitespace_addr,
                "destination_address": "123 Main St",
            }

            response = client.post("/api/v1/distance", json=request_data)
            assert response.status_code == 422

            # Test reverse (whitespace destination)
            request_data = {
                "source_address": "123 Main St",
                "destination_address": whitespace_addr,
            }

            response = client.post("/api/v1/distance", json=request_data)
            assert response.status_code == 422

        print("✅ Whitespace-only address validation works")

    def test_invalid_json_format(self):
        """Test error handling for invalid JSON"""
        # Test with completely invalid JSON
        response = client.post(
            "/api/v1/distance",
            data="invalid json string",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 422

        # Test with malformed JSON
        response = client.post(
            "/api/v1/distance",
            data='{"source_address": "test", "destination_address":}',  # Missing value
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 422

        print("✅ Invalid JSON handling works")

    def test_wrong_content_type(self):
        """Test error handling for wrong content type"""
        # Test with form data instead of JSON
        response = client.post(
            "/api/v1/distance",
            data={
                "source_address": "123 Main St",
                "destination_address": "456 Oak Ave",
            },
        )
        assert response.status_code == 422

        print("✅ Wrong content type handling works")

    def test_extra_unexpected_fields(self):
        """Test handling of extra fields in request"""
        request_data = {
            "source_address": "123 Main St, City, State",
            "destination_address": "456 Oak Ave, City, State",
            "extra_field": "should be ignored",
            "another_field": 12345,
            "nested_field": {"key": "value"},
        }

        # This should succeed - Pydantic ignores extra fields by default
        # But we'll verify the extra fields don't cause issues
        response = client.post("/api/v1/distance", json=request_data)

        # Should either succeed (ignoring extra fields) or fail with validation error
        assert response.status_code in [
            200,
            400,
            422,
            503,
        ]  # Various acceptable responses

        print("✅ Extra fields handling works")


class TestDistanceSecurityValidation:
    """Test security-related validation and malicious input handling."""

    def test_xss_attempt_in_addresses(self):
        """Test handling of XSS attempts in address fields"""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
            "javascript:alert('xss')",
            "<iframe src='javascript:alert(\"xss\")'></iframe>",
            "' onmouseover='alert(\"xss\")'",
        ]

        for payload in xss_payloads:
            request_data = {
                "source_address": payload,
                "destination_address": "123 Main St, City, State",
            }

            response = client.post("/api/v1/distance", json=request_data)

            # Should either reject (422) or sanitize and process (200/400/503)
            assert response.status_code in [200, 400, 422, 503]

            if response.status_code == 200:
                # If processed, ensure XSS content was sanitized
                data = response.json()
                response_str = str(data).lower()
                assert "<script>" not in response_str
                assert "javascript:" not in response_str
                assert "onerror=" not in response_str
                assert "<iframe>" not in response_str

            # Test XSS in destination address
            request_data = {
                "source_address": "123 Main St, City, State",
                "destination_address": payload,
            }

            response = client.post("/api/v1/distance", json=request_data)
            assert response.status_code in [200, 400, 422, 503]

            if response.status_code == 200:
                data = response.json()
                response_str = str(data).lower()
                assert "<script>" not in response_str
                assert "javascript:" not in response_str

        print("✅ XSS attempt handling works")

    def test_sql_injection_attempt_in_addresses(self):
        """Test handling of SQL injection attempts in address fields"""
        sql_payloads = [
            "'; DROP TABLE users; --",
            "' OR '1'='1'; --",
            "'; DELETE FROM distance_queries; --",
            "' UNION SELECT * FROM users; --",
            "'; INSERT INTO users VALUES ('hacker', 'password'); --",
            "1'; EXEC xp_cmdshell('dir'); --",
        ]

        for payload in sql_payloads:
            request_data = {
                "source_address": payload,
                "destination_address": "123 Main St, City, State",
            }

            response = client.post("/api/v1/distance", json=request_data)

            # Should either reject (422) or sanitize and process
            assert response.status_code in [200, 400, 422, 503]

            if response.status_code == 200:
                # If processed, ensure SQL injection content was sanitized
                data = response.json()
                response_str = str(data).upper()
                assert "DROP TABLE" not in response_str
                assert "DELETE FROM" not in response_str
                assert "UNION SELECT" not in response_str
                assert "INSERT INTO" not in response_str
                assert "EXEC " not in response_str

            # Test SQL injection in destination address
            request_data = {
                "source_address": "123 Main St, City, State",
                "destination_address": payload,
            }

            response = client.post("/api/v1/distance", json=request_data)
            assert response.status_code in [200, 400, 422, 503]

        print("✅ SQL injection attempt handling works")

    def test_very_long_addresses(self):
        """Test handling of extremely long address strings"""
        # Test with addresses longer than typical limits
        long_address = "A" * 1000  # 1000 character address
        very_long_address = "B" * 10000  # 10000 character address

        for test_address in [long_address, very_long_address]:
            request_data = {
                "source_address": test_address,
                "destination_address": "123 Main St, City, State",
            }

            response = client.post("/api/v1/distance", json=request_data)

            # Should handle gracefully - either reject for length or process
            assert response.status_code in [200, 400, 422, 503]

            # Test very long destination
            request_data = {
                "source_address": "123 Main St, City, State",
                "destination_address": test_address,
            }

            response = client.post("/api/v1/distance", json=request_data)
            assert response.status_code in [200, 400, 422, 503]

        print("✅ Long address handling works")

    def test_unicode_and_special_characters(self):
        """Test handling of unicode and special characters in addresses"""
        unicode_addresses = [
            "北京市朝阳区",  # Chinese characters
            "Москва, Россия",  # Cyrillic characters
            "العنوان باللغة العربية",  # Arabic characters
            "🏠 123 Emoji Street 🌍",  # Emoji characters
            "Café René, Montréal, Québec",  # Accented characters
            "Straße 123, München, Deutschland",  # German umlauts
            "Ñuñoa, Santiago, Chile",  # Spanish ñ
        ]

        for address in unicode_addresses:
            request_data = {
                "source_address": address,
                "destination_address": "123 Main St, City, State",
            }

            response = client.post("/api/v1/distance", json=request_data)

            # Should handle gracefully - unicode should be supported
            assert response.status_code in [200, 400, 422, 503]

            if response.status_code == 200:
                # If successful, verify the unicode was preserved
                data = response.json()
                # The address might be cleaned/processed but should still contain key parts
                assert len(data["source_address"]) > 0

        print("✅ Unicode and special character handling works")

    def test_null_and_none_values(self):
        """Test handling of null/None values in request"""
        null_variations = [
            {"source_address": None, "destination_address": "123 Main St"},
            {"source_address": "123 Main St", "destination_address": None},
            {"source_address": None, "destination_address": None},
        ]

        for request_data in null_variations:
            response = client.post("/api/v1/distance", json=request_data)

            # Should reject null values with validation error
            assert response.status_code == 422

            data = response.json()
            assert "details" in data and "validation_errors" in data["details"]

        print("✅ Null value handling works")


class TestDistanceValidationEdgeCases:
    """Test edge cases in validation."""

    def test_numeric_addresses(self):
        """Test handling of purely numeric addresses"""
        numeric_addresses = [
            "123",
            "12345",
            "0",
            "-123",
            "123.456",
        ]

        for address in numeric_addresses:
            request_data = {
                "source_address": address,
                "destination_address": "123 Main St, City, State",
            }

            response = client.post("/api/v1/distance", json=request_data)

            # Numeric-only addresses should typically be rejected
            # But system might handle them - verify appropriate response
            assert response.status_code in [200, 400, 422, 503]

        print("✅ Numeric address handling works")

    def test_single_character_addresses(self):
        """Test handling of single character addresses"""
        single_chars = ["a", "A", "1", ".", " ", "!", "@"]

        for char in single_chars:
            request_data = {
                "source_address": char,
                "destination_address": "123 Main St, City, State",
            }

            response = client.post("/api/v1/distance", json=request_data)

            # Single characters should typically be rejected
            assert response.status_code in [400, 422]

        print("✅ Single character address handling works")

    def test_address_with_only_punctuation(self):
        """Test handling of addresses with only punctuation"""
        punctuation_addresses = [
            "!!!",
            "...",
            "???",
            "---",
            "___",
            "***",
            "+++",
            "===",
        ]

        for address in punctuation_addresses:
            request_data = {
                "source_address": address,
                "destination_address": "123 Main St, City, State",
            }

            response = client.post("/api/v1/distance", json=request_data)

            # Punctuation-only addresses should be rejected
            assert response.status_code in [400, 422]

        print("✅ Punctuation-only address handling works")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
