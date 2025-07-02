"""Test database connection functionality."""

from sqlalchemy import create_engine, text
from app.models.database import get_database_url


def test_database_connection():
    """Test that we can connect to the database"""
    engine = create_engine(get_database_url())
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        assert result.fetchone()[0] == 1
    print("✅ Database connection successful")


def test_database_exists():
    """Test that our database exists"""
    engine = create_engine(get_database_url())
    with engine.connect() as conn:
        result = conn.execute(text("SELECT current_database()"))
        db_name = result.fetchone()[0]
        assert db_name == "delivery_tracker"
    print("✅ Database exists and is accessible")


def test_database_url_format():
    """Test that database URL is properly formatted"""
    db_url = get_database_url()
    assert db_url.startswith("postgresql://")
    assert "delivery_tracker" in db_url
    print("✅ Database URL format is correct")


def test_database_connection_pooling():
    """Test database connection pooling works"""
    engine = create_engine(get_database_url())

    # Test multiple connections
    connections = []
    try:
        for i in range(3):
            conn = engine.connect()
            connections.append(conn)
            result = conn.execute(text("SELECT 1"))
            assert result.fetchone()[0] == 1

        print("✅ Database connection pooling works")
    finally:
        # Close all connections
        for conn in connections:
            conn.close()


def test_database_engine_configuration():
    """Test that database engine is properly configured"""
    engine = create_engine(get_database_url())

    # Check that engine has proper configuration
    assert engine.pool.size() >= 0  # Pool exists
    assert hasattr(engine, "url")
    assert str(engine.url).startswith("postgresql://")

    print("✅ Database engine configuration is correct")
