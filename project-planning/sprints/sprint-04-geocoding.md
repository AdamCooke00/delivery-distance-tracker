# Sprint 4: Geocoding Service Integration

> **📊 SPRINT STATUS: 🔄 PENDING** (Requires Sprint 2 + 3 completion)  
> **📚 COMPLETION TEMPLATE: Added below - use Sprint Completion Checklist when ready**  
> **🔗 DEPENDENCIES: Sprint 2 (Database) + Sprint 3 (FastAPI) must be complete**

## 🎯 Objective
Implement Nominatim API integration for address geocoding with comprehensive error handling, address validation, and robust testing including API mocking.

## 📋 Acceptance Criteria

### 1. Nominatim API Client Implementation
- [ ] Create `app/services/geocoding.py` with Nominatim API client
- [ ] Implement async HTTP client using httpx
- [ ] Configure proper user agent and request headers
- [ ] Set up rate limiting and retry logic
- [ ] Handle API timeouts and connection errors

### 2. Address Validation & Geocoding
- [ ] Create `app/utils/validation.py` for address validation
- [ ] Implement address format validation and sanitization
- [ ] Create geocoding request/response models with Pydantic
- [ ] Handle partial matches and ambiguous addresses
- [ ] Implement coordinate validation (latitude/longitude bounds)

### 3. Geocoding Service Layer
- [ ] Create service interface for geocoding operations
- [ ] Implement caching logic for geocoding results (in-memory for MVP)
- [ ] Add proper error handling for various API failure scenarios
- [ ] Create fallback mechanisms for API unavailability
- [ ] Implement logging for geocoding operations

### 4. Distance Calculation Utilities
- [ ] Create `app/utils/distance.py` with Haversine formula implementation
- [ ] Implement coordinate-to-distance calculation
- [ ] Add support for different distance units (km/miles)
- [ ] Validate coordinate inputs and handle edge cases
- [ ] Create utility functions for geographic calculations

### 5. Comprehensive Testing with Mocks
- [ ] Create mock responses for Nominatim API testing
- [ ] Implement unit tests for geocoding service
- [ ] Test error handling scenarios (API down, invalid responses)
- [ ] Create integration tests with actual API (optional/skippable)
- [ ] Test caching functionality and cache invalidation

### 6. README.md Documentation
- [ ] Update README.md to reflect current repository state
- [ ] Document prerequisites: Python 3.8+, Docker, Docker Compose
- [ ] Include complete setup instructions:
  - Clone repository steps
  - Virtual environment setup and activation
  - Dependencies installation including httpx for API calls
  - Database setup with Docker
  - Environment variables configuration including NOMINATIM_BASE_URL
  - FastAPI application startup
  - Testing geocoding service functionality
- [ ] Document geocoding service capabilities and API integration
- [ ] Include commands to run geocoding tests with and without integration tests

## 🧪 Test Cases That Must Pass

### Test Case 1: Address Validation
```python
# File: app/tests/test_address_validation.py
import pytest
from app.utils.validation import validate_address, sanitize_address

def test_valid_address_validation():
    """Test validation of properly formatted addresses"""
    valid_addresses = [
        "1600 Amphitheatre Parkway, Mountain View, CA, USA",
        "123 Main Street, New York, NY",
        "Big Ben, London, UK"
    ]
    
    for address in valid_addresses:
        assert validate_address(address) is True
        sanitized = sanitize_address(address)
        assert len(sanitized) > 0
        assert sanitized != address or address == sanitized
    
    print("✅ Valid address validation works")

def test_invalid_address_validation():
    """Test rejection of invalid addresses"""
    invalid_addresses = [
        "",
        "   ",
        "a",
        "123",
        None,
        "SELECT * FROM users",  # SQL injection attempt
        "<script>alert('xss')</script>",  # XSS attempt
    ]
    
    for address in invalid_addresses:
        assert validate_address(address) is False
    
    print("✅ Invalid address validation works")

def test_address_sanitization():
    """Test address sanitization removes dangerous content"""
    dangerous_addresses = [
        "123 Main St<script>alert('xss')</script>",
        "123 Main St'; DROP TABLE users; --",
        "123 Main St\n\r\t   "
    ]
    
    for address in dangerous_addresses:
        sanitized = sanitize_address(address)
        assert "<script>" not in sanitized
        assert "DROP TABLE" not in sanitized
        assert sanitized.strip() == sanitized
    
    print("✅ Address sanitization works")
```

### Test Case 2: Geocoding Service with Mocks
```python
# File: app/tests/test_geocoding_service.py
import pytest
from unittest.mock import AsyncMock, patch
from app.services.geocoding import GeocodingService, GeocodingError

@pytest.fixture
def geocoding_service():
    return GeocodingService()

@pytest.fixture
def mock_nominatim_response():
    return {
        "lat": "37.4224764",
        "lon": "-122.0842499",
        "display_name": "1600 Amphitheatre Parkway, Mountain View, CA, USA",
        "place_id": 123456,
        "importance": 0.8
    }

@patch('httpx.AsyncClient.get')
async def test_successful_geocoding(mock_get, geocoding_service, mock_nominatim_response):
    """Test successful geocoding of valid address"""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = [mock_nominatim_response]
    
    result = await geocoding_service.geocode_address("1600 Amphitheatre Parkway, Mountain View, CA")
    
    assert result is not None
    assert result.latitude == 37.4224764
    assert result.longitude == -122.0842499
    assert "1600 Amphitheatre Parkway" in result.display_name
    
    print("✅ Successful geocoding works")

@patch('httpx.AsyncClient.get')
async def test_geocoding_no_results(mock_get, geocoding_service):
    """Test geocoding when no results found"""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = []
    
    with pytest.raises(GeocodingError) as exc_info:
        await geocoding_service.geocode_address("Nonexistent Address 12345")
    
    assert "No results found" in str(exc_info.value)
    print("✅ No results error handling works")

@patch('httpx.AsyncClient.get')
async def test_geocoding_api_error(mock_get, geocoding_service):
    """Test geocoding when API returns error"""
    mock_get.return_value.status_code = 500
    mock_get.return_value.text = "Internal Server Error"
    
    with pytest.raises(GeocodingError) as exc_info:
        await geocoding_service.geocode_address("123 Main St")
    
    assert "API error" in str(exc_info.value)
    print("✅ API error handling works")

@patch('httpx.AsyncClient.get')
async def test_geocoding_timeout(mock_get, geocoding_service):
    """Test geocoding when API times out"""
    mock_get.side_effect = TimeoutError("Request timed out")
    
    with pytest.raises(GeocodingError) as exc_info:
        await geocoding_service.geocode_address("123 Main St")
    
    assert "timeout" in str(exc_info.value).lower()
    print("✅ Timeout error handling works")
```

### Test Case 3: Distance Calculation
```python
# File: app/tests/test_distance_calculation.py
import pytest
from app.utils.distance import calculate_distance, haversine_distance

def test_distance_calculation_known_locations():
    """Test distance calculation between known locations"""
    # Distance between NYC and Los Angeles (approximately 3944 km)
    nyc_lat, nyc_lng = 40.7128, -74.0060
    la_lat, la_lng = 34.0522, -118.2437
    
    distance = calculate_distance(nyc_lat, nyc_lng, la_lat, la_lng)
    
    # Allow 1% tolerance for calculation differences
    expected_distance = 3944
    assert abs(distance - expected_distance) < (expected_distance * 0.01)
    print("✅ Distance calculation for known locations accurate")

def test_distance_calculation_same_location():
    """Test distance calculation for same location"""
    lat, lng = 40.7128, -74.0060
    distance = calculate_distance(lat, lng, lat, lng)
    assert distance == 0.0
    print("✅ Same location distance calculation works")

def test_distance_calculation_invalid_coordinates():
    """Test distance calculation with invalid coordinates"""
    with pytest.raises(ValueError):
        calculate_distance(91.0, 0.0, 0.0, 0.0)  # Invalid latitude
    
    with pytest.raises(ValueError):
        calculate_distance(0.0, 181.0, 0.0, 0.0)  # Invalid longitude
    
    print("✅ Invalid coordinate validation works")

def test_haversine_formula_accuracy():
    """Test Haversine formula implementation accuracy"""
    # Test with specific coordinates where distance is known
    lat1, lng1 = 52.5200, 13.4050  # Berlin
    lat2, lng2 = 48.8566, 2.3522   # Paris
    
    distance = haversine_distance(lat1, lng1, lat2, lng2)
    expected_distance = 878  # Approximately 878 km
    
    assert abs(distance - expected_distance) < 10  # 10km tolerance
    print("✅ Haversine formula accuracy validated")
```

### Test Case 4: Geocoding Caching
```python
# File: app/tests/test_geocoding_cache.py
import pytest
from unittest.mock import AsyncMock, patch
from app.services.geocoding import GeocodingService

@pytest.fixture
def geocoding_service():
    return GeocodingService()

@patch('httpx.AsyncClient.get')
async def test_geocoding_cache_hit(mock_get, geocoding_service):
    """Test that repeated geocoding requests use cache"""
    mock_response = {
        "lat": "37.4224764",
        "lon": "-122.0842499", 
        "display_name": "Test Address",
        "place_id": 123456
    }
    
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = [mock_response]
    
    address = "123 Test Street"
    
    # First call should hit the API
    result1 = await geocoding_service.geocode_address(address)
    assert mock_get.call_count == 1
    
    # Second call should use cache
    result2 = await geocoding_service.geocode_address(address)
    assert mock_get.call_count == 1  # Should not increase
    
    # Results should be identical
    assert result1.latitude == result2.latitude
    assert result1.longitude == result2.longitude
    
    print("✅ Geocoding cache functionality works")

def test_cache_invalidation(geocoding_service):
    """Test cache invalidation functionality"""
    # Add item to cache
    cache_key = "test_address"
    geocoding_service._cache[cache_key] = {"lat": 1.0, "lng": 2.0}
    
    # Verify item is in cache
    assert cache_key in geocoding_service._cache
    
    # Clear cache
    geocoding_service.clear_cache()
    
    # Verify cache is empty
    assert len(geocoding_service._cache) == 0
    
    print("✅ Cache invalidation works")
```

### Test Case 5: Integration Test (Optional)
```python
# File: app/tests/test_geocoding_integration.py
import pytest
import os
from app.services.geocoding import GeocodingService

@pytest.mark.skipif(
    os.getenv("SKIP_INTEGRATION_TESTS") == "true",
    reason="Integration tests skipped"
)
@pytest.mark.asyncio
async def test_real_nominatim_api():
    """Test actual Nominatim API integration (optional)"""
    geocoding_service = GeocodingService()
    
    # Test with a well-known address
    result = await geocoding_service.geocode_address("1600 Amphitheatre Parkway, Mountain View, CA")
    
    assert result is not None
    assert result.latitude is not None
    assert result.longitude is not None
    assert "Mountain View" in result.display_name
    
    print("✅ Real Nominatim API integration works")
```

## 🔧 Implementation Steps

### Step 1: Geocoding Service Foundation
1. Create `app/services/geocoding.py` with base GeocodingService class
2. Set up httpx AsyncClient for API requests
3. Configure proper headers and user agent
4. Implement basic error handling structure
5. Add logging for all operations

### Step 2: Address Validation System
1. Create `app/utils/validation.py` with validation functions
2. Implement address format validation
3. Add sanitization for security (XSS, SQL injection prevention)
4. Create Pydantic models for geocoding requests/responses
5. Add coordinate validation utilities

### Step 3: Nominatim API Integration
1. Implement actual API calls to Nominatim
2. Handle various response formats and edge cases
3. Add retry logic with exponential backoff
4. Implement timeout handling
5. Create proper error mapping from API responses

### Step 4: Distance Calculation Implementation
1. Create `app/utils/distance.py` with Haversine formula
2. Implement coordinate validation
3. Add support for different units (km/miles)
4. Handle edge cases (same location, antipodal points)
5. Add geographic utility functions

### Step 5: Caching and Testing
1. Implement in-memory caching for geocoding results
2. Create comprehensive mock-based tests
3. Add integration test capability (optional)
4. Implement cache management utilities
5. Add performance monitoring

## 📝 Git Workflow Instructions

### Branch Strategy
- Work on `feature/sprint-04-geocoding` branch
- Branch from `develop` after Sprint 3 is merged
- Follow conventional commit format

### Commit Process
1. Create feature branch: `git checkout develop && git pull && git checkout -b feature/sprint-04-geocoding`
2. Implement components systematically
3. Write tests for each component before implementation
4. Commit frequently: `git commit -m "feat: implement Nominatim geocoding service"`
5. Push branch: `git push -u origin feature/sprint-04-geocoding`

## 🔒 Security Requirements
- [ ] Input sanitization prevents XSS and SQL injection
- [ ] No API keys or sensitive data in logs
- [ ] Proper user agent identification to Nominatim
- [ ] Rate limiting to respect API usage policies
- [ ] Coordinate validation prevents invalid data storage

## 📊 Quality Gates
- [ ] All 5 test cases pass
- [ ] Mock-based tests provide 100% coverage of service logic
- [ ] Address validation prevents malicious input
- [ ] Distance calculations are mathematically accurate
- [ ] Caching reduces API calls for repeated requests
- [ ] Error handling covers all failure scenarios
- [ ] Code passes Black formatting and Flake8 linting
- [ ] Integration test passes (if not skipped)

## 🎁 Deliverables
1. Complete geocoding service with Nominatim integration
2. Robust address validation and sanitization
3. Accurate distance calculation utilities
4. In-memory caching system for performance
5. Comprehensive error handling for all scenarios
6. Mock-based test suite with high coverage
7. Optional integration test capability
8. Performance monitoring and logging

## 🚫 Exit Criteria
**This sprint is complete when:**
- All 5 test cases pass without errors
- Geocoding service can handle valid addresses successfully
- Invalid addresses are properly rejected and sanitized
- Distance calculations are mathematically accurate
- Caching reduces redundant API calls
- Error handling gracefully manages all failure scenarios
- Feature branch is ready for merge to develop

## 📋 Sprint Completion Checklist

**Before marking sprint complete, verify:**
- [ ] All acceptance criteria checkboxes are marked ✅
- [ ] All 5 test cases pass without errors  
- [ ] All quality gates are met and marked ✅
- [ ] All security requirements are met and marked ✅
- [ ] Code passes Black formatting and Flake8 linting
- [ ] Test coverage >= 80%
- [ ] All files created/modified are documented in completion summary
- [ ] Completion summary added with date and key deliverables
- [ ] Feature branch committed with conventional format
- [ ] Ready for merge to develop

## 🔄 Next Sprint Preview
Sprint 5 will implement the POST /distance endpoint using the geocoding service, add database storage for queries, and create comprehensive endpoint testing with various scenarios.

---

## ✅ SPRINT 4 COMPLETION SUMMARY

**Completed On:** [DATE]  
**Status:** [ ] COMPLETE - All acceptance criteria and quality gates met

### Key Deliverables Achieved:
- [ ] **Nominatim API Client**: [Description]
- [ ] **Address Validation**: [Description]
- [ ] **Distance Calculation**: [Description]
- [ ] **Geocoding Testing**: [Description]

### Files Created/Modified:
**New Files Created ([X] files):**
- [ ] `app/services/geocoding.py` - [Description of purpose and functionality]
- [ ] `app/utils/validation.py` - [Description of purpose and functionality]
- [ ] `app/utils/distance.py` - [Description of purpose and functionality]
- [ ] `app/tests/test_geocoding.py` - [Description of test coverage]

**Files Modified ([X] files):**
- [ ] `requirements.txt` - [Add httpx and other dependencies]
- [ ] `README.md` - [Update with geocoding setup instructions]

### Test Results Summary:
- [ ] **[X]/[X] tests passing** across all test categories
- [ ] **Geocoding Tests** ([X] tests) - API client, validation, error handling
- [ ] **Distance Tests** ([X] tests) - Haversine formula, edge cases
- [ ] **Integration Tests** ([X] tests) - End-to-end geocoding workflow

### Quality Gates Achieved:
- [ ] All 5 Sprint 4 test cases pass without errors
- [ ] Geocoding service handles valid addresses successfully
- [ ] Invalid addresses properly rejected and sanitized
- [ ] Distance calculations mathematically accurate
- [ ] Caching reduces redundant API calls
- [ ] Error handling gracefully manages all failure scenarios

### Code Implementation Details:
- [ ] **API Client**: Async HTTP client with proper headers and rate limiting
- [ ] **Validation**: Address format validation and sanitization
- [ ] **Distance Calculation**: Haversine formula implementation with unit tests
- [ ] **Error Handling**: Comprehensive exception handling for API failures
- [ ] **Caching**: In-memory caching for geocoding results

### Security Compliance:
- [ ] No API keys hardcoded (use environment variables if needed)
- [ ] Input validation prevents injection attacks
- [ ] Rate limiting prevents API abuse
- [ ] Error messages don't expose internal details

### Notes:
- [Any deviations, decisions, or important implementation notes]

### Ready for Next Sprint:
Sprint 4 provides complete geocoding foundation for Sprint 5 distance endpoint implementation.