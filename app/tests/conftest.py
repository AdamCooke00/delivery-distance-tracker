"""Test configuration and fixtures for database testing."""

import os
import pytest
from dotenv import load_dotenv

from app.models.database import Base
from app.models.distance_query import DistanceQuery

# Load environment variables
load_dotenv()

# Use main database for testing (same as production for MVP)
TEST_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://delivery_user:delivery_password@localhost:5432/delivery_tracker",
)


@pytest.fixture(scope="session")
def test_engine():
    """Create a test database engine."""
    from app.models.database import engine as main_engine

    # Use the main engine for Sprint 2 (single database approach)
    # Create all tables if they don't exist
    Base.metadata.create_all(bind=main_engine)

    yield main_engine


@pytest.fixture(scope="function")
def test_session(test_engine):
    """Create a test database session."""
    from app.models.database import SessionLocal

    # Use the main session for Sprint 2
    session = SessionLocal()

    yield session

    # Clean up any test data and close session
    try:
        session.query(DistanceQuery).filter(
            DistanceQuery.source_address.like("Test%")
        ).delete()
        session.commit()
    except Exception:
        session.rollback()
    finally:
        session.close()


@pytest.fixture
def sample_distance_query():
    """Create a sample distance query for testing."""
    return DistanceQuery(
        source_address="123 Main St, City, State",
        destination_address="456 Oak Ave, City, State",
        source_lat=40.7128,
        source_lng=-74.0060,
        destination_lat=40.7589,
        destination_lng=-73.9851,
        distance_km=5.2,
    )


@pytest.fixture
def multiple_distance_queries():
    """Create multiple sample distance queries for testing."""
    return [
        DistanceQuery(
            source_address="Address 1",
            destination_address="Address 2",
            source_lat=40.7128,
            source_lng=-74.0060,
            destination_lat=40.7589,
            destination_lng=-73.9851,
            distance_km=5.2,
        ),
        DistanceQuery(
            source_address="Address 3",
            destination_address="Address 4",
            source_lat=34.0522,
            source_lng=-118.2437,
            destination_lat=37.7749,
            destination_lng=-122.4194,
            distance_km=559.12,
        ),
        DistanceQuery(
            source_address="Address 5",
            destination_address="Address 6",
            source_lat=41.8781,
            source_lng=-87.6298,
            destination_lat=29.7604,
            destination_lng=-95.3698,
            distance_km=1520.5,
        ),
    ]


@pytest.fixture(autouse=True)
def cleanup_database(test_session):
    """Clean up database after each test."""
    yield
    # Clean up any remaining test data
    test_session.query(DistanceQuery).delete()
    test_session.commit()
