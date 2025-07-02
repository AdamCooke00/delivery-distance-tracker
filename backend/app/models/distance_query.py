"""
Distance query model and schemas for the Delivery Distance Tracker.

This module defines the core data models and validation schemas for distance calculations:

SQLAlchemy Model:
- DistanceQuery: Database table model for storing distance calculation results
- Indexes on addresses for query performance optimization
- Decimal precision for accurate coordinate and distance storage

Pydantic Schemas:
- DistanceQueryBase: Base schema with common fields and validation rules
- DistanceQueryCreate: Input schema for creating new distance queries
- DistanceQueryResponse: Output schema for API responses with computed fields

Field Validation Rules:
- Addresses: Must be non-empty strings between 1-255 characters
- Coordinates: Latitude (-90 to 90), Longitude (-180 to 180) with 8 decimal precision
- Distance: Non-negative decimal with 3 decimal places for meter precision

Database Schema:
```sql
CREATE TABLE distance_queries (
    id SERIAL PRIMARY KEY,
    source_address VARCHAR(255) NOT NULL,
    destination_address VARCHAR(255) NOT NULL,
    source_lat DECIMAL(10, 8),           -- 8 decimal places for GPS precision
    source_lng DECIMAL(11, 8),           -- 11 digits total for longitude range
    destination_lat DECIMAL(10, 8),
    destination_lng DECIMAL(11, 8),
    distance_km DECIMAL(10, 3)           -- 3 decimal places for meter precision
);

-- Performance indexes
CREATE INDEX idx_distance_queries_addresses ON distance_queries(source_address, destination_address);
```

Usage Examples:
    # Create a new distance query
    query_data = DistanceQueryCreate(
        source_address="123 Main St, City, State",
        destination_address="456 Oak Ave, City, State",
        source_lat=40.7128,
        source_lng=-74.0060,
        destination_lat=40.7589,
        destination_lng=-73.9851,
        distance_km=5.2
    )

    # Validation is automatic
    try:
        validated_data = query_data.model_validate(data)
    except ValidationError as e:
        print(f"Validation failed: {e}")

Performance Considerations:
- Decimal fields ensure precision for financial/scientific calculations
- Indexes optimize common query patterns (address-based)
- Coordinate validation prevents invalid GPS data storage
"""

from decimal import Decimal
from typing import Optional

from sqlalchemy import Column, Integer, String, Numeric
from pydantic import BaseModel, Field, field_validator

from .database import Base


class DistanceQuery(Base):
    """SQLAlchemy model for distance_queries table."""

    __tablename__ = "distance_queries"

    id = Column(Integer, primary_key=True, index=True)
    source_address = Column(String(255), nullable=False)
    destination_address = Column(String(255), nullable=False)
    source_lat = Column(Numeric(10, 8), nullable=True)
    source_lng = Column(Numeric(11, 8), nullable=True)
    destination_lat = Column(Numeric(10, 8), nullable=True)
    destination_lng = Column(Numeric(11, 8), nullable=True)
    distance_km = Column(Numeric(10, 3), nullable=True)


# Pydantic schemas for data validation and serialization


class DistanceQueryRequest(BaseModel):
    """Request schema for distance calculation."""

    source_address: str = Field(
        ..., min_length=1, max_length=255, description="Source address"
    )
    destination_address: str = Field(
        ..., min_length=1, max_length=255, description="Destination address"
    )

    @field_validator("source_address", "destination_address")
    @classmethod
    def validate_address(cls, v):
        """
        Validate address fields for proper format and content.

        Ensures addresses are non-empty strings with meaningful content.
        Automatically strips leading/trailing whitespace for consistent storage.

        Args:
            v (str): The address string to validate

        Returns:
            str: The validated and cleaned address string

        Raises:
            ValueError: If address is empty, None, or contains only whitespace

        Example:
            >>> # Valid addresses
            >>> "123 Main St, City, State"  # ✓ Full address
            >>> "Central Park"              # ✓ Landmark
            >>> "  456 Oak Ave  "           # ✓ Trimmed to "456 Oak Ave"

            >>> # Invalid addresses
            >>> ""                          # ✗ Empty string
            >>> "   "                       # ✗ Only whitespace
            >>> None                        # ✗ None value
        """
        if not v or not v.strip():
            raise ValueError("Address cannot be empty")
        return v.strip()


class DistanceQueryResponse(BaseModel):
    """Response schema for distance calculation."""

    id: int
    source_address: str
    destination_address: str
    source_lat: Optional[float] = None
    source_lng: Optional[float] = None
    destination_lat: Optional[float] = None
    destination_lng: Optional[float] = None
    distance_km: Optional[float] = None

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda d: float(d) if d is not None else None,
        }


class DistanceQueryCreate(BaseModel):
    """Schema for creating distance query records."""

    source_address: str
    destination_address: str
    source_lat: Optional[float] = None
    source_lng: Optional[float] = None
    destination_lat: Optional[float] = None
    destination_lng: Optional[float] = None
    distance_km: Optional[float] = None

    @field_validator("source_lat", "destination_lat")
    @classmethod
    def validate_latitude(cls, v):
        """
        Validate latitude coordinate values for GPS accuracy.

        Ensures latitude values fall within the valid geographic range.
        Latitude represents the north-south position on Earth's surface.

        Args:
            v (float | None): The latitude value to validate

        Returns:
            float | None: The validated latitude value, or None if input was None

        Raises:
            ValueError: If latitude is outside the valid range (-90 to 90 degrees)

        Geographic Reference:
            - -90°: South Pole (southernmost point on Earth)
            -   0°: Equator (dividing line between hemispheres)
            - +90°: North Pole (northernmost point on Earth)

        Example:
            >>> # Valid latitudes
            >>> 40.7128    # ✓ New York City
            >>> -33.8688   # ✓ Sydney, Australia
            >>> 0.0        # ✓ Equator
            >>> 89.9999    # ✓ Near North Pole

            >>> # Invalid latitudes
            >>> 91.0       # ✗ Beyond North Pole
            >>> -91.0      # ✗ Beyond South Pole
            >>> 180.0      # ✗ This is longitude range
        """
        if v is not None and (v < -90 or v > 90):
            raise ValueError("Latitude must be between -90 and 90")
        return v

    @field_validator("source_lng", "destination_lng")
    @classmethod
    def validate_longitude(cls, v):
        """
        Validate longitude coordinate values for GPS accuracy.

        Ensures longitude values fall within the valid geographic range.
        Longitude represents the east-west position on Earth's surface.

        Args:
            v (float | None): The longitude value to validate

        Returns:
            float | None: The validated longitude value, or None if input was None

        Raises:
            ValueError: If longitude is outside the valid range (-180 to 180 degrees)

        Geographic Reference:
            - -180°: International Date Line (westernmost)
            -    0°: Prime Meridian (Greenwich, England)
            - +180°: International Date Line (easternmost)

        Example:
            >>> # Valid longitudes
            >>> -74.0060   # ✓ New York City
            >>> 151.2093   # ✓ Sydney, Australia
            >>> 0.0        # ✓ Prime Meridian (Greenwich)
            >>> -179.9999  # ✓ Near Date Line (west)
            >>> 179.9999   # ✓ Near Date Line (east)

            >>> # Invalid longitudes
            >>> 181.0      # ✗ Beyond eastern limit
            >>> -181.0     # ✗ Beyond western limit
            >>> 360.0      # ✗ Full circle, but invalid range
        """
        if v is not None and (v < -180 or v > 180):
            raise ValueError("Longitude must be between -180 and 180")
        return v

    @field_validator("distance_km")
    @classmethod
    def validate_distance(cls, v):
        """
        Validate distance values for physical accuracy.

        Ensures distance values are non-negative real numbers representing
        kilometers between two geographic points on Earth.

        Args:
            v (float | None): The distance value in kilometers to validate

        Returns:
            float | None: The validated distance value, or None if input was None

        Raises:
            ValueError: If distance is negative (physically impossible)

        Physical Reference:
            - Maximum possible distance on Earth: ~20,037 km (half Earth's circumference)
            - Typical city distances: 1-50 km
            - Typical country distances: 100-5,000 km
            - Continental distances: 1,000-15,000 km

        Example:
            >>> # Valid distances
            >>> 0.0        # ✓ Same location
            >>> 5.2        # ✓ Across town
            >>> 250.5      # ✓ Between cities
            >>> 12742.0    # ✓ Opposite sides of Earth (diameter)

            >>> # Invalid distances
            >>> -1.0       # ✗ Negative distance (impossible)
            >>> -0.1       # ✗ Any negative value
        """
        if v is not None and v < 0:
            raise ValueError("Distance cannot be negative")
        return v
