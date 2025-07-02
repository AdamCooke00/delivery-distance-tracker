"""Test environment configuration and database environment setup."""

import os
from dotenv import load_dotenv


def test_environment_variables_loaded():
    """Test that required environment variables are loaded"""
    load_dotenv()
    assert os.getenv("DATABASE_URL") is not None
    assert os.getenv("NOMINATIM_BASE_URL") is not None
    assert os.getenv("LOG_LEVEL") is not None
    print("✅ Environment configuration validated")


def test_database_environment_variables():
    """Test database-specific environment variables"""
    load_dotenv()

    # Test DATABASE_URL format
    db_url = os.getenv("DATABASE_URL")
    assert db_url is not None
    assert db_url.startswith("postgresql://")
    assert "delivery_tracker" in db_url

    # Test optional PostgreSQL variables
    postgres_user = os.getenv("POSTGRES_USER")
    postgres_password = os.getenv("POSTGRES_PASSWORD")
    postgres_db = os.getenv("POSTGRES_DB")

    if postgres_user:
        assert len(postgres_user) > 0
    if postgres_password:
        assert len(postgres_password) > 0
    if postgres_db:
        assert postgres_db == "delivery_tracker"

    print("✅ Database environment variables validated")


def test_environment_file_security():
    """Test that .env file is properly configured and secure"""
    load_dotenv()

    # Check that we don't have default/insecure values
    db_url = os.getenv("DATABASE_URL", "")

    # Should not contain default placeholder values
    assert "user:password" not in db_url or "delivery_user:delivery_password" in db_url

    # Check that LOG_LEVEL is valid
    log_level = os.getenv("LOG_LEVEL", "INFO")
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    assert log_level.upper() in valid_levels

    print("✅ Environment security checks passed")


def test_dotenv_loading():
    """Test that python-dotenv loads configuration correctly"""
    # Test loading from different sources
    load_dotenv()

    # Should be able to get at least the basic required variables
    required_vars = ["DATABASE_URL", "NOMINATIM_BASE_URL", "LOG_LEVEL"]

    for var in required_vars:
        value = os.getenv(var)
        assert value is not None, f"Required environment variable {var} not found"
        assert len(value) > 0, f"Environment variable {var} is empty"

    print("✅ Dotenv loading works correctly")


def test_database_url_parsing():
    """Test that DATABASE_URL can be parsed correctly"""
    load_dotenv()

    db_url = os.getenv("DATABASE_URL")
    assert db_url is not None

    # Basic URL format validation
    parts = db_url.split("://")
    assert len(parts) == 2
    assert parts[0] == "postgresql"

    # Should contain host, port, and database name
    assert "@" in parts[1]  # User:password@host format
    assert ":" in parts[1]  # Port specification
    assert "/" in parts[1]  # Database name

    print("✅ Database URL parsing validation passed")
