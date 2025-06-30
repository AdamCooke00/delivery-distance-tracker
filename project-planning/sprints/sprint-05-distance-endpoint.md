# Sprint 5: Distance Calculation & Storage

> **📊 SPRINT STATUS: 🔄 PENDING** (Requires Sprint 2 + 3 + 4 completion)  
> **📚 COMPLETION TEMPLATE: Added below - use Sprint Completion Checklist when ready**  
> **🔗 DEPENDENCIES: Sprint 2 (Database) + Sprint 3 (FastAPI) + Sprint 4 (Geocoding) must be complete**

## 🎯 Objective
Implement the POST /distance endpoint that geocodes addresses, calculates distances, stores queries in the database, and returns structured responses with comprehensive error handling.

## 📋 Acceptance Criteria

### 1. Distance Endpoint Implementation
- [ ] Create `app/api/distance.py` with POST /distance endpoint
- [ ] Implement Pydantic request/response models
- [ ] Integrate geocoding service for address processing
- [ ] Calculate distance between geocoded coordinates
- [ ] Return structured JSON response with all required fields

### 2. Request/Response Models
- [ ] Create `app/models/schemas.py` with Pydantic schemas
- [ ] Implement `DistanceRequest` model with validation
- [ ] Create `DistanceResponse` model with proper field types
- [ ] Add `GeocodingResult` model for coordinate data
- [ ] Implement proper error response models

### 3. Database Integration
- [ ] Store each distance query in the distance_queries table
- [ ] Save source/destination addresses and coordinates
- [ ] Record calculated distance and timestamp
- [ ] Implement proper database session management
- [ ] Add database error handling and rollback logic

### 4. Business Logic Implementation
- [ ] Create `app/services/distance_service.py` for business logic
- [ ] Integrate geocoding service with distance calculation
- [ ] Implement end-to-end distance query processing
- [ ] Add validation for geocoding results
- [ ] Handle partial geocoding failures gracefully

### 5. Comprehensive Error Handling
- [ ] Handle invalid address formats
- [ ] Manage geocoding API failures
- [ ] Process database connection errors
- [ ] Return appropriate HTTP status codes
- [ ] Provide user-friendly error messages

### 6. README.md Documentation
- [ ] Update README.md to reflect current repository state
- [ ] Document prerequisites: Python 3.8+, Docker, Docker Compose
- [ ] Include complete setup instructions:
  - Clone repository steps
  - Virtual environment setup and activation
  - Dependencies installation
  - Database setup with Docker and schema initialization
  - Environment variables configuration for database and Nominatim API
  - FastAPI application startup
  - API endpoint testing with curl or HTTP client
- [ ] Document POST /distance endpoint usage with request/response examples
- [ ] Include commands to test the distance calculation endpoint

## 🧪 Test Cases That Must Pass

### Test Case 1: Successful Distance Calculation
```python
# File: app/tests/test_distance_endpoint.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app

client = TestClient(app)

@patch('app.services.geocoding.GeocodingService.geocode_address')
async def test_successful_distance_calculation(mock_geocode):
    """Test successful distance calculation between two addresses"""
    # Mock geocoding responses
    mock_geocode.side_effect = [
        AsyncMock(latitude=37.4224764, longitude=-122.0842499, display_name="1600 Amphitheatre Parkway, Mountain View, CA"),
        AsyncMock(latitude=37.3349, longitude=-122.009, display_name="1 Apple Park Way, Cupertino, CA")
    ]
    
    request_data = {
        "source": "1600 Amphitheatre Parkway, Mountain View, CA",
        "destination": "1 Apple Park Way, Cupertino, CA"
    }
    
    response = client.post("/api/v1/distance", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    required_fields = ["distance_km", "source_coords", "destination_coords", "timestamp"]
    for field in required_fields:
        assert field in data
    
    # Verify data types and ranges
    assert isinstance(data["distance_km"], (int, float))
    assert data["distance_km"] > 0
    assert len(data["source_coords"]) == 2
    assert len(data["destination_coords"]) == 2
    assert data["timestamp"] is not None
    
    print("✅ Successful distance calculation works")

@patch('app.services.geocoding.GeocodingService.geocode_address')
async def test_distance_calculation_same_location(mock_geocode):
    """Test distance calculation for same location returns 0"""
    # Mock same geocoding response for both addresses
    same_location = AsyncMock(latitude=37.4224764, longitude=-122.0842499, display_name="Same Location")
    mock_geocode.side_effect = [same_location, same_location]
    
    request_data = {
        "source": "Same Location",
        "destination": "Same Location"
    }
    
    response = client.post("/api/v1/distance", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["distance_km"] == 0.0
    
    print("✅ Same location distance calculation works")
```

### Test Case 2: Request Validation
```python
# File: app/tests/test_distance_validation.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_missing_source_address():
    """Test validation error when source address is missing"""
    request_data = {
        "destination": "123 Main St, City, State"
    }
    
    response = client.post("/api/v1/distance", json=request_data)
    assert response.status_code == 422
    
    data = response.json()
    assert "detail" in data
    assert any("source" in str(error) for error in data["detail"])
    
    print("✅ Missing source address validation works")

def test_missing_destination_address():
    """Test validation error when destination address is missing"""
    request_data = {
        "source": "123 Main St, City, State"
    }
    
    response = client.post("/api/v1/distance", json=request_data)
    assert response.status_code == 422
    
    data = response.json()
    assert "detail" in data
    assert any("destination" in str(error) for error in data["detail"])
    
    print("✅ Missing destination address validation works")

def test_empty_addresses():
    """Test validation error for empty addresses"""
    request_data = {
        "source": "",
        "destination": ""
    }
    
    response = client.post("/api/v1/distance", json=request_data)
    assert response.status_code == 422
    
    print("✅ Empty address validation works")

def test_invalid_json():
    """Test error handling for invalid JSON"""
    response = client.post("/api/v1/distance", data="invalid json")
    assert response.status_code == 422
    
    print("✅ Invalid JSON handling works")

def test_malicious_input_handling():
    """Test security validation for malicious input"""
    malicious_inputs = [
        {"source": "<script>alert('xss')</script>", "destination": "123 Main St"},
        {"source": "'; DROP TABLE users; --", "destination": "123 Main St"},
        {"source": "123 Main St", "destination": "\n\r\t<iframe src='evil.com'>"}
    ]
    
    for malicious_data in malicious_inputs:
        response = client.post("/api/v1/distance", json=malicious_data)
        # Should either reject (422) or sanitize and process
        assert response.status_code in [422, 200]
        
        if response.status_code == 200:
            # If processed, ensure malicious content was sanitized
            data = response.json()
            response_str = str(data)
            assert "<script>" not in response_str
            assert "DROP TABLE" not in response_str
            assert "<iframe>" not in response_str
    
    print("✅ Malicious input handling works")
```

### Test Case 3: Geocoding Error Handling
```python
# File: app/tests/test_distance_geocoding_errors.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app
from app.services.geocoding import GeocodingError

client = TestClient(app)

@patch('app.services.geocoding.GeocodingService.geocode_address')
async def test_source_address_not_found(mock_geocode):
    """Test error when source address cannot be geocoded"""
    mock_geocode.side_effect = [
        GeocodingError("No results found for address"),
        AsyncMock(latitude=37.3349, longitude=-122.009, display_name="Valid Address")
    ]
    
    request_data = {
        "source": "Nonexistent Address 12345",
        "destination": "1 Apple Park Way, Cupertino, CA"
    }
    
    response = client.post("/api/v1/distance", json=request_data)
    assert response.status_code == 400
    
    data = response.json()
    assert "error" in data
    assert "source" in data["error"].lower()
    
    print("✅ Source address not found error handling works")

@patch('app.services.geocoding.GeocodingService.geocode_address')
async def test_destination_address_not_found(mock_geocode):
    """Test error when destination address cannot be geocoded"""
    mock_geocode.side_effect = [
        AsyncMock(latitude=37.4224764, longitude=-122.0842499, display_name="Valid Address"),
        GeocodingError("No results found for address")
    ]
    
    request_data = {
        "source": "1600 Amphitheatre Parkway, Mountain View, CA",
        "destination": "Nonexistent Address 12345"
    }
    
    response = client.post("/api/v1/distance", json=request_data)
    assert response.status_code == 400
    
    data = response.json()
    assert "error" in data
    assert "destination" in data["error"].lower()
    
    print("✅ Destination address not found error handling works")

@patch('app.services.geocoding.GeocodingService.geocode_address')
async def test_geocoding_api_unavailable(mock_geocode):
    """Test error when geocoding API is unavailable"""
    mock_geocode.side_effect = GeocodingError("API timeout")
    
    request_data = {
        "source": "123 Main St",
        "destination": "456 Oak Ave"
    }
    
    response = client.post("/api/v1/distance", json=request_data)
    assert response.status_code == 503
    
    data = response.json()
    assert "error" in data
    assert "service unavailable" in data["error"].lower() or "timeout" in data["error"].lower()
    
    print("✅ Geocoding API unavailable error handling works")
```

### Test Case 4: Database Integration
```python
# File: app/tests/test_distance_database.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from sqlalchemy.orm import Session
from app.main import app
from app.models.distance_query import DistanceQuery
from app.models.database import SessionLocal

client = TestClient(app)

@patch('app.services.geocoding.GeocodingService.geocode_address')
async def test_distance_query_stored_in_database(mock_geocode):
    """Test that distance queries are properly stored in database"""
    # Mock geocoding responses
    mock_geocode.side_effect = [
        AsyncMock(latitude=40.7128, longitude=-74.0060, display_name="New York, NY"),
        AsyncMock(latitude=34.0522, longitude=-118.2437, display_name="Los Angeles, CA")
    ]
    
    # Get initial count of records
    db = SessionLocal()
    initial_count = db.query(DistanceQuery).count()
    db.close()
    
    request_data = {
        "source": "New York, NY",
        "destination": "Los Angeles, CA"
    }
    
    response = client.post("/api/v1/distance", json=request_data)
    assert response.status_code == 200
    
    # Verify record was added to database
    db = SessionLocal()
    final_count = db.query(DistanceQuery).count()
    assert final_count == initial_count + 1
    
    # Verify stored data
    latest_query = db.query(DistanceQuery).order_by(DistanceQuery.created_at.desc()).first()
    assert latest_query.source_address == "New York, NY"
    assert latest_query.destination_address == "Los Angeles, CA"
    assert latest_query.source_lat == 40.7128
    assert latest_query.source_lng == -74.0060
    assert latest_query.destination_lat == 34.0522
    assert latest_query.destination_lng == -118.2437
    assert latest_query.distance_km > 0
    assert latest_query.created_at is not None
    
    db.close()
    print("✅ Distance query database storage works")

@patch('app.services.geocoding.GeocodingService.geocode_address')
async def test_database_error_handling(mock_geocode):
    """Test handling of database errors during storage"""
    mock_geocode.side_effect = [
        AsyncMock(latitude=40.7128, longitude=-74.0060, display_name="New York, NY"),
        AsyncMock(latitude=34.0522, longitude=-118.2437, display_name="Los Angeles, CA")
    ]
    
    request_data = {
        "source": "New York, NY",
        "destination": "Los Angeles, CA"
    }
    
    # Mock database error
    with patch('app.models.database.SessionLocal') as mock_session:
        mock_session.return_value.__enter__.return_value.commit.side_effect = Exception("Database error")
        
        response = client.post("/api/v1/distance", json=request_data)
        assert response.status_code == 500
        
        data = response.json()
        assert "error" in data
    
    print("✅ Database error handling works")
```

### Test Case 5: End-to-End Integration
```python
# File: app/tests/test_distance_e2e.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.mark.skipif(
    os.getenv("SKIP_E2E_TESTS") == "true",
    reason="End-to-end tests skipped"
)
def test_complete_distance_calculation_flow():
    """Test complete flow from request to response with real geocoding"""
    request_data = {
        "source": "Empire State Building, New York, NY",
        "destination": "Statue of Liberty, New York, NY"
    }
    
    response = client.post("/api/v1/distance", json=request_data)
    
    if response.status_code == 200:
        data = response.json()
        
        # Verify response structure
        assert "distance_km" in data
        assert "source_coords" in data
        assert "destination_coords" in data
        assert "timestamp" in data
        
        # Verify reasonable distance (should be around 8-10 km)
        assert 5 <= data["distance_km"] <= 15
        
        print("✅ End-to-end distance calculation works")
    else:
        # If geocoding fails, that's acceptable for this test
        print("⚠️ End-to-end test skipped due to geocoding service unavailability")
```

## 🔧 Implementation Steps

### Step 1: Request/Response Models
1. Create `app/models/schemas.py` with Pydantic models
2. Implement `DistanceRequest` with proper validation
3. Create `DistanceResponse` with all required fields
4. Add error response models
5. Test model validation thoroughly

### Step 2: Distance Service Layer
1. Create `app/services/distance_service.py`
2. Integrate geocoding service with distance calculation
3. Implement business logic for complete flow
4. Add comprehensive error handling
5. Create service-level tests

### Step 3: API Endpoint Implementation
1. Create `app/api/distance.py` with POST endpoint
2. Integrate request validation and response formatting
3. Connect service layer with API layer
4. Implement proper HTTP status codes
5. Add endpoint documentation

### Step 4: Database Integration
1. Update database models if needed
2. Implement database storage in service layer
3. Add transaction management and rollback logic
4. Create database session management
5. Test database operations thoroughly

### Step 5: Error Handling & Testing
1. Implement comprehensive error handling
2. Create all test cases with proper mocking
3. Add integration tests
4. Verify error responses and status codes
5. Test edge cases and security scenarios

## 📝 Git Workflow Instructions

### Branch Strategy
- Work on `feature/sprint-05-distance-endpoint` branch
- Branch from `develop` after Sprint 4 is merged
- Follow conventional commit format

### Commit Process
1. Create feature branch: `git checkout develop && git pull && git checkout -b feature/sprint-05-distance-endpoint`
2. Implement components in logical order
3. Write tests before implementation (TDD approach)
4. Commit frequently: `git commit -m "feat: implement POST /distance endpoint with database storage"`
5. Push branch: `git push -u origin feature/sprint-05-distance-endpoint`

## 🔒 Security Requirements
- [ ] Input validation prevents injection attacks
- [ ] Address sanitization in all processing
- [ ] Proper error message sanitization
- [ ] Database operations use parameterized queries
- [ ] No sensitive data in error responses or logs

## 📊 Quality Gates
- [ ] All 5 test cases pass
- [ ] Endpoint handles all success scenarios correctly
- [ ] Validation rejects all invalid input formats
- [ ] Error handling covers all failure scenarios
- [ ] Database storage works reliably
- [ ] Response format matches API specification
- [ ] Code passes Black formatting and Flake8 linting
- [ ] Test coverage >= 85%

## 🎁 Deliverables
1. Complete POST /distance endpoint implementation
2. Pydantic request/response models with validation
3. Distance service with geocoding integration
4. Database storage for all distance queries
5. Comprehensive error handling for all scenarios
6. Complete test suite with mocking and integration tests
7. API documentation with OpenAPI schemas
8. Security validation for all inputs

## 🚫 Exit Criteria
**This sprint is complete when:**
- All 5 test cases pass without errors
- POST /distance endpoint accepts valid requests and returns proper responses
- Invalid requests are properly validated and rejected
- Geocoding errors are handled gracefully with appropriate status codes
- All distance queries are stored in the database correctly
- Error handling covers all identified failure scenarios
- Feature branch is ready for merge to develop

## 🔄 Next Sprint Preview
Sprint 6 will implement the GET /history endpoint to retrieve past distance queries with pagination, filtering, and sorting capabilities.