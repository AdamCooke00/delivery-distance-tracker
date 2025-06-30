"""Test database health check functionality."""

from app.utils.database import (
    check_database_health,
    initialize_database,
    test_database_operations,
)


def test_database_health_check():
    """Test database health check utility"""
    is_healthy, message = check_database_health()
    assert is_healthy is True
    assert "healthy" in message.lower()
    assert "delivery_tracker" in message
    assert "ms" in message  # Response time should be included
    print("✅ Database health check works")


def test_database_health_check_response_format():
    """Test health check returns proper format"""
    is_healthy, message = check_database_health()

    # Should return a tuple with boolean and string
    assert isinstance(is_healthy, bool)
    assert isinstance(message, str)
    assert len(message) > 0

    print("✅ Health check response format is correct")


def test_database_initialization():
    """Test database initialization function"""
    success, message = initialize_database()
    assert success is True
    assert "success" in message.lower()

    print("✅ Database initialization works")


def test_database_operations_crud():
    """Test comprehensive database CRUD operations"""
    success, message = test_database_operations()
    assert success is True
    assert "successful" in message.lower()

    print("✅ Database CRUD operations test passes")


def test_database_health_performance():
    """Test that health check completes within reasonable time"""
    import time

    start_time = time.time()
    is_healthy, message = check_database_health()
    end_time = time.time()

    response_time = (end_time - start_time) * 1000  # Convert to milliseconds

    assert is_healthy is True
    assert response_time < 5000  # Should complete within 5 seconds

    print(f"✅ Health check completed in {response_time:.2f}ms")


def test_database_connection_error_handling():
    """Test health check handles connection errors gracefully"""
    from app.utils.database import check_database_health
    import unittest.mock

    # Mock a database connection error
    with unittest.mock.patch("app.utils.database.engine") as mock_engine:
        mock_engine.connect.side_effect = Exception("Connection failed")

        is_healthy, message = check_database_health()
        assert is_healthy is False
        assert "error" in message.lower()
        assert "Connection failed" in message

    print("✅ Database error handling works correctly")
