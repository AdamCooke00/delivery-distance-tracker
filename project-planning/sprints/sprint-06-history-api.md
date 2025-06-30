# Sprint 6: Query History API

## 🎯 Objective
Implement the GET /history endpoint to retrieve past distance queries with pagination, filtering, sorting capabilities, and proper database optimization.

## 📋 Acceptance Criteria

### 1. History Endpoint Implementation
- [ ] Create `app/api/history.py` with GET /history endpoint
- [ ] Implement query parameter handling for pagination
- [ ] Add filtering capabilities (date range, address search)
- [ ] Implement sorting options (timestamp, distance, addresses)
- [ ] Return paginated results with metadata

### 2. Query Parameters & Validation
- [ ] Create Pydantic models for query parameters
- [ ] Implement `limit` and `offset` for pagination
- [ ] Add `start_date` and `end_date` for date filtering
- [ ] Create `search` parameter for address filtering
- [ ] Add `sort_by` and `sort_order` parameters

### 3. Database Query Optimization
- [ ] Create efficient database queries with proper indexes
- [ ] Implement filtering with SQLAlchemy ORM
- [ ] Add query optimization for large datasets
- [ ] Use database-level pagination for performance
- [ ] Implement proper SQL query generation

### 4. Response Formatting
- [ ] Create `HistoryResponse` model with pagination metadata
- [ ] Format individual query items consistently
- [ ] Include total count for pagination
- [ ] Add query execution time metadata
- [ ] Implement proper JSON serialization

### 5. Performance & Caching
- [ ] Optimize database queries for performance
- [ ] Implement query result validation
- [ ] Add response time monitoring
- [ ] Create efficient data transformation
- [ ] Handle large result sets gracefully

### 6. README.md Documentation
- [ ] Update README.md to reflect current repository state
- [ ] Document prerequisites: Python 3.8+, Docker, Docker Compose
- [ ] Include complete setup instructions:
  - Clone repository steps
  - Virtual environment setup and activation
  - Dependencies installation
  - Database setup with Docker and schema initialization
  - Environment variables configuration
  - FastAPI application startup
  - API endpoints testing
- [ ] Document GET /history endpoint usage with query parameters and examples
- [ ] Include commands to test pagination, filtering, and sorting functionality

## 🧪 Test Cases That Must Pass

### Test Case 1: Basic History Retrieval
```python
# File: app/tests/test_history_endpoint.py
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from app.main import app
from app.models.distance_query import DistanceQuery
from app.models.database import SessionLocal

client = TestClient(app)

def setup_test_data():
    """Create test data for history endpoint testing"""
    db = SessionLocal()
    
    # Clear existing test data
    db.query(DistanceQuery).filter(DistanceQuery.source_address.like("Test%")).delete()
    
    # Create test queries
    test_queries = [
        {
            "source_address": "Test Address 1",
            "destination_address": "Test Destination 1",
            "source_lat": 40.7128,
            "source_lng": -74.0060,
            "destination_lat": 34.0522,
            "destination_lng": -118.2437,
            "distance_km": 3944.0,
            "created_at": datetime.now() - timedelta(days=1)
        },
        {
            "source_address": "Test Address 2", 
            "destination_address": "Test Destination 2",
            "source_lat": 51.5074,
            "source_lng": -0.1278,
            "destination_lat": 48.8566,
            "destination_lng": 2.3522,
            "distance_km": 344.0,
            "created_at": datetime.now() - timedelta(hours=2)
        },
        {
            "source_address": "Test Address 3",
            "destination_address": "Test Destination 3", 
            "source_lat": 35.6762,
            "source_lng": 139.6503,
            "destination_lat": 37.7749,
            "destination_lng": -122.4194,
            "distance_km": 8280.0,
            "created_at": datetime.now()
        }
    ]
    
    for query_data in test_queries:
        query = DistanceQuery(**query_data)
        db.add(query)
    
    db.commit()
    db.close()

def test_get_history_basic():
    """Test basic history retrieval without parameters"""
    setup_test_data()
    
    response = client.get("/api/v1/history")
    assert response.status_code == 200
    
    data = response.json()
    
    # Verify response structure
    required_fields = ["items", "total", "limit", "offset", "has_more"]
    for field in required_fields:
        assert field in data
    
    # Verify items structure
    assert len(data["items"]) > 0
    item = data["items"][0]
    item_fields = ["id", "source_address", "destination_address", "distance_km", "created_at"]
    for field in item_fields:
        assert field in item
    
    print("✅ Basic history retrieval works")

def test_get_history_with_limit():
    """Test history retrieval with limit parameter"""
    setup_test_data()
    
    response = client.get("/api/v1/history?limit=2")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data["items"]) <= 2
    assert data["limit"] == 2
    
    print("✅ History limit parameter works")

def test_get_history_with_pagination():
    """Test history retrieval with pagination"""
    setup_test_data()
    
    # Get first page
    response1 = client.get("/api/v1/history?limit=1&offset=0")
    assert response1.status_code == 200
    data1 = response1.json()
    
    # Get second page
    response2 = client.get("/api/v1/history?limit=1&offset=1")
    assert response2.status_code == 200
    data2 = response2.json()
    
    # Items should be different
    if len(data1["items"]) > 0 and len(data2["items"]) > 0:
        assert data1["items"][0]["id"] != data2["items"][0]["id"]
    
    print("✅ History pagination works")
```

### Test Case 2: Filtering and Search
```python
# File: app/tests/test_history_filtering.py
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from urllib.parse import quote
from app.main import app

client = TestClient(app)

def test_history_date_filtering():
    """Test history filtering by date range"""
    # Get yesterday's date
    yesterday = (datetime.now() - timedelta(days=1)).isoformat()
    
    response = client.get(f"/api/v1/history?start_date={quote(yesterday)}")
    assert response.status_code == 200
    
    data = response.json()
    
    # Verify all returned items are after the start date
    for item in data["items"]:
        item_date = datetime.fromisoformat(item["created_at"].replace("Z", "+00:00"))
        filter_date = datetime.fromisoformat(yesterday)
        assert item_date >= filter_date
    
    print("✅ History date filtering works")

def test_history_search_filtering():
    """Test history filtering by address search"""
    search_term = "Test"
    
    response = client.get(f"/api/v1/history?search={search_term}")
    assert response.status_code == 200
    
    data = response.json()
    
    # Verify all returned items contain the search term
    for item in data["items"]:
        addresses = item["source_address"] + " " + item["destination_address"]
        assert search_term.lower() in addresses.lower()
    
    print("✅ History search filtering works")

def test_history_combined_filters():
    """Test history with multiple filters combined"""
    yesterday = (datetime.now() - timedelta(days=1)).isoformat()
    search_term = "Test"
    
    response = client.get(f"/api/v1/history?search={search_term}&start_date={quote(yesterday)}&limit=5")
    assert response.status_code == 200
    
    data = response.json()
    assert data["limit"] == 5
    
    # Should respect all filters
    for item in data["items"]:
        addresses = item["source_address"] + " " + item["destination_address"]
        assert search_term.lower() in addresses.lower()
        
        item_date = datetime.fromisoformat(item["created_at"].replace("Z", "+00:00"))
        filter_date = datetime.fromisoformat(yesterday)
        assert item_date >= filter_date
    
    print("✅ Combined history filters work")
```

### Test Case 3: Sorting Functionality
```python
# File: app/tests/test_history_sorting.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_history_sort_by_date_desc():
    """Test history sorting by date descending (default)"""
    response = client.get("/api/v1/history?sort_by=created_at&sort_order=desc")
    assert response.status_code == 200
    
    data = response.json()
    
    if len(data["items"]) > 1:
        # Verify items are sorted by date descending
        for i in range(len(data["items"]) - 1):
            current_date = datetime.fromisoformat(data["items"][i]["created_at"].replace("Z", "+00:00"))
            next_date = datetime.fromisoformat(data["items"][i + 1]["created_at"].replace("Z", "+00:00"))
            assert current_date >= next_date
    
    print("✅ History date sorting (desc) works")

def test_history_sort_by_date_asc():
    """Test history sorting by date ascending"""
    response = client.get("/api/v1/history?sort_by=created_at&sort_order=asc")
    assert response.status_code == 200
    
    data = response.json()
    
    if len(data["items"]) > 1:
        # Verify items are sorted by date ascending
        for i in range(len(data["items"]) - 1):
            current_date = datetime.fromisoformat(data["items"][i]["created_at"].replace("Z", "+00:00"))
            next_date = datetime.fromisoformat(data["items"][i + 1]["created_at"].replace("Z", "+00:00"))
            assert current_date <= next_date
    
    print("✅ History date sorting (asc) works")

def test_history_sort_by_distance():
    """Test history sorting by distance"""
    response = client.get("/api/v1/history?sort_by=distance_km&sort_order=desc")
    assert response.status_code == 200
    
    data = response.json()
    
    if len(data["items"]) > 1:
        # Verify items are sorted by distance descending
        for i in range(len(data["items"]) - 1):
            current_distance = data["items"][i]["distance_km"]
            next_distance = data["items"][i + 1]["distance_km"]
            assert current_distance >= next_distance
    
    print("✅ History distance sorting works")

def test_invalid_sort_parameters():
    """Test handling of invalid sort parameters"""
    response = client.get("/api/v1/history?sort_by=invalid_field")
    assert response.status_code == 422
    
    response = client.get("/api/v1/history?sort_order=invalid_order")
    assert response.status_code == 422
    
    print("✅ Invalid sort parameter validation works")
```

### Test Case 4: Error Handling and Validation
```python
# File: app/tests/test_history_validation.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_invalid_pagination_parameters():
    """Test validation of invalid pagination parameters"""
    # Test negative limit
    response = client.get("/api/v1/history?limit=-1")
    assert response.status_code == 422
    
    # Test negative offset
    response = client.get("/api/v1/history?offset=-1")
    assert response.status_code == 422
    
    # Test excessively large limit
    response = client.get("/api/v1/history?limit=10000")
    assert response.status_code == 422
    
    print("✅ Invalid pagination parameter validation works")

def test_invalid_date_format():
    """Test validation of invalid date formats"""
    invalid_dates = [
        "invalid-date",
        "2023-13-01",  # Invalid month
        "2023-02-30",  # Invalid day
        "not-a-date"
    ]
    
    for invalid_date in invalid_dates:
        response = client.get(f"/api/v1/history?start_date={invalid_date}")
        assert response.status_code == 422
    
    print("✅ Invalid date format validation works")

def test_database_error_handling():
    """Test handling of database errors during history retrieval"""
    # This test would require mocking database errors
    # For now, just verify the endpoint doesn't crash
    response = client.get("/api/v1/history")
    assert response.status_code in [200, 500]  # Either success or graceful error
    
    print("✅ Database error handling verified")
```

### Test Case 5: Performance and Optimization
```python
# File: app/tests/test_history_performance.py
import pytest
import time
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_history_response_time():
    """Test that history endpoint responds within acceptable time"""
    start_time = time.time()
    
    response = client.get("/api/v1/history?limit=50")
    
    end_time = time.time()
    response_time = end_time - start_time
    
    assert response.status_code == 200
    assert response_time < 2.0  # Should respond within 2 seconds
    
    print(f"✅ History response time: {response_time:.3f}s")

def test_large_result_set_handling():
    """Test handling of requests for large result sets"""
    # Test with maximum allowed limit
    response = client.get("/api/v1/history?limit=100")
    assert response.status_code == 200
    
    data = response.json()
    assert "items" in data
    assert len(data["items"]) <= 100
    
    print("✅ Large result set handling works")

def test_pagination_metadata_accuracy():
    """Test accuracy of pagination metadata"""
    response = client.get("/api/v1/history?limit=5&offset=0")
    assert response.status_code == 200
    
    data = response.json()
    
    # Verify metadata fields exist and are logical
    assert "total" in data
    assert "has_more" in data
    assert data["total"] >= len(data["items"])
    
    if data["total"] > 5:
        assert data["has_more"] is True
    else:
        assert data["has_more"] is False
    
    print("✅ Pagination metadata accuracy verified")
```

## 🔧 Implementation Steps

### Step 1: History Endpoint Foundation
1. Create `app/api/history.py` with GET endpoint
2. Set up basic routing and response structure
3. Create Pydantic models for query parameters
4. Implement basic database query
5. Add initial error handling

### Step 2: Query Parameters and Validation
1. Implement pagination parameters (limit, offset)
2. Add date filtering (start_date, end_date)
3. Create search functionality for addresses
4. Add sorting parameters (sort_by, sort_order)
5. Validate all parameters with Pydantic

### Step 3: Database Query Optimization
1. Create efficient SQLAlchemy queries
2. Implement proper filtering logic
3. Add database-level pagination
4. Optimize with proper indexes
5. Test query performance

### Step 4: Response Formatting
1. Create HistoryResponse model
2. Implement pagination metadata
3. Format individual items consistently
4. Add query performance metrics
5. Test JSON serialization

### Step 5: Testing and Performance
1. Create comprehensive test suite
2. Test all filtering and sorting combinations
3. Verify pagination accuracy
4. Test performance with large datasets
5. Add error handling tests

## 📝 Git Workflow Instructions

### Branch Strategy
- Work on `feature/sprint-06-history-api` branch
- Branch from `develop` after Sprint 5 is merged
- Follow conventional commit format

### Commit Process
1. Create feature branch: `git checkout develop && git pull && git checkout -b feature/sprint-06-history-api`
2. Implement systematically with tests
3. Test each feature as implemented
4. Commit regularly: `git commit -m "feat: implement GET /history endpoint with pagination and filtering"`
5. Push branch: `git push -u origin feature/sprint-06-history-api`

## 🔒 Security Requirements
- [ ] Input validation for all query parameters
- [ ] Prevent SQL injection in search functionality
- [ ] Limit maximum result set size
- [ ] Validate date ranges to prevent performance attacks
- [ ] Sanitize search terms

## 📊 Quality Gates
- [ ] All 5 test cases pass
- [ ] Endpoint responds within 2 seconds for reasonable queries
- [ ] Pagination works correctly with accurate metadata
- [ ] Filtering produces correct results
- [ ] Sorting works for all supported fields
- [ ] Database queries are optimized with proper indexes
- [ ] Code passes Black formatting and Flake8 linting
- [ ] Test coverage >= 85%

## 🎁 Deliverables
1. Complete GET /history endpoint with all features
2. Pagination with limit, offset, and metadata
3. Date range and search filtering capabilities
4. Sorting by timestamp, distance, and addresses
5. Optimized database queries with proper indexes
6. Comprehensive test suite covering all scenarios
7. Performance optimization for large datasets
8. Error handling for all edge cases

## 🚫 Exit Criteria
**This sprint is complete when:**
- All 5 test cases pass without errors
- GET /history endpoint returns paginated results correctly
- Filtering by date range and search works accurately
- Sorting by all supported fields works correctly
- Database queries are optimized and performant
- Error handling covers all validation scenarios
- Feature branch is ready for merge to develop

## 🔄 Next Sprint Preview
Sprint 7 will implement the SvelteKit frontend application with components for address input, results display, and integration with the backend API.