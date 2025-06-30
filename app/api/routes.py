"""
Main API router configuration for Delivery Distance Tracker.

This module sets up the main API router and includes all sub-routers
for different API endpoints with proper organization and versioning.
"""

from fastapi import APIRouter

from .health import health_router

# Create main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(health_router, tags=["Health"])

# Future routers will be added here:
# api_router.include_router(distance_router, prefix="/distance", tags=["Distance"])
# api_router.include_router(history_router, prefix="/history", tags=["History"])
