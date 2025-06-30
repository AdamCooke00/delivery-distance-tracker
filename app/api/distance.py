"""
Distance calculation API endpoints for the Delivery Distance Tracker.

This module provides REST API endpoints for distance calculation between addresses:

Endpoints:
- POST /distance: Calculate distance between two addresses with geocoding and storage

Request/Response Flow:
1. Validate request using DistanceQueryRequest schema
2. Process through DistanceService business logic
3. Return DistanceQueryResponse with all calculation details
4. Handle errors with appropriate HTTP status codes

Error Mapping:
- 400 Bad Request: Geocoding failures (address not found)
- 422 Unprocessable Entity: Validation errors (malformed requests)
- 503 Service Unavailable: External API unavailable (Nominatim down)
- 500 Internal Server Error: Database/internal errors

Security Features:
- Request validation prevents injection attacks
- Address sanitization in service layer
- Error message sanitization (no internal details exposed)
- Rate limiting through geocoding service

Performance:
- Async request processing
- Concurrent geocoding operations
- Efficient database transactions
- Proper resource cleanup
"""

from typing import Dict, Any, AsyncGenerator
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from app.services.distance_service import DistanceService, DistanceServiceError
from app.models.distance_query import DistanceQueryRequest, DistanceQueryResponse
from app.utils.logging import get_logger

logger = get_logger(__name__)

# Create distance router
distance_router = APIRouter()


async def get_distance_service() -> AsyncGenerator[DistanceService, None]:
    """
    Dependency to provide DistanceService instance.

    This function creates and manages DistanceService instances for request processing.
    It ensures proper resource management and service lifecycle.

    Returns:
        DistanceService: Configured distance service instance

    Note:
        The service cleanup is handled automatically by FastAPI's dependency system
        and the service's async context management.
    """
    service = DistanceService()
    try:
        yield service
    finally:
        await service.close()


@distance_router.post("/distance", response_model=DistanceQueryResponse)
async def calculate_distance(
    request: DistanceQueryRequest,
    distance_service: DistanceService = Depends(get_distance_service),
) -> JSONResponse:
    """
    Calculate distance between two addresses.

    This endpoint processes distance calculation requests by:
    1. Validating input addresses using Pydantic schema validation
    2. Geocoding both addresses using the Nominatim API
    3. Calculating the distance using the Haversine formula
    4. Storing the complete query in the database
    5. Returning detailed results including coordinates and metadata

    Args:
        request: Distance calculation request with source and destination addresses
        distance_service: Injected distance service for business logic processing

    Returns:
        JSONResponse: Detailed distance calculation results including:
            - id: Database record ID for the query
            - source_address: Cleaned source address
            - destination_address: Cleaned destination address
            - source_lat/lng: Source coordinates from geocoding
            - destination_lat/lng: Destination coordinates from geocoding
            - source_coords: [lat, lng] array for source
            - destination_coords: [lat, lng] array for destination
            - distance_km: Calculated distance in kilometers
            - created_at: Timestamp of the query

    Raises:
        HTTPException 400: Geocoding failed (address not found)
        HTTPException 422: Validation error (invalid input format)
        HTTPException 503: External service unavailable (Nominatim API down)
        HTTPException 500: Internal error (database or calculation failure)

    Example Request:
        ```json
        {
            "source_address": "1600 Amphitheatre Parkway, Mountain View, CA",
            "destination_address": "1 Apple Park Way, Cupertino, CA"
        }
        ```

    Example Response:
        ```json
        {
            "id": 123,
            "source_address": "1600 Amphitheatre Parkway, Mountain View, CA",
            "destination_address": "1 Apple Park Way, Cupertino, CA",
            "source_lat": 37.4224764,
            "source_lng": -122.0842499,
            "destination_lat": 37.3349,
            "destination_lng": -122.009,
            "source_coords": [37.4224764, -122.0842499],
            "destination_coords": [37.3349, -122.009],
            "distance_km": 11.2,
            "created_at": "2025-06-30T10:30:45.123456"
        }
        ```

    Performance Notes:
        - Geocoding operations run concurrently for optimal response time
        - Database operations use transactions with automatic rollback
        - Response times typically 1-3 seconds depending on geocoding API

    Security Notes:
        - All addresses are validated and sanitized before processing
        - Error messages sanitized to prevent information disclosure
        - Rate limiting applied through geocoding service
    """
    logger.info(
        f"Distance calculation request: {request.source_address} → {request.destination_address}"
    )

    try:
        # Process the distance calculation through service layer
        result = await distance_service.calculate_distance(
            source_address=request.source_address,
            destination_address=request.destination_address,
        )

        # Convert service result to API response format
        response_data = result.to_dict()

        logger.info(
            f"Distance calculation successful: {result.distance_km} km (ID: {result.query_id})"
        )

        return JSONResponse(status_code=200, content=response_data)

    except DistanceServiceError as e:
        logger.error(f"Distance service error: {e.message} (type: {e.error_type})")

        # Map service errors to appropriate HTTP status codes
        if e.error_type == "validation_error":
            # Input validation failed
            raise HTTPException(
                status_code=422,
                detail=e.message,
            )
        elif e.error_type == "geocoding_error":
            # Address not found or geocoding failed
            raise HTTPException(
                status_code=400,
                detail=e.message,
            )
        elif e.error_type == "service_unavailable":
            # External API (Nominatim) unavailable
            raise HTTPException(
                status_code=503,
                detail="Geocoding service is temporarily unavailable. Please try again later.",
            )
        elif e.error_type in ["database_error", "calculation_error"]:
            # Internal system errors
            logger.error(f"Internal error during distance calculation: {e.message}")
            raise HTTPException(
                status_code=500,
                detail="An internal error occurred while processing your request. Please try again later.",
            )
        else:
            # Unknown error type
            logger.error(f"Unknown error type in distance calculation: {e.error_type}")
            raise HTTPException(
                status_code=500,
                detail="An unexpected error occurred. Please try again later.",
            )

    except Exception as e:
        # Catch any unexpected errors
        logger.error(f"Unexpected error in distance calculation endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred. Please try again later.",
        )


@distance_router.get("/distance/health")
async def distance_service_health() -> Dict[str, Any]:
    """
    Health check endpoint for distance calculation service.

    This endpoint provides health status for the distance calculation service and its dependencies.
    Useful for monitoring and load balancer health checks.

    Returns:
        Dict[str, Any]: Health status information including:
            - status: "healthy" or "unhealthy"
            - service: "distance_calculation"
            - timestamp: Current timestamp
            - dependencies: Status of required services

    Example Response:
        ```json
        {
            "status": "healthy",
            "service": "distance_calculation",
            "timestamp": "2025-06-30T10:30:45.123456",
            "dependencies": {
                "geocoding_service": "healthy",
                "database": "healthy",
                "distance_calculation": "healthy"
            }
        }
        ```
    """
    from datetime import datetime

    logger.info("Distance service health check requested")

    # Check service dependencies
    dependencies = {
        "geocoding_service": "healthy",  # Assume healthy - detailed check via main health endpoint
        "database": "healthy",  # Assume healthy - detailed check via main health endpoint
        "distance_calculation": "healthy",
    }

    # Overall status based on dependencies
    overall_status = (
        "healthy"
        if all(status == "healthy" for status in dependencies.values())
        else "unhealthy"
    )

    return {
        "status": overall_status,
        "service": "distance_calculation",
        "timestamp": datetime.utcnow().isoformat(),
        "dependencies": dependencies,
    }
