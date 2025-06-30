"""
Health check endpoints for Delivery Distance Tracker API.

This module provides comprehensive health check functionality including:
- Database connectivity testing
- External API (Nominatim) connectivity testing
- System status reporting
"""

import time
import httpx
from datetime import datetime
from typing import Dict, Union
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.utils.database import check_database_health
from app.utils.logging import get_logger

logger = get_logger(__name__)

# Create health router
health_router = APIRouter()


class HealthCheck(BaseModel):
    """Health check response model."""

    status: str
    timestamp: datetime
    checks: Dict[str, Dict[str, Union[str, int, float]]]


class ServiceCheck(BaseModel):
    """Individual service check model."""

    status: str
    response_time_ms: float
    message: str = ""


async def check_nominatim_api() -> ServiceCheck:
    """
    Check Nominatim API connectivity.

    Returns:
        ServiceCheck: Status of the Nominatim API connectivity
    """
    start_time = time.time()

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Test with a simple geocoding request
            response = await client.get(
                "https://nominatim.openstreetmap.org/search",
                params={"q": "New York City", "format": "json", "limit": 1},
            )

        response_time = (time.time() - start_time) * 1000

        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                return ServiceCheck(
                    status="healthy",
                    response_time_ms=round(response_time, 2),
                    message="Nominatim API is accessible and responding correctly",
                )
            else:
                return ServiceCheck(
                    status="degraded",
                    response_time_ms=round(response_time, 2),
                    message="Nominatim API responded but returned no results",
                )
        else:
            return ServiceCheck(
                status="unhealthy",
                response_time_ms=round(response_time, 2),
                message=f"Nominatim API returned status code {response.status_code}",
            )

    except httpx.TimeoutException:
        response_time = (time.time() - start_time) * 1000
        return ServiceCheck(
            status="unhealthy",
            response_time_ms=round(response_time, 2),
            message="Nominatim API request timed out",
        )
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        logger.error(f"Error checking Nominatim API: {str(e)}")
        return ServiceCheck(
            status="unhealthy",
            response_time_ms=round(response_time, 2),
            message=f"Nominatim API check failed: {str(e)}",
        )


@health_router.get("/health", response_model=HealthCheck)
async def health_check():
    """
    Comprehensive health check endpoint.

    Checks:
    - Database connectivity
    - Nominatim API connectivity
    - Overall system status

    Returns:
        HealthCheck: Comprehensive health status of all services
    """
    logger.info("Health check requested")

    # Check database health
    db_healthy, db_message = check_database_health()
    db_check = {
        "status": "healthy" if db_healthy else "unhealthy",
        "response_time_ms": 0.0,  # Database check is synchronous for now
        "message": db_message,
    }

    # Check Nominatim API health
    nominatim_check = await check_nominatim_api()

    # Determine overall status
    checks = {
        "database": db_check,
        "nominatim_api": {
            "status": nominatim_check.status,
            "response_time_ms": nominatim_check.response_time_ms,
            "message": nominatim_check.message,
        },
    }

    # Overall status logic
    all_healthy = all(check["status"] == "healthy" for check in checks.values())

    any_degraded = any(check["status"] == "degraded" for check in checks.values())

    if all_healthy:
        overall_status = "healthy"
    elif any_degraded:
        overall_status = "degraded"
    else:
        overall_status = "unhealthy"

    health_response = HealthCheck(
        status=overall_status, timestamp=datetime.utcnow(), checks=checks
    )

    logger.info(f"Health check completed with status: {overall_status}")

    # Return appropriate HTTP status code
    if overall_status == "unhealthy":
        raise HTTPException(status_code=503, detail=health_response.dict())

    return health_response


@health_router.get("/health/database")
async def database_health():
    """
    Database-specific health check endpoint.

    Returns:
        Dict: Database health status and details
    """
    is_healthy, message = check_database_health()

    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "message": message,
        "timestamp": datetime.utcnow(),
    }


@health_router.get("/health/nominatim")
async def nominatim_health():
    """
    Nominatim API-specific health check endpoint.

    Returns:
        ServiceCheck: Nominatim API health status and details
    """
    check_result = await check_nominatim_api()

    return {
        "status": check_result.status,
        "response_time_ms": check_result.response_time_ms,
        "message": check_result.message,
        "timestamp": datetime.utcnow(),
    }
