"""
FastAPI application entry point for Delivery Distance Tracker.

This module creates and configures the FastAPI application with:
- CORS configuration for frontend integration
- OpenAPI documentation setup
- Application lifecycle event handlers
- Router inclusion for API endpoints
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api.routes import api_router
from app.utils.logging import setup_logging, get_logger, RequestLoggingMiddleware
from app.utils.exceptions import EXCEPTION_HANDLERS
from app.utils.config import config


logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    logger.info("Starting Delivery Distance Tracker API")
    setup_logging()
    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down Delivery Distance Tracker API")


# Create FastAPI application instance
app = FastAPI(
    title="Delivery Distance Tracker API",
    description="A REST API for calculating distances between delivery addresses",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Configure CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Add exception handlers
for exception_class, handler in EXCEPTION_HANDLERS.items():
    app.add_exception_handler(exception_class, handler)

# Include API router with versioning
app.include_router(api_router, prefix="/api/v1")


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint returning API information."""
    return {
        "message": "Delivery Distance Tracker API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
