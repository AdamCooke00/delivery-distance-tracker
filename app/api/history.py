"""
History API endpoint for retrieving past distance queries.
Provides pagination, filtering, sorting, and search capabilities.
"""

from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, or_
from pydantic import BaseModel, Field, validator
from app.models.database import SessionLocal
from app.models.distance_query import DistanceQuery
import logging
import re

logger = logging.getLogger(__name__)

router = APIRouter()

# Secure mapping for sort columns - eliminates dynamic attribute access vulnerability
SORT_COLUMNS = {
    "created_at": DistanceQuery.created_at,
    "distance_km": DistanceQuery.distance_km,
    "source_address": DistanceQuery.source_address,
    "destination_address": DistanceQuery.destination_address,
}


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def sanitize_search_term(search_term: str) -> str:
    """Sanitize search input to prevent injection attacks"""
    if not search_term:
        return ""
    # Remove potentially dangerous characters and limit length
    sanitized = re.sub(r'[<>"\';\\]', "", search_term.strip())
    return sanitized[:100]  # Limit to 100 characters


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
    params: HistoryQueryParams = Depends(),
    db: Session = Depends(get_db),
):
    """
    Retrieve history of distance queries with pagination and filtering.

    Security features:
    - All parameter validation handled by Pydantic HistoryQueryParams model
    - Secure column mapping prevents dynamic attribute access vulnerability
    - Input sanitization for search terms prevents injection attacks
    - Database-level pagination for performance
    """
    try:
        # Start building the query
        query = db.query(DistanceQuery)

        # Apply date filtering
        if params.start_date:
            query = query.filter(DistanceQuery.created_at >= params.start_date)
        if params.end_date:
            query = query.filter(DistanceQuery.created_at <= params.end_date)

        # Apply search filtering with sanitization
        if params.search:
            sanitized_search = sanitize_search_term(params.search)
            if (
                sanitized_search
            ):  # Only search if we have valid terms after sanitization
                search_term = f"%{sanitized_search}%"
                query = query.filter(
                    or_(
                        DistanceQuery.source_address.ilike(search_term),
                        DistanceQuery.destination_address.ilike(search_term),
                    )
                )

        # Get total count before pagination
        total = query.count()

        # Apply sorting using secure column mapping
        # Note: sort_by validation is handled by Pydantic Field pattern validation
        sort_column = SORT_COLUMNS[params.sort_by]
        if params.sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

        # Apply pagination
        items = query.offset(params.offset).limit(params.limit).all()

        # Check if there are more results
        has_more = (params.offset + len(items)) < total

        logger.info(
            f"Retrieved {len(items)} history items (total: {total}, "
            f"offset: {params.offset}, limit: {params.limit})"
        )

        return HistoryResponse(
            items=[HistoryItem.model_validate(item) for item in items],
            total=total,
            limit=params.limit,
            offset=params.offset,
            has_more=has_more,
        )

    except HTTPException:
        # Re-raise HTTP exceptions (validation errors)
        raise
    except Exception as e:
        logger.error(f"Error retrieving history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve history")
