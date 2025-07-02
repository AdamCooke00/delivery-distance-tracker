# Sprint 2: Database Foundation

## 🎯 Objective
Set up PostgreSQL database with Docker, create the database schema, and establish reliable database connectivity patterns with proper error handling.

## 📋 Acceptance Criteria

### 1. Docker PostgreSQL Setup
- [ ] Create `docker/docker-compose.yml` with PostgreSQL 14+ service
- [ ] Configure PostgreSQL with proper environment variables
- [ ] Set up persistent volume for database data
- [ ] Create database initialization scripts
- [ ] Verify database starts and is accessible

### 2. Database Schema Implementation
- [ ] Create `app/models/database.py` with SQLAlchemy setup
- [ ] Implement exact schema from stack decision:
  ```sql
  CREATE TABLE distance_queries (
      id SERIAL PRIMARY KEY,
      source_address VARCHAR(255) NOT NULL,
      destination_address VARCHAR(255) NOT NULL,
      source_lat DECIMAL(10, 8),
      source_lng DECIMAL(11, 8),
      destination_lat DECIMAL(10, 8),
      destination_lng DECIMAL(11, 8),
      distance_km DECIMAL(10, 3),
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );
  ```
- [ ] Create required indexes for performance
- [ ] Implement database migration capability

### 3. Database Models & ORM
- [ ] Create `app/models/distance_query.py` with SQLAlchemy model
- [ ] Implement Pydantic schemas for request/response validation
- [ ] Set up database connection pooling
- [ ] Create database session management

### 4. Database Utilities
- [ ] Create `app/utils/database.py` with connection utilities
- [ ] Implement database health check functionality
- [ ] Create database initialization and migration scripts
- [ ] Set up proper error handling for database operations

### 5. Testing Infrastructure
- [ ] Set up test database configuration
- [ ] Create database fixtures for testing
- [ ] Implement test data cleanup mechanisms
- [ ] Create database connectivity tests

### 6. README.md Documentation
- [ ] Update README.md to reflect current repository state
- [ ] Document prerequisites: Python 3.8+, Docker, Docker Compose
- [ ] Include complete setup instructions:
  - Clone repository steps
  - Virtual environment setup and activation
  - Dependencies installation
  - Docker and Docker Compose installation verification
  - Database setup with docker-compose up postgres
  - Environment variables configuration for database connection
  - Database schema initialization commands
- [ ] Document how to run database tests and verify connectivity

## 🧪 Test Cases That Must Pass

### Test Case 1: Docker Database Startup
```bash
# Database container starts successfully
cd docker
docker-compose up -d postgres
docker-compose ps | grep postgres | grep "Up"
docker-compose logs postgres | grep "database system is ready to accept connections"
echo "✅ PostgreSQL container started successfully"
```

### Test Case 2: Database Connection Test
```python
# File: app/tests/test_database_connection.py
import pytest
from sqlalchemy import create_engine, text
from app.utils.database import get_database_url

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
```

### Test Case 3: Schema Creation Test
```python
# File: app/tests/test_database_schema.py
import pytest
from sqlalchemy import create_engine, inspect, text
from app.models.database import Base, engine
from app.models.distance_query import DistanceQuery

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
        'id': 'INTEGER',
        'source_address': 'VARCHAR', 
        'destination_address': 'VARCHAR',
        'source_lat': 'NUMERIC',
        'source_lng': 'NUMERIC', 
        'destination_lat': 'NUMERIC',
        'destination_lng': 'NUMERIC',
        'distance_km': 'NUMERIC',
        'created_at': 'TIMESTAMP'
    }
    
    for column in columns:
        col_name = column['name']
        col_type = str(column['type'])
        assert col_name in expected_columns
        assert expected_columns[col_name] in col_type
    
    print("✅ Table schema validated")

def test_indexes_created():
    """Test that required indexes exist"""
    inspector = inspect(engine)
    indexes = inspector.get_indexes("distance_queries")
    
    index_names = [idx['name'] for idx in indexes]
    assert "idx_distance_queries_created_at" in index_names
    assert "idx_distance_queries_addresses" in index_names
    print("✅ Database indexes created")
```

### Test Case 4: Model Operations Test
```python
# File: app/tests/test_distance_query_model.py
import pytest
from datetime import datetime
from app.models.distance_query import DistanceQuery
from app.models.database import SessionLocal

def test_create_distance_query():
    """Test creating a new distance query record"""
    db = SessionLocal()
    
    query = DistanceQuery(
        source_address="123 Main St, City, State",
        destination_address="456 Oak Ave, City, State", 
        source_lat=40.7128,
        source_lng=-74.0060,
        destination_lat=40.7589,
        destination_lng=-73.9851,
        distance_km=5.2
    )
    
    db.add(query)
    db.commit()
    db.refresh(query)
    
    assert query.id is not None
    assert query.created_at is not None
    assert query.distance_km == 5.2
    
    db.close()
    print("✅ Distance query model operations work")

def test_query_retrieval():
    """Test retrieving distance queries from database"""
    db = SessionLocal()
    
    queries = db.query(DistanceQuery).all()
    assert len(queries) >= 1
    
    latest_query = db.query(DistanceQuery).order_by(DistanceQuery.created_at.desc()).first()
    assert latest_query is not None
    
    db.close()
    print("✅ Distance query retrieval works")
```

### Test Case 5: Database Health Check
```python
# File: app/tests/test_database_health.py
import pytest
from app.utils.database import check_database_health

def test_database_health_check():
    """Test database health check utility"""
    is_healthy, message = check_database_health()
    assert is_healthy is True
    assert "healthy" in message.lower()
    print("✅ Database health check works")
```

## 🔧 Implementation Steps

### Step 1: Docker Configuration
1. Create `docker/docker-compose.yml` with PostgreSQL service
2. Configure environment variables for database connection
3. Set up volume mounting for data persistence
4. Create database initialization script

### Step 2: Database Configuration
1. Create `app/models/database.py` with SQLAlchemy engine and session setup
2. Configure connection pooling and database URL handling
3. Set up environment-specific database configurations
4. Implement proper connection management

### Step 3: Schema Implementation
1. Create `app/models/distance_query.py` with SQLAlchemy model
2. Define exact table structure as specified in stack decision
3. Create database indexes for performance optimization
4. Implement Pydantic schemas for validation

### Step 4: Database Utilities
1. Create `app/utils/database.py` with helper functions
2. Implement database health check functionality
3. Create migration and initialization utilities
4. Set up proper error handling patterns

### Step 5: Testing Setup
1. Configure test database environment
2. Create test fixtures and cleanup utilities
3. Implement comprehensive database tests
4. Verify all functionality works correctly

## 📝 Git Workflow Instructions

### Branch Strategy
- Work on `feature/sprint-02-database` branch
- Branch from `develop` after Sprint 1 is merged
- Follow conventional commit format

### Commit Process
1. Create feature branch: `git checkout develop && git pull && git checkout -b feature/sprint-02-database`
2. Make changes following acceptance criteria
3. Run all tests to ensure they pass
4. Commit changes: `git commit -m "feat: implement PostgreSQL database foundation with Docker"`
5. Push branch: `git push -u origin feature/sprint-02-database`

## 🔒 Security Requirements
- [ ] Database credentials stored in environment variables only
- [ ] No hardcoded database passwords in any files
- [ ] SQL injection prevention with parameterized queries
- [ ] Database connection properly secured
- [ ] Test database isolated from production configuration

## 📊 Quality Gates
- [ ] All 5 test cases pass
- [ ] Database starts cleanly with `docker-compose up`
- [ ] Schema matches exact specification from stack decision
- [ ] Models work correctly with ORM operations
- [ ] Code passes Black formatting and Flake8 linting
- [ ] Test coverage for database operations >= 80%

## 🎁 Deliverables
1. Working Docker Compose configuration for PostgreSQL
2. Complete database schema with proper indexes
3. SQLAlchemy models and Pydantic schemas
4. Database connection and session management utilities
5. Comprehensive test suite for database operations
6. Database health check functionality
7. Migration and initialization scripts

## 🚫 Exit Criteria
**This sprint is complete when:**
- All 5 test cases pass without errors
- Database can be started with single `docker-compose up` command
- All database operations work correctly through ORM
- Schema exactly matches stack decision specification
- Test suite provides comprehensive coverage
- Feature branch is ready for merge to develop

## 🔄 Next Sprint Preview
Sprint 3 will build upon the database foundation by creating the FastAPI application framework, implementing basic routing structure, and adding the health check endpoint with proper error handling.