"""
Custom exception classes and global error handlers for Delivery Distance Tracker API.

This module provides:
- Custom exception classes for different error types
- Global exception handlers for FastAPI
- Structured error response models
"""

from typing import Dict, Any, Optional
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


class ErrorResponse(BaseModel):
    """Standard error response model."""

    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: str


class DeliveryTrackerException(Exception):
    """Base exception class for Delivery Distance Tracker."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class DatabaseConnectionError(DeliveryTrackerException):
    """Raised when database connection fails."""

    pass


class GeocodingError(DeliveryTrackerException):
    """Raised when geocoding operation fails."""

    pass


class AddressValidationError(DeliveryTrackerException):
    """Raised when address validation fails."""

    pass


class DistanceCalculationError(DeliveryTrackerException):
    """Raised when distance calculation fails."""

    pass


class ExternalAPIError(DeliveryTrackerException):
    """Raised when external API calls fail."""

    pass


class RateLimitError(DeliveryTrackerException):
    """Raised when rate limits are exceeded."""

    pass


async def database_connection_error_handler(
    request: Request, exc: DatabaseConnectionError
):
    """Handle database connection errors."""
    logger.error(
        f"Database connection error: {exc.message}", extra={"details": exc.details}
    )

    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "error": "Database Connection Error",
            "message": "Unable to connect to the database. Please try again later.",
            "details": exc.details,
            "timestamp": (
                request.state.timestamp if hasattr(request.state, "timestamp") else None
            ),
        },
    )


async def geocoding_error_handler(request: Request, exc: GeocodingError):
    """Handle geocoding errors."""
    logger.error(f"Geocoding error: {exc.message}", extra={"details": exc.details})

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Geocoding Error",
            "message": exc.message,
            "details": exc.details,
            "timestamp": (
                request.state.timestamp if hasattr(request.state, "timestamp") else None
            ),
        },
    )


async def address_validation_error_handler(
    request: Request, exc: AddressValidationError
):
    """Handle address validation errors."""
    logger.warning(
        f"Address validation error: {exc.message}", extra={"details": exc.details}
    )

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Address Validation Error",
            "message": exc.message,
            "details": exc.details,
            "timestamp": (
                request.state.timestamp if hasattr(request.state, "timestamp") else None
            ),
        },
    )


async def distance_calculation_error_handler(
    request: Request, exc: DistanceCalculationError
):
    """Handle distance calculation errors."""
    logger.error(
        f"Distance calculation error: {exc.message}", extra={"details": exc.details}
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Distance Calculation Error",
            "message": exc.message,
            "details": exc.details,
            "timestamp": (
                request.state.timestamp if hasattr(request.state, "timestamp") else None
            ),
        },
    )


async def external_api_error_handler(request: Request, exc: ExternalAPIError):
    """Handle external API errors."""
    logger.error(f"External API error: {exc.message}", extra={"details": exc.details})

    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content={
            "error": "External API Error",
            "message": "External service is temporarily unavailable. Please try again later.",
            "details": exc.details,
            "timestamp": (
                request.state.timestamp if hasattr(request.state, "timestamp") else None
            ),
        },
    )


async def rate_limit_error_handler(request: Request, exc: RateLimitError):
    """Handle rate limit errors."""
    logger.warning(
        f"Rate limit exceeded: {exc.message}", extra={"details": exc.details}
    )

    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "error": "Rate Limit Exceeded",
            "message": exc.message,
            "details": exc.details,
            "timestamp": (
                request.state.timestamp if hasattr(request.state, "timestamp") else None
            ),
        },
    )


async def validation_error_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors."""
    logger.warning(f"Request validation error: {exc.errors()}")

    # Convert validation errors to JSON-serializable format
    serializable_errors = []
    for error in exc.errors():
        serializable_error = {}
        for key, value in error.items():
            try:
                # Test if value is JSON serializable
                import json

                json.dumps(value)
                serializable_error[key] = value
            except (TypeError, ValueError):
                # Convert non-serializable values to strings
                serializable_error[key] = str(value)
        serializable_errors.append(serializable_error)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "message": "Request validation failed",
            "details": {"validation_errors": serializable_errors},
            "timestamp": (
                request.state.timestamp if hasattr(request.state, "timestamp") else None
            ),
        },
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": f"HTTP {exc.status_code}",
            "message": exc.detail,
            "timestamp": (
                request.state.timestamp if hasattr(request.state, "timestamp") else None
            ),
        },
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please try again later.",
            "timestamp": (
                request.state.timestamp if hasattr(request.state, "timestamp") else None
            ),
        },
    )


# Exception handler mapping
EXCEPTION_HANDLERS = {
    DatabaseConnectionError: database_connection_error_handler,
    GeocodingError: geocoding_error_handler,
    AddressValidationError: address_validation_error_handler,
    DistanceCalculationError: distance_calculation_error_handler,
    ExternalAPIError: external_api_error_handler,
    RateLimitError: rate_limit_error_handler,
    RequestValidationError: validation_error_handler,
    HTTPException: http_exception_handler,
    Exception: general_exception_handler,
}
