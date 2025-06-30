"""Distance query model and schemas."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Column, Integer, String, Numeric, DateTime
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
    created_at = Column(DateTime, default=datetime.utcnow)


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
        """Validate address fields."""
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
    created_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
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
        """Validate latitude values."""
        if v is not None and (v < -90 or v > 90):
            raise ValueError("Latitude must be between -90 and 90")
        return v

    @field_validator("source_lng", "destination_lng")
    @classmethod
    def validate_longitude(cls, v):
        """Validate longitude values."""
        if v is not None and (v < -180 or v > 180):
            raise ValueError("Longitude must be between -180 and 180")
        return v

    @field_validator("distance_km")
    @classmethod
    def validate_distance(cls, v):
        """Validate distance values."""
        if v is not None and v < 0:
            raise ValueError("Distance cannot be negative")
        return v
