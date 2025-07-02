# Sprint 3: Core Backend API Framework

## 🎯 Objective
Create the FastAPI application foundation with proper project structure, implement basic routing, health check endpoint, and establish comprehensive error handling and logging patterns.

## 📋 Acceptance Criteria

### 1. FastAPI Application Setup
- [ ] Create `app/main.py` as the FastAPI application entry point
- [ ] Configure FastAPI with proper title, description, and version
- [ ] Set up CORS configuration for frontend integration
- [ ] Implement application startup and shutdown event handlers
- [ ] Configure automatic OpenAPI documentation

### 2. API Router Structure
- [ ] Create `app/api/__init__.py` for API module initialization
- [ ] Create `app/api/routes.py` with main router configuration
- [ ] Create `app/api/health.py` for health check endpoints
- [ ] Implement proper router organization and dependency injection
- [ ] Set up API versioning structure (v1)

### 3. Health Check Endpoint Implementation
- [ ] Implement `GET /health` endpoint with comprehensive health checks
- [ ] Include database connectivity check
- [ ] Include external API (Nominatim) connectivity check
- [ ] Return structured health status with proper HTTP codes
- [ ] Implement detailed health information for debugging

### 4. Error Handling & Validation
- [ ] Create `app/utils/exceptions.py` with custom exception classes
- [ ] Implement global exception handlers for common errors
- [ ] Set up Pydantic models for request/response validation
- [ ] Create proper HTTP status code responses
- [ ] Implement error logging with context information

### 5. Logging & Monitoring
- [ ] Create `app/utils/logging.py` with structured logging setup
- [ ] Configure log levels based on environment variables
- [ ] Implement request/response logging middleware
- [ ] Set up proper log formatting and output
- [ ] Create monitoring utilities for performance tracking

### 6. README.md Documentation
- [ ] Update README.md to reflect current repository state
- [ ] Document prerequisites: Python 3.8+, Docker, Docker Compose
- [ ] Include complete setup instructions:
  - Clone repository steps
  - Virtual environment setup and activation
  - Dependencies installation
  - Database setup with Docker
  - Environment variables configuration
  - FastAPI application startup with uvicorn app.main:app --reload
  - Health check endpoint verification at /health
- [ ] Document API endpoints and OpenAPI documentation access at /docs
- [ ] Include testing commands for the API framework

## 🧪 Test Cases That Must Pass

### Test Case 1: FastAPI Application Startup
```python
# File: app/tests/test_application.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_app_startup():
    """Test that FastAPI application starts correctly"""
    response = client.get("/docs")
    assert response.status_code == 200
    print("✅ FastAPI application starts successfully")

def test_openapi_documentation():
    """Test that OpenAPI documentation is accessible"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    openapi_schema = response.json()
    assert openapi_schema["info"]["title"] == "Delivery Distance Tracker API"
    print("✅ OpenAPI documentation accessible")
```

### Test Case 2: Health Check Endpoint
```python
# File: app/tests/test_health.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint_exists():
    """Test that health endpoint is accessible"""
    response = client.get("/health")
    assert response.status_code == 200
    print("✅ Health endpoint accessible")

def test_health_endpoint_response_structure():
    """Test health endpoint returns proper structure"""
    response = client.get("/health")
    data = response.json()
    
    required_fields = ["status", "timestamp", "checks"]
    for field in required_fields:
        assert field in data
    
    assert data["status"] in ["healthy", "unhealthy"]
    assert "database" in data["checks"]
    assert "nominatim_api" in data["checks"]
    print("✅ Health endpoint structure validated")

def test_database_health_check():
    """Test database connectivity in health check"""
    response = client.get("/health")
    data = response.json()
    
    db_check = data["checks"]["database"]
    assert "status" in db_check
    assert "response_time_ms" in db_check
    print("✅ Database health check working")

def test_nominatim_health_check():
    """Test Nominatim API connectivity in health check"""
    response = client.get("/health")
    data = response.json()
    
    api_check = data["checks"]["nominatim_api"]
    assert "status" in api_check
    assert "response_time_ms" in api_check
    print("✅ Nominatim API health check working")
```

### Test Case 3: Error Handling
```python
# File: app/tests/test_error_handling.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_404_error_handling():
    """Test 404 error handling"""
    response = client.get("/nonexistent-endpoint")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    print("✅ 404 error handling works")

def test_validation_error_handling():
    """Test request validation error handling"""
    # This will be more relevant in later sprints with actual endpoints
    response = client.post("/distance", json={"invalid": "data"})
    assert response.status_code in [404, 422]  # 404 until endpoint exists, 422 after
    print("✅ Validation error handling works")

def test_internal_server_error_handling():
    """Test internal server error handling"""
    # Test that 500 errors are properly handled and logged
    # This requires creating a test endpoint that raises an exception
    pass  # Implementation depends on test endpoint creation
```

### Test Case 4: CORS Configuration
```python
# File: app/tests/test_cors.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_cors_headers():
    """Test CORS headers are properly set"""
    response = client.options("/health", headers={
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "GET"
    })
    
    assert "access-control-allow-origin" in response.headers
    assert "access-control-allow-methods" in response.headers
    print("✅ CORS configuration working")
```

### Test Case 5: Logging Configuration
```python
# File: app/tests/test_logging.py
import pytest
import logging
from app.utils.logging import setup_logging, get_logger

def test_logging_setup():
    """Test logging configuration"""
    setup_logging()
    logger = get_logger(__name__)
    
    assert logger.level == logging.INFO
    assert len(logger.handlers) > 0
    print("✅ Logging configuration working")

def test_request_logging():
    """Test request logging middleware"""
    from fastapi.testclient import TestClient
    from app.main import app
    
    client = TestClient(app)
    
    # Make a request and verify it gets logged
    response = client.get("/health")
    assert response.status_code == 200
    
    # In a real implementation, we'd check log output
    # For now, just verify the middleware doesn't break anything
    print("✅ Request logging middleware working")
```

## 🔧 Implementation Steps

### Step 1: FastAPI Application Foundation
1. Create `app/main.py` with FastAPI app initialization
2. Configure CORS settings for frontend integration
3. Set up application metadata (title, description, version)
4. Configure automatic OpenAPI documentation
5. Add startup and shutdown event handlers

### Step 2: Router Structure Implementation
1. Create `app/api/__init__.py` and `app/api/routes.py`
2. Set up API versioning with `/api/v1` prefix
3. Create router organization for future endpoints
4. Implement dependency injection patterns
5. Configure proper error propagation

### Step 3: Health Check Endpoint
1. Create `app/api/health.py` with comprehensive health checks
2. Implement database connectivity testing
3. Add Nominatim API connectivity testing
4. Create structured health response format
5. Set up proper HTTP status codes

### Step 4: Error Handling System
1. Create `app/utils/exceptions.py` with custom exceptions
2. Implement global exception handlers
3. Set up Pydantic models for error responses
4. Create proper HTTP status code mapping
5. Add error context logging

### Step 5: Logging & Monitoring
1. Create `app/utils/logging.py` with structured logging
2. Set up environment-based log levels
3. Implement request/response logging middleware
4. Configure log formatting and output
5. Add performance monitoring utilities

## 📝 Git Workflow Instructions

### Branch Strategy
- Work on `feature/sprint-03-api-framework` branch
- Branch from `develop` after Sprint 2 is merged
- Follow conventional commit format

### Commit Process
1. Create feature branch: `git checkout develop && git pull && git checkout -b feature/sprint-03-api-framework`
2. Implement each acceptance criteria systematically
3. Run tests after each major component
4. Commit incrementally: `git commit -m "feat: implement FastAPI application foundation"`
5. Push branch: `git push -u origin feature/sprint-03-api-framework`

## 🔒 Security Requirements
- [ ] CORS properly configured for frontend domain only
- [ ] No sensitive information in logs
- [ ] Proper error message sanitization (no internal details exposed)
- [ ] Environment variables for all configuration
- [ ] Input validation on all endpoints

## 📊 Quality Gates
- [ ] All 5 test cases pass
- [ ] FastAPI application starts without errors
- [ ] Health endpoint returns comprehensive status
- [ ] OpenAPI documentation is accessible and accurate
- [ ] Error handling works for all common scenarios
- [ ] Logging configuration is environment-appropriate
- [ ] Code passes Black formatting and Flake8 linting
- [ ] Test coverage >= 80%

## 🎁 Deliverables
1. Complete FastAPI application with proper configuration
2. Structured API routing with versioning
3. Comprehensive health check endpoint
4. Global error handling system
5. Structured logging and monitoring setup
6. OpenAPI documentation generation
7. Test suite covering all core functionality
8. CORS configuration for frontend integration

## 🚫 Exit Criteria
**This sprint is complete when:**
- All 5 test cases pass without errors
- FastAPI application can be started with `uvicorn app.main:app --reload`
- Health endpoint provides accurate system status
- Error handling gracefully manages all error types
- Logging provides appropriate information for debugging
- OpenAPI docs are accessible at `/docs`
- Feature branch is ready for merge to develop

## 🔄 Next Sprint Preview
Sprint 4 will integrate the Nominatim geocoding service, implement address validation and geocoding logic, and create comprehensive unit tests for the geocoding functionality.