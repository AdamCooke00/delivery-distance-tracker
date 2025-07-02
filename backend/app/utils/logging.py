"""
Logging and monitoring utilities for Delivery Distance Tracker API.

This module provides:
- Structured logging configuration
- Request/response logging middleware
- Performance monitoring utilities
- Environment-based log level configuration
"""

import logging
import time
import json
import os
from datetime import datetime
from typing import Optional
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add extra fields if present
        if hasattr(record, "extra"):
            log_entry.update(record.extra)

        return json.dumps(log_entry, ensure_ascii=False)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses."""

    def __init__(self, app: ASGIApp, logger: Optional[logging.Logger] = None):
        super().__init__(app)
        self.logger = logger or get_logger("request")

    async def dispatch(self, request: Request, call_next):
        """Process request and log details."""
        start_time = time.time()

        # Add timestamp to request state for error handlers
        request.state.timestamp = datetime.utcnow().isoformat() + "Z"

        # Log incoming request
        request_log = {
            "event": "request_started",
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "user_agent": request.headers.get("user-agent"),
            "client_ip": self._get_client_ip(request),
            "request_id": id(request),  # Simple request ID
        }

        self.logger.info("HTTP request started", extra=request_log)

        # Process request
        try:
            response = await call_next(request)
            duration = time.time() - start_time

            # Log response
            response_log = {
                "event": "request_completed",
                "method": request.method,
                "url": str(request.url),
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration * 1000, 2),
                "request_id": id(request),
            }

            # Log at different levels based on status code
            if response.status_code >= 500:
                self.logger.error(
                    "HTTP request completed with server error", extra=response_log
                )
            elif response.status_code >= 400:
                self.logger.warning(
                    "HTTP request completed with client error", extra=response_log
                )
            else:
                self.logger.info(
                    "HTTP request completed successfully", extra=response_log
                )

            return response

        except Exception as e:
            duration = time.time() - start_time

            error_log = {
                "event": "request_failed",
                "method": request.method,
                "url": str(request.url),
                "path": request.url.path,
                "duration_ms": round(duration * 1000, 2),
                "error": str(e),
                "request_id": id(request),
            }

            self.logger.error("HTTP request failed with exception", extra=error_log)
            raise

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address from request."""
        # Check for forwarded headers (behind proxy)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        # Fallback to direct client IP
        if request.client:
            return request.client.host

        return "unknown"


def setup_logging(level: Optional[str] = None) -> None:
    """
    Set up logging configuration for the application.

    Args:
        level: Log level override (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Get log level from environment or parameter
    log_level = level or os.getenv("LOG_LEVEL", "INFO").upper()

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level, logging.INFO))

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create console handler with structured formatter
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level, logging.INFO))

    # Use structured formatter for production, simple for development
    if os.getenv("ENVIRONMENT", "development") == "production":
        formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Set levels for third-party loggers
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    logging.info(f"Logging configured with level: {log_level}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.

    Args:
        name: Logger name (typically __name__)

    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name)


class PerformanceMonitor:
    """Utility class for performance monitoring."""

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or get_logger("performance")

    def log_database_query(self, query: str, duration: float, result_count: int = 0):
        """Log database query performance."""
        self.logger.info(
            "Database query executed",
            extra={
                "event": "database_query",
                "query": query[:100] + "..." if len(query) > 100 else query,
                "duration_ms": round(duration * 1000, 2),
                "result_count": result_count,
            },
        )

    def log_external_api_call(
        self, service: str, endpoint: str, duration: float, status_code: int
    ):
        """Log external API call performance."""
        self.logger.info(
            "External API call completed",
            extra={
                "event": "external_api_call",
                "service": service,
                "endpoint": endpoint,
                "duration_ms": round(duration * 1000, 2),
                "status_code": status_code,
            },
        )

    def log_geocoding_operation(self, address: str, duration: float, success: bool):
        """Log geocoding operation performance."""
        self.logger.info(
            "Geocoding operation completed",
            extra={
                "event": "geocoding_operation",
                "address": address[:50] + "..." if len(address) > 50 else address,
                "duration_ms": round(duration * 1000, 2),
                "success": success,
            },
        )

    def log_distance_calculation(
        self, source: str, destination: str, duration: float, distance_km: float
    ):
        """Log distance calculation performance."""
        self.logger.info(
            "Distance calculation completed",
            extra={
                "event": "distance_calculation",
                "source": source[:50] + "..." if len(source) > 50 else source,
                "destination": (
                    destination[:50] + "..." if len(destination) > 50 else destination
                ),
                "duration_ms": round(duration * 1000, 2),
                "distance_km": distance_km,
            },
        )


# Global performance monitor instance
performance_monitor = PerformanceMonitor()
