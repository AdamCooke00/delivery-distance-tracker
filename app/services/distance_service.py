"""
Distance calculation service for the Delivery Distance Tracker.

This module provides the core business logic for processing distance calculation requests:

Service Flow:
1. Validate input addresses using Sprint 4 validation utilities
2. Geocode both source and destination addresses using GeocodingService
3. Calculate distance between coordinates using Haversine formula
4. Store the complete query record in the database
5. Return structured response with all geocoding and calculation results

Error Handling:
- Graceful handling of geocoding failures (partial or complete)
- Database transaction rollback on any failures
- Detailed error messaging for client troubleshooting
- Proper exception mapping to HTTP status codes

Performance Considerations:
- Async operations for geocoding API calls
- Efficient database transactions with proper session management
- Connection pooling through SQLAlchemy session handling
- Rate limiting respect for external APIs

Security Features:
- Address sanitization before processing
- Input validation to prevent injection attacks
- No sensitive data in logs or error messages
- Proper database parameterization
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from decimal import Decimal

from sqlalchemy.exc import SQLAlchemyError

from app.services.geocoding import GeocodingService, GeocodingError, GeocodingResult
from app.utils.distance import haversine_distance
from app.utils.validation import validate_address, sanitize_address
from app.models.distance_query import DistanceQuery, DistanceQueryCreate
from app.models.database import SessionLocal
from app.utils.logging import get_logger

logger = get_logger(__name__)


class DistanceServiceError(Exception):
    """Base exception for distance service errors."""

    def __init__(
        self,
        message: str,
        error_type: str = "unknown",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_type = error_type
        self.details = details or {}


class DistanceCalculationResult:
    """Container for distance calculation results."""

    def __init__(
        self,
        source_address: str,
        destination_address: str,
        source_geocoding: Optional[GeocodingResult],
        destination_geocoding: Optional[GeocodingResult],
        distance_km: Optional[float],
        query_id: Optional[int] = None,
        created_at: Optional[datetime] = None,
    ):
        self.source_address = source_address
        self.destination_address = destination_address
        self.source_geocoding = source_geocoding
        self.destination_geocoding = destination_geocoding
        self.distance_km = distance_km
        self.query_id = query_id
        self.created_at = created_at or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for API response."""
        result = {
            "id": self.query_id,
            "source_address": self.source_address,
            "destination_address": self.destination_address,
            "distance_km": self.distance_km,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

        if self.source_geocoding:
            result["source_coords"] = [
                self.source_geocoding.latitude,
                self.source_geocoding.longitude,
            ]
            result["source_lat"] = self.source_geocoding.latitude
            result["source_lng"] = self.source_geocoding.longitude
        else:
            result["source_coords"] = None
            result["source_lat"] = None
            result["source_lng"] = None

        if self.destination_geocoding:
            result["destination_coords"] = [
                self.destination_geocoding.latitude,
                self.destination_geocoding.longitude,
            ]
            result["destination_lat"] = self.destination_geocoding.latitude
            result["destination_lng"] = self.destination_geocoding.longitude
        else:
            result["destination_coords"] = None
            result["destination_lat"] = None
            result["destination_lng"] = None

        return result


class DistanceService:
    """Service for processing distance calculation requests."""

    def __init__(self, geocoding_service: Optional[GeocodingService] = None):
        """
        Initialize distance service.

        Args:
            geocoding_service: Optional geocoding service instance. If None, creates a new one.
        """
        self.geocoding_service = geocoding_service or GeocodingService()

    async def calculate_distance(
        self, source_address: str, destination_address: str
    ) -> DistanceCalculationResult:
        """
        Calculate distance between two addresses with full processing pipeline.

        This method orchestrates the complete distance calculation workflow:
        1. Validates and sanitizes input addresses
        2. Geocodes both addresses concurrently
        3. Calculates distance using Haversine formula
        4. Stores the query in the database
        5. Returns comprehensive results

        Args:
            source_address: Starting location address
            destination_address: Ending location address

        Returns:
            DistanceCalculationResult: Complete calculation results with database ID

        Raises:
            DistanceServiceError: For validation errors, geocoding failures, or database issues

        Example:
            >>> service = DistanceService()
            >>> result = await service.calculate_distance(
            ...     "1600 Amphitheatre Parkway, Mountain View, CA",
            ...     "1 Apple Park Way, Cupertino, CA"
            ... )
            >>> print(f"Distance: {result.distance_km} km")
            >>> print(f"Database ID: {result.query_id}")
        """
        logger.info(
            f"Starting distance calculation: {source_address} → {destination_address}"
        )

        # Step 1: Validate and sanitize addresses
        try:
            if not validate_address(source_address):
                raise DistanceServiceError(
                    "Source address is invalid or empty",
                    error_type="validation_error",
                    details={"field": "source_address", "value": source_address},
                )

            if not validate_address(destination_address):
                raise DistanceServiceError(
                    "Destination address is invalid or empty",
                    error_type="validation_error",
                    details={
                        "field": "destination_address",
                        "value": destination_address,
                    },
                )

            clean_source = sanitize_address(source_address)
            clean_destination = sanitize_address(destination_address)

        except Exception as e:
            logger.error(f"Address validation failed: {str(e)}")
            raise DistanceServiceError(
                f"Address validation failed: {str(e)}", error_type="validation_error"
            )

        # Step 2: Geocode both addresses concurrently
        source_geocoding = None
        destination_geocoding = None

        try:
            logger.info("Starting geocoding for both addresses")

            # Use asyncio.gather for concurrent geocoding
            geocoding_results = await asyncio.gather(
                self.geocoding_service.geocode_address(clean_source),
                self.geocoding_service.geocode_address(clean_destination),
                return_exceptions=True,
            )

            source_result, destination_result = geocoding_results

            # Check source geocoding result
            if isinstance(source_result, Exception):
                logger.error(f"Source geocoding failed: {str(source_result)}")
                # Sanitize error message based on error type
                error_msg = str(source_result).lower()
                if any(
                    keyword in error_msg
                    for keyword in [
                        "password",
                        "postgresql://",
                        "timeout",
                        "timed out",
                        "connection",
                        "unavailable",
                        "rate limit",
                        "initialize",
                        "failed to",
                        "unexpected",
                    ]
                ):
                    sanitized_message = "Geocoding service is temporarily unavailable"
                    error_type = "service_unavailable"
                else:
                    sanitized_message = f"Failed to geocode source address '{clean_source}': address not found"
                    error_type = "geocoding_error"
                raise DistanceServiceError(
                    sanitized_message,
                    error_type=error_type,
                    details={"address": clean_source, "field": "source"},
                )
            source_geocoding = source_result

            # Check destination geocoding result
            if isinstance(destination_result, Exception):
                logger.error(f"Destination geocoding failed: {str(destination_result)}")
                # Sanitize error message based on error type
                error_msg = str(destination_result).lower()
                if any(
                    keyword in error_msg
                    for keyword in [
                        "password",
                        "postgresql://",
                        "timeout",
                        "timed out",
                        "connection",
                        "unavailable",
                        "rate limit",
                        "initialize",
                        "failed to",
                        "unexpected",
                    ]
                ):
                    sanitized_message = "Geocoding service is temporarily unavailable"
                    error_type = "service_unavailable"
                else:
                    sanitized_message = f"Failed to geocode destination address '{clean_destination}': address not found"
                    error_type = "geocoding_error"
                raise DistanceServiceError(
                    sanitized_message,
                    error_type=error_type,
                    details={"address": clean_destination, "field": "destination"},
                )
            destination_geocoding = destination_result

            logger.info(
                f"Geocoding successful: {source_geocoding.latitude},{source_geocoding.longitude} → {destination_geocoding.latitude},{destination_geocoding.longitude}"
            )

        except DistanceServiceError:
            raise  # Re-raise our own errors
        except GeocodingError as e:
            logger.error(f"Geocoding service error: {str(e)}")
            # Sanitize error message to prevent sensitive information exposure
            sanitized_message = "Geocoding service is temporarily unavailable"
            raise DistanceServiceError(
                sanitized_message,
                error_type="service_unavailable",
            )
        except Exception as e:
            logger.error(f"Unexpected geocoding error: {str(e)}")
            # Sanitize error message to prevent sensitive information exposure
            sanitized_message = "Geocoding service is temporarily unavailable"
            raise DistanceServiceError(
                sanitized_message,
                error_type="service_unavailable",
            )

        # Step 3: Calculate distance using Haversine formula
        try:
            distance_km = haversine_distance(
                source_geocoding.latitude,
                source_geocoding.longitude,
                destination_geocoding.latitude,
                destination_geocoding.longitude,
            )

            logger.info(f"Distance calculated: {distance_km} km")

        except Exception as e:
            logger.error(f"Distance calculation failed: {str(e)}")
            raise DistanceServiceError(
                f"Distance calculation failed: {str(e)}", error_type="calculation_error"
            )

        # Step 4: Store query in database
        query_id = None
        db_session = None

        try:
            db_session = SessionLocal()

            # Create database record
            query_data = DistanceQueryCreate(
                source_address=clean_source,
                destination_address=clean_destination,
                source_lat=source_geocoding.latitude,
                source_lng=source_geocoding.longitude,
                destination_lat=destination_geocoding.latitude,
                destination_lng=destination_geocoding.longitude,
                distance_km=distance_km,
            )

            db_query = DistanceQuery(
                source_address=query_data.source_address,
                destination_address=query_data.destination_address,
                source_lat=Decimal(str(query_data.source_lat)),
                source_lng=Decimal(str(query_data.source_lng)),
                destination_lat=Decimal(str(query_data.destination_lat)),
                destination_lng=Decimal(str(query_data.destination_lng)),
                distance_km=Decimal(str(query_data.distance_km)),
            )

            db_session.add(db_query)
            db_session.commit()
            db_session.refresh(db_query)

            query_id = db_query.id
            created_at = db_query.created_at

            logger.info(f"Distance query stored in database with ID: {query_id}")

        except SQLAlchemyError as e:
            logger.error(f"Database error during storage: {str(e)}")
            if db_session:
                db_session.rollback()
            # Sanitize error message to prevent sensitive information exposure
            sanitized_message = "Database storage temporarily unavailable"
            raise DistanceServiceError(
                sanitized_message,
                error_type="database_error",
            )
        except Exception as e:
            logger.error(f"Unexpected database error: {str(e)}")
            if db_session:
                db_session.rollback()
            # Sanitize error message to prevent sensitive information exposure
            sanitized_message = "Database storage temporarily unavailable"
            raise DistanceServiceError(
                sanitized_message,
                error_type="database_error",
            )
        finally:
            if db_session:
                db_session.close()

        # Step 5: Return comprehensive results
        result = DistanceCalculationResult(
            source_address=clean_source,
            destination_address=clean_destination,
            source_geocoding=source_geocoding,
            destination_geocoding=destination_geocoding,
            distance_km=distance_km,
            query_id=query_id,
            created_at=created_at,
        )

        logger.info(
            f"Distance calculation completed successfully: {distance_km} km (ID: {query_id})"
        )
        return result

    async def close(self):
        """Close the geocoding service and clean up resources."""
        if self.geocoding_service:
            await self.geocoding_service.close()
