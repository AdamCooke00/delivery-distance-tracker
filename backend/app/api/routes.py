"""
Main API router configuration for Delivery Distance Tracker.

This module sets up the main API router and includes all sub-routers
for different API endpoints with proper organization and versioning.
"""

from fastapi import APIRouter

from .health import health_router
from .distance import distance_router
from .history import router as history_router

# Create main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(health_router, tags=["Health"])
api_router.include_router(distance_router, tags=["Distance"])
api_router.include_router(history_router, tags=["History"])
