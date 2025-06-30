"""
History API endpoint for retrieving past distance queries.
Provides pagination, filtering, sorting, and search capabilities.
"""

from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, or_
from pydantic import BaseModel, Field, validator
from app.models.database import SessionLocal
from app.models.distance_query import DistanceQuery
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class HistoryQueryParams(BaseModel):
    """Query parameters for history endpoint"""

    limit: int = Field(
        default=10, ge=1, le=100, description="Number of items to return"
    )
    offset: int = Field(default=0, ge=0, description="Number of items to skip")
    start_date: Optional[datetime] = Field(
        None, description="Filter results from this date"
    )
    end_date: Optional[datetime] = Field(
        None, description="Filter results up to this date"
    )
    search: Optional[str] = Field(None, description="Search in addresses")
    sort_by: str = Field(
        default="created_at",
        description="Field to sort by",
        pattern="^(created_at|distance_km|source_address|destination_address)$",
    )
    sort_order: str = Field(
        default="desc", description="Sort order", pattern="^(asc|desc)$"
    )

    @validator("end_date")
    def validate_date_range(cls, v, values):
        """Ensure end_date is after start_date if both are provided"""
        if v and "start_date" in values and values["start_date"]:
            if v < values["start_date"]:
                raise ValueError("end_date must be after start_date")
        return v


class HistoryItem(BaseModel):
    """Individual history item in response"""

    id: int
    source_address: str
    destination_address: str
    source_lat: float
    source_lng: float
    destination_lat: float
    destination_lng: float
    distance_km: float
    created_at: datetime

    class Config:
        from_attributes = True


class HistoryResponse(BaseModel):
    """Paginated history response"""

    items: List[HistoryItem]
    total: int
    limit: int
    offset: int
    has_more: bool


@router.get("/history", response_model=HistoryResponse)
async def get_history(
    limit: int = Query(10, ge=1, le=100, description="Number of items to return"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    start_date: Optional[datetime] = Query(
        None, description="Filter results from this date"
    ),
    end_date: Optional[datetime] = Query(
        None, description="Filter results up to this date"
    ),
    search: Optional[str] = Query(None, description="Search in addresses"),
    sort_by: str = Query(
        "created_at",
        pattern="^(created_at|distance_km|source_address|destination_address)$",
        description="Field to sort by",
    ),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
    db: Session = Depends(get_db),
):
    """
    Retrieve history of distance queries with pagination and filtering.

    - **limit**: Maximum number of results to return (1-100)
    - **offset**: Number of results to skip for pagination
    - **start_date**: Filter results from this date (ISO format)
    - **end_date**: Filter results up to this date (ISO format)
    - **search**: Search term for filtering by addresses
    - **sort_by**: Field to sort by (created_at, distance_km, source_address, destination_address)
    - **sort_order**: Sort order (asc or desc)
    """
    try:
        # Start building the query
        query = db.query(DistanceQuery)

        # Apply date filtering
        if start_date:
            query = query.filter(DistanceQuery.created_at >= start_date)
        if end_date:
            query = query.filter(DistanceQuery.created_at <= end_date)

        # Apply search filtering
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    DistanceQuery.source_address.ilike(search_term),
                    DistanceQuery.destination_address.ilike(search_term),
                )
            )

        # Get total count before pagination
        total = query.count()

        # Apply sorting
        sort_column = getattr(DistanceQuery, sort_by)
        if sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

        # Apply pagination
        items = query.offset(offset).limit(limit).all()

        # Check if there are more results
        has_more = (offset + len(items)) < total

        logger.info(
            f"Retrieved {len(items)} history items (total: {total}, "
            f"offset: {offset}, limit: {limit})"
        )

        return HistoryResponse(
            items=[HistoryItem.model_validate(item) for item in items],
            total=total,
            limit=limit,
            offset=offset,
            has_more=has_more,
        )

    except Exception as e:
        logger.error(f"Error retrieving history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve history")
