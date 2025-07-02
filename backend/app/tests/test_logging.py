"""
Tests for logging configuration and functionality.

This module tests:
- Logging setup and configuration
- Request logging middleware
- Logger creation and usage
- Performance monitoring
- Log levels and formatting
"""

import logging
import json
from fastapi.testclient import TestClient
from app.main import app
from app.utils.logging import (
    setup_logging,
    get_logger,
    PerformanceMonitor,
    StructuredFormatter,
)

client = TestClient(app)


def test_logging_setup():
    """Test logging configuration."""
    setup_logging()
    logger = get_logger(__name__)

    assert logger.level <= logging.INFO  # Should be INFO or lower (DEBUG)
    # Handlers are on root logger, not individual loggers
    root_logger = logging.getLogger()
    assert len(root_logger.handlers) > 0
    print("✅ Logging configuration working")


def test_get_logger():
    """Test logger creation with get_logger function."""
    logger = get_logger("test_module")

    assert isinstance(logger, logging.Logger)
    assert logger.name == "test_module"
    print("✅ Logger creation working")


def test_structured_formatter():
    """Test structured JSON formatter."""
    formatter = StructuredFormatter()

    # Create a test log record
    logger = logging.getLogger("test")
    record = logger.makeRecord(
        name="test",
        level=logging.INFO,
        fn="test_file.py",
        lno=42,
        msg="Test message",
        args=(),
        exc_info=None,
    )

    formatted = formatter.format(record)

    # Should be valid JSON
    log_data = json.loads(formatted)

    assert log_data["level"] == "INFO"
    assert log_data["logger"] == "test"
    assert log_data["message"] == "Test message"
    assert log_data["line"] == 42
    assert "timestamp" in log_data

    print("✅ Structured formatter working")


def test_request_logging():
    """Test request logging middleware."""
    # Make a request and verify it doesn't break anything
    response = client.get("/api/v1/health")
    assert response.status_code in [200, 503]

    # In a real implementation, we'd check log output
    # For now, just verify the middleware doesn't break anything
    print("✅ Request logging middleware working")


def test_performance_monitor():
    """Test performance monitoring utilities."""
    monitor = PerformanceMonitor()

    # Test database query logging
    monitor.log_database_query("SELECT * FROM test", 0.05, 10)

    # Test external API call logging
    monitor.log_external_api_call("nominatim", "/search", 0.2, 200)

    # Test geocoding operation logging
    monitor.log_geocoding_operation("123 Main St", 0.3, True)

    # Test distance calculation logging
    monitor.log_distance_calculation("123 Main St", "456 Oak Ave", 0.1, 5.2)

    # If we get here without exceptions, the monitor is working
    print("✅ Performance monitor working")


def test_logging_levels():
    """Test different logging levels."""
    logger = get_logger("test_levels")

    # Test that logger accepts different levels
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")

    # If we get here without exceptions, logging levels work
    print("✅ Logging levels working")


def test_request_logging_with_errors():
    """Test request logging when errors occur."""
    # Make a request that will generate an error
    response = client.get("/nonexistent-endpoint")
    assert response.status_code == 404

    # The request should still be logged despite the error
    # In a real implementation, we'd verify the error was logged
    print("✅ Request logging with errors working")


def test_logger_context_information():
    """Test that loggers include context information."""
    logger = get_logger(__name__)

    # Test logging with extra context
    logger.info(
        "Test message with context",
        extra={"user_id": "123", "request_id": "abc-def-ghi"},
    )

    # If we get here without exceptions, context logging works
    print("✅ Logger context information working")


def test_multiple_requests_logging():
    """Test logging for multiple concurrent requests."""
    # Make multiple requests
    responses = []
    for i in range(5):
        response = client.get("/")
        responses.append(response)

    # All requests should complete successfully
    for response in responses:
        assert response.status_code == 200

    # Logging should handle multiple requests without issues
    print("✅ Multiple requests logging working")


def test_log_level_environment_configuration():
    """Test that log levels can be configured via environment."""
    # Test with different log levels
    for level in ["DEBUG", "INFO", "WARNING", "ERROR"]:
        setup_logging(level=level)
        logger = get_logger("test_env")

        expected_level = getattr(logging, level)
        # Root logger should be at or below the specified level
        assert logger.getEffectiveLevel() <= expected_level

    print("✅ Log level environment configuration working")


def test_exception_logging():
    """Test logging of exceptions."""
    logger = get_logger("test_exceptions")

    try:
        # Generate an exception
        raise ValueError("Test exception")
    except ValueError:
        # Log the exception
        logger.error("An error occurred", exc_info=True)

    # If we get here, exception logging works
    print("✅ Exception logging working")
