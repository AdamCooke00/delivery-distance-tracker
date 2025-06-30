"""Database utility functions and connection management."""

import time
from typing import Tuple, Optional
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.models.database import engine, SessionLocal, Base


def check_database_health() -> Tuple[bool, str]:
    """
    Check database health and connectivity.

    Returns:
        Tuple[bool, str]: (is_healthy, status_message)
    """
    try:
        start_time = time.time()

        # Test database connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            test_value = result.fetchone()[0]

            if test_value != 1:
                return False, "Database connectivity test failed"

            # Test database exists
            result = conn.execute(text("SELECT current_database()"))
            db_name = result.fetchone()[0]

            response_time = round((time.time() - start_time) * 1000, 2)

            return (
                True,
                f"Database '{db_name}' is healthy (response: {response_time}ms)",
            )

    except SQLAlchemyError as e:
        return False, f"Database error: {str(e)}"
    except Exception as e:
        return False, f"Unexpected database error: {str(e)}"


def initialize_database():
    """
    Initialize database tables and schema.
    Creates all tables defined in the Base metadata.
    """
    try:
        Base.metadata.create_all(bind=engine)
        return True, "Database initialized successfully"
    except SQLAlchemyError as e:
        return False, f"Database initialization failed: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error during initialization: {str(e)}"


def get_database_session():
    """
    Get a new database session with proper error handling.

    Returns:
        SessionLocal: Database session
    """
    try:
        session = SessionLocal()
        return session
    except SQLAlchemyError as e:
        raise RuntimeError(f"Failed to create database session: {str(e)}")


def close_database_session(session):
    """
    Safely close a database session.

    Args:
        session: Database session to close
    """
    try:
        if session:
            session.close()
    except Exception:
        # Ignore errors when closing session
        pass


def test_database_operations() -> Tuple[bool, str]:
    """
    Test basic database operations (CRUD).

    Returns:
        Tuple[bool, str]: (success, message)
    """
    from app.models.distance_query import DistanceQuery

    session = None
    try:
        session = get_database_session()

        # Test CREATE - Insert a test record
        test_query = DistanceQuery(
            source_address="Test Source Address",
            destination_address="Test Destination Address",
            source_lat=40.7128,
            source_lng=-74.0060,
            destination_lat=40.7589,
            destination_lng=-73.9851,
            distance_km=5.2,
        )

        session.add(test_query)
        session.commit()
        session.refresh(test_query)

        # Test READ - Query the record
        retrieved_query = (
            session.query(DistanceQuery)
            .filter(DistanceQuery.id == test_query.id)
            .first()
        )

        if not retrieved_query:
            return False, "Failed to retrieve test record"

        # Test UPDATE - Modify the record
        retrieved_query.distance_km = 6.0
        session.commit()

        # Test DELETE - Remove the record
        session.delete(retrieved_query)
        session.commit()

        return True, "Database CRUD operations successful"

    except SQLAlchemyError as e:
        if session:
            session.rollback()
        return False, f"Database operation failed: {str(e)}"
    except Exception as e:
        if session:
            session.rollback()
        return False, f"Unexpected error in database operations: {str(e)}"
    finally:
        close_database_session(session)


def get_table_info() -> Optional[dict]:
    """
    Get information about database tables.

    Returns:
        dict: Table information or None if error
    """
    try:
        with engine.connect() as conn:
            # Get table names
            result = conn.execute(
                text(
                    """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
            """
                )
            )
            tables = [row[0] for row in result.fetchall()]

            # Get column info for distance_queries table
            result = conn.execute(
                text(
                    """
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'distance_queries'
                ORDER BY ordinal_position
            """
                )
            )
            columns = [
                {"name": row[0], "type": row[1], "nullable": row[2] == "YES"}
                for row in result.fetchall()
            ]

            # Get index info
            result = conn.execute(
                text(
                    """
                SELECT indexname, indexdef
                FROM pg_indexes
                WHERE tablename = 'distance_queries'
            """
                )
            )
            indexes = [
                {"name": row[0], "definition": row[1]} for row in result.fetchall()
            ]

            return {
                "tables": tables,
                "distance_queries_columns": columns,
                "distance_queries_indexes": indexes,
            }

    except SQLAlchemyError as e:
        print(f"Error getting table info: {str(e)}")
        return None
    except Exception as e:
        print(f"Unexpected error getting table info: {str(e)}")
        return None
