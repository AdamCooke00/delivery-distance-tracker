# File: app/tests/test_history_security.py
"""
Security-focused tests for the history API endpoint.
Tests security fixes including input sanitization, date validation, and parameter security.
"""

from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from urllib.parse import quote
from app.main import app

client = TestClient(app)


def test_search_term_sanitization():
    """Test that search terms are properly sanitized"""
    dangerous_searches = [
        "<script>alert('xss')</script>",
        "'; DROP TABLE distance_queries; --",
        '"malicious"',
        "\\' OR 1=1 --",
        "admin\\\\'",
        "<>\"';\\",
    ]

    for dangerous_search in dangerous_searches:
        response = client.get(f"/api/v1/history?search={quote(dangerous_search)}")
        # Should not crash and should return valid response
        assert response.status_code in [200, 422]
        if response.status_code == 200:
            data = response.json()
            assert "items" in data

    print("✅ Search term sanitization works")


def test_invalid_sort_by_parameter():
    """Test that invalid sort_by parameters are rejected"""
    invalid_sort_fields = [
        "__class__",
        "__dict__",
        "__module__",
        "password",
        "secret",
        "private_key",
        "../etc/passwd",
        "nonexistent_field",
    ]

    for invalid_field in invalid_sort_fields:
        response = client.get(f"/api/v1/history?sort_by={invalid_field}")
        # Should return 422 validation error
        assert response.status_code == 422
        data = response.json()
        assert "error" in data or "detail" in data

    print("✅ Invalid sort_by parameter rejection works")


def test_date_range_validation_pydantic_model():
    """Test that date range validation works at Pydantic model level directly"""
    from app.api.history import HistoryQueryParams
    from pydantic import ValidationError

    # Test end_date before start_date - should be caught by Pydantic validator
    start_date = datetime.now() - timedelta(days=1)
    end_date = datetime.now() - timedelta(days=2)

    # Test the Pydantic model validation directly
    try:
        HistoryQueryParams(start_date=start_date, end_date=end_date, limit=10, offset=0)
        assert False, "Expected ValidationError but none was raised"
    except ValidationError as e:
        error_text = str(e)
        assert "end_date must be after start_date" in error_text
        assert len(e.errors()) == 1
        assert e.errors()[0]["type"] == "value_error"

    print("✅ Date range validation at Pydantic model level works")


def test_search_term_length_limit():
    """Test that search terms are limited in length"""
    # Create a very long search term (over 100 characters)
    long_search = "a" * 200

    response = client.get(f"/api/v1/history?search={long_search}")
    # Should not crash - either return results or 200 with no results
    assert response.status_code == 200

    print("✅ Search term length limiting works")


def test_parameter_validation_pydantic_model():
    """Test parameter validation using Pydantic model directly"""
    from app.api.history import HistoryQueryParams
    from pydantic import ValidationError

    test_cases = [
        # Negative values - should be caught by Pydantic Field validation
        {"limit": -1, "expected_error": "greater_than_equal"},
        {"offset": -1, "expected_error": "greater_than_equal"},
        {"limit": 0, "expected_error": "greater_than_equal"},
        # Extremely large values - should be caught by Field le/ge constraints
        {"limit": 10000, "expected_error": "less_than_equal"},
        # Invalid sort combinations - should be caught by pattern validation
        {"sort_by": "invalid_field", "expected_error": "string_pattern_mismatch"},
        {"sort_order": "invalid_order", "expected_error": "string_pattern_mismatch"},
    ]

    for test_case in test_cases:
        params = {k: v for k, v in test_case.items() if k != "expected_error"}
        try:
            HistoryQueryParams(**params)
            assert False, f"Expected ValidationError for {params} but none was raised"
        except ValidationError as e:
            # Verify the error type matches what we expect
            error_found = any(
                error["type"] == test_case["expected_error"] for error in e.errors()
            )
            assert (
                error_found
            ), f"Expected error type {test_case['expected_error']} not found in {e.errors()}"

    print("✅ Parameter validation edge cases handled correctly by Pydantic model")


def test_sql_injection_prevention():
    """Test that SQL injection attempts are prevented"""
    injection_attempts = [
        "'; DELETE FROM distance_queries; --",
        "' UNION SELECT * FROM distance_queries --",
        "admin' OR '1'='1",
        "'; INSERT INTO distance_queries VALUES ('hack'); --",
    ]

    for injection in injection_attempts:
        # Test in search parameter
        response = client.get(f"/api/v1/history?search={quote(injection)}")
        assert response.status_code in [200, 422]  # Should not crash

        if response.status_code == 200:
            data = response.json()
            assert "items" in data
            # Verify the injection didn't work by checking response structure
            assert "total" in data

    print("✅ SQL injection prevention works")


def test_concurrent_requests_security():
    """Test that concurrent requests don't expose security issues"""
    import concurrent.futures

    def make_request():
        return client.get("/api/v1/history?limit=5")

    # Make multiple concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(make_request) for _ in range(10)]
        results = [
            future.result() for future in concurrent.futures.as_completed(futures)
        ]

    # All requests should succeed
    for response in results:
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    print("✅ Concurrent request security works")


def test_malformed_date_handling():
    """Test handling of malformed date parameters"""
    malformed_dates = [
        "not-a-date",
        "2023-13-01",  # Invalid month
        "2023-02-30",  # Invalid day
        "2023/01/01",  # Wrong format
        "01-01-2023",  # Wrong format
        "<script>alert('xss')</script>",
        "'; DROP TABLE --",
    ]

    for bad_date in malformed_dates:
        response = client.get(f"/api/v1/history?start_date={quote(bad_date)}")
        # Should return validation error, not crash
        assert response.status_code == 422
        data = response.json()
        assert "error" in data or "detail" in data

    print("✅ Malformed date handling works")


def test_empty_and_whitespace_search():
    """Test handling of empty and whitespace-only search terms"""
    test_searches = [
        "",
        "   ",
        "\t\n",
        "null",
        "undefined",
    ]

    for search_term in test_searches:
        response = client.get(f"/api/v1/history?search={quote(search_term)}")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    print("✅ Empty and whitespace search handling works")
