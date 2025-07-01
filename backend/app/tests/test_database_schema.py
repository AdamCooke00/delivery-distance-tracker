"""Test database schema creation and structure."""

from sqlalchemy import inspect, text
from app.models.database import Base, engine


def test_table_creation():
    """Test that distance_queries table is created correctly"""
    Base.metadata.create_all(bind=engine)

    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert "distance_queries" in tables
    print("✅ distance_queries table created")


def test_table_schema():
    """Test that table has correct columns and types"""
    inspector = inspect(engine)
    columns = inspector.get_columns("distance_queries")

    expected_columns = {
        "id": "INTEGER",
        "source_address": "VARCHAR",
        "destination_address": "VARCHAR",
        "source_lat": "NUMERIC",
        "source_lng": "NUMERIC",
        "destination_lat": "NUMERIC",
        "destination_lng": "NUMERIC",
        "distance_km": "NUMERIC",
        "created_at": "TIMESTAMP",
    }

    column_dict = {col["name"]: str(col["type"]) for col in columns}

    for col_name, expected_type in expected_columns.items():
        assert col_name in column_dict, f"Column {col_name} not found"
        assert (
            expected_type in column_dict[col_name]
        ), f"Column {col_name} has wrong type: {column_dict[col_name]}"

    print("✅ Table schema validated")


def test_indexes_created():
    """Test that required indexes exist"""
    inspector = inspect(engine)
    indexes = inspector.get_indexes("distance_queries")

    index_names = [idx["name"] for idx in indexes]

    # Check for our custom indexes
    expected_indexes = [
        "idx_distance_queries_created_at",
        "idx_distance_queries_addresses",
    ]
    for expected_index in expected_indexes:
        # PostgreSQL might modify index names, so check if any index contains our expected name
        index_found = any(expected_index in idx_name for idx_name in index_names)
        if not index_found:
            # Try to find the index by checking the actual database
            with engine.connect() as conn:
                result = conn.execute(
                    text(
                        """
                    SELECT indexname FROM pg_indexes
                    WHERE tablename = 'distance_queries'
                    AND indexname LIKE %s
                """
                    ),
                    (f"%{expected_index.split('_')[-1]}%",),
                )
                db_indexes = [row[0] for row in result.fetchall()]
                index_found = len(db_indexes) > 0

        assert index_found, f"Index {expected_index} not found"

    print("✅ Database indexes created")


def test_table_constraints():
    """Test table constraints and nullable fields"""
    inspector = inspect(engine)
    columns = inspector.get_columns("distance_queries")

    # Check primary key
    pk_columns = inspector.get_pk_constraint("distance_queries")
    assert pk_columns["constrained_columns"] == ["id"]

    # Check NOT NULL constraints
    for col in columns:
        if col["name"] in ["source_address", "destination_address"]:
            assert not col["nullable"], f"Column {col['name']} should be NOT NULL"
        elif col["name"] == "id":
            assert not col["nullable"], "ID column should be NOT NULL"

    print("✅ Table constraints validated")


def test_table_creation_idempotent():
    """Test that creating tables multiple times doesn't cause errors"""
    # Create tables multiple times
    Base.metadata.create_all(bind=engine)
    Base.metadata.create_all(bind=engine)  # Should not raise error

    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert "distance_queries" in tables

    print("✅ Table creation is idempotent")
