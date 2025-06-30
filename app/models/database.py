"""Database configuration and session management for SQLAlchemy."""

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
    """Get the database URL from environment variables."""
    return DATABASE_URL


def get_db_session():
    """Create a new database session."""
    db = SessionLocal()
    try:
        return db
    except Exception:
        db.close()
        raise


def close_db_session(db):
    """Close a database session."""
    db.close()
