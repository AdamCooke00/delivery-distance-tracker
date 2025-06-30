"""Test distance query model operations."""

from datetime import datetime
from app.models.distance_query import DistanceQuery
from app.models.database import SessionLocal


def test_create_distance_query():
    """Test creating a new distance query record"""
    db = SessionLocal()

    try:
        query = DistanceQuery(
            source_address="123 Main St, City, State",
            destination_address="456 Oak Ave, City, State",
            source_lat=40.7128,
            source_lng=-74.0060,
            destination_lat=40.7589,
            destination_lng=-73.9851,
            distance_km=5.2,
        )

        db.add(query)
        db.commit()
        db.refresh(query)

        assert query.id is not None
        assert query.created_at is not None
        assert float(query.distance_km) == 5.2
        assert query.source_address == "123 Main St, City, State"
        assert query.destination_address == "456 Oak Ave, City, State"

        print("✅ Distance query model operations work")
    finally:
        db.close()


def test_query_retrieval():
    """Test retrieving distance queries from database"""
    db = SessionLocal()

    try:
        # First, create a test record
        query = DistanceQuery(
            source_address="Test Source",
            destination_address="Test Destination",
            source_lat=40.0,
            source_lng=-74.0,
            destination_lat=41.0,
            destination_lng=-73.0,
            distance_km=10.5,
        )

        db.add(query)
        db.commit()
        db.refresh(query)

        # Test retrieval
        queries = db.query(DistanceQuery).all()
        assert len(queries) >= 1

        latest_query = (
            db.query(DistanceQuery).order_by(DistanceQuery.created_at.desc()).first()
        )
        assert latest_query is not None
        assert latest_query.source_address == "Test Source"

        print("✅ Distance query retrieval works")
    finally:
        db.close()


def test_model_validation():
    """Test model field validation and constraints"""
    db = SessionLocal()

    try:
        # Test with minimal required fields
        query = DistanceQuery(
            source_address="Source", destination_address="Destination"
        )

        db.add(query)
        db.commit()
        db.refresh(query)

        assert query.id is not None
        assert query.created_at is not None
        assert query.source_lat is None  # Optional field
        assert query.distance_km is None  # Optional field

        print("✅ Model validation works correctly")
    finally:
        db.close()


def test_model_update_operations():
    """Test updating distance query records"""
    db = SessionLocal()

    try:
        # Create a record
        query = DistanceQuery(
            source_address="Original Source",
            destination_address="Original Destination",
            distance_km=5.0,
        )

        db.add(query)
        db.commit()
        db.refresh(query)

        original_id = query.id

        # Update the record
        query.distance_km = 7.5
        query.source_lat = 40.7128
        query.source_lng = -74.0060

        db.commit()

        # Verify update
        updated_query = (
            db.query(DistanceQuery).filter(DistanceQuery.id == original_id).first()
        )
        assert float(updated_query.distance_km) == 7.5
        assert float(updated_query.source_lat) == 40.7128
        assert float(updated_query.source_lng) == -74.0060

        print("✅ Model update operations work")
    finally:
        db.close()


def test_model_delete_operations():
    """Test deleting distance query records"""
    db = SessionLocal()

    try:
        # Create a record
        query = DistanceQuery(
            source_address="To Be Deleted", destination_address="Delete Me Too"
        )

        db.add(query)
        db.commit()
        db.refresh(query)

        record_id = query.id

        # Delete the record
        db.delete(query)
        db.commit()

        # Verify deletion
        deleted_query = (
            db.query(DistanceQuery).filter(DistanceQuery.id == record_id).first()
        )
        assert deleted_query is None

        print("✅ Model delete operations work")
    finally:
        db.close()


def test_model_datetime_handling():
    """Test datetime field handling"""
    db = SessionLocal()

    try:
        query = DistanceQuery(
            source_address="Time Test", destination_address="Time Test 2"
        )

        db.add(query)
        db.commit()
        db.refresh(query)

        # Check that created_at is set and is recent
        assert query.created_at is not None
        assert isinstance(query.created_at, datetime)

        # Should be within the last minute
        time_diff = datetime.utcnow() - query.created_at
        assert time_diff.total_seconds() < 60

        print("✅ Model datetime handling works")
    finally:
        db.close()
