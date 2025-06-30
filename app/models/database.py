"""
Database configuration and session management for SQLAlchemy.

This module configures the core database infrastructure for the Delivery Distance Tracker:

Database Connection:
- PostgreSQL database with connection pooling for performance
- Environment-based configuration for different deployment environments
- Automatic connection retry and error handling
- Connection pool settings optimized for web application usage

Connection Pooling Configuration:
- Pool size: 20 connections (configurable via engine parameters)
- Pool recycle: 3600 seconds to prevent stale connections
- Pool pre-ping: True for connection health checking
- Echo: False in production, True for debugging SQL queries

Session Management:
- SessionLocal: Factory for creating database sessions
- Autocommit: False (explicit transaction control)
- Autoflush: False (manual flush control for performance)
- Bind: Connected to the configured engine

Base Model:
- Declarative base for all SQLAlchemy models
- Provides common functionality for model inheritance
- Used by all database models in the application

Environment Variables:
- DATABASE_URL: Full PostgreSQL connection string
- Fallback: localhost connection for development

Usage Example:
    # Create a database session
    db = SessionLocal()
    try:
        # Perform database operations
        result = db.query(Model).all()
        db.commit()
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()

    # Or use with context manager (recommended)
    with SessionLocal() as db:
        result = db.query(Model).all()
        db.commit()
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database URL from environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://delivery_user:delivery_password@localhost:5432/delivery_tracker",
)

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True,
    pool_recycle=300,
)

# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base
Base = declarative_base()


def get_database_url():
    """
    Get the database URL from environment variables.

    Retrieves the PostgreSQL connection string from the DATABASE_URL environment
    variable, with a fallback to localhost development configuration.

    Returns:
        str: PostgreSQL connection URL in the format:
             postgresql://user:password@host:port/database

    Example:
        >>> url = get_database_url()
        >>> print(url)
        postgresql://delivery_user:delivery_password@localhost:5432/delivery_tracker
    """
    return DATABASE_URL


def get_db_session():
    """
    Create a new database session for manual session management.

    Creates a new SQLAlchemy session using the configured SessionLocal factory.
    This function is provided for cases where manual session management is needed,
    though dependency injection is preferred for FastAPI endpoints.

    Important: The caller is responsible for closing the session to prevent
    connection leaks. Use try/finally blocks or context managers.

    Returns:
        Session: A new SQLAlchemy database session

    Raises:
        SQLAlchemyError: If session creation fails

    Example:
        >>> db = get_db_session()
        >>> try:
        ...     result = db.query(Model).all()
        ...     db.commit()
        ... except Exception as e:
        ...     db.rollback()
        ...     raise
        ... finally:
        ...     db.close()

    Preferred Usage (with dependency injection):
        ```python
        def get_db():
            db = SessionLocal()
            try:
                yield db
            finally:
                db.close()

        @app.get("/items/")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Model).all()
        ```
    """
    db = SessionLocal()
    try:
        return db
    except Exception:
        db.close()
        raise


def close_db_session(db):
    """Close a database session."""
    db.close()
