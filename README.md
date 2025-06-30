# Delivery Distance Tracker

A FastAPI + SvelteKit application for calculating distances between delivery addresses using geocoding services.

## 🎯 Project Overview

This application allows users to:
- Calculate distances between two addresses
- Store and retrieve calculation history
- Access a clean, responsive web interface
- View paginated query history with search capabilities

## 🛠️ Technology Stack

- **Backend**: FastAPI with Python 3.8+
- **Frontend**: SvelteKit with TypeScript
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Geocoding**: Nominatim (OpenStreetMap)
- **Containerization**: Docker & Docker Compose
- **Testing**: pytest (backend), Jest (frontend), Playwright (E2E)

## 📋 Prerequisites

- Python 3.8 or higher
- Git
- Docker & Docker Compose
- Node.js 16+ (for frontend development)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/AdamCooke00/delivery-distance-tracker.git
cd delivery-distance-tracker
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 3. Set Up Database with Docker

```bash
# Start PostgreSQL database
cd docker
docker-compose up -d postgres

# Verify database is running
docker-compose ps
docker-compose logs postgres | grep "database system is ready"
```

### 4. Configure Environment Variables

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your configuration
# DATABASE_URL=postgresql://delivery_user:delivery_password@localhost:5432/delivery_tracker
# POSTGRES_USER=delivery_user
# POSTGRES_PASSWORD=delivery_password
# POSTGRES_DB=delivery_tracker
# NOMINATIM_BASE_URL=https://nominatim.openstreetmap.org
# CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
# LOG_LEVEL=INFO
```

### 5. Initialize Database Schema

```bash
# Activate virtual environment
source venv/bin/activate

# Initialize database tables
python3 -c "
from app.utils.database import initialize_database
success, message = initialize_database()
print(f'Database initialization: {message}')
"

# Verify database health
python3 -c "
from app.utils.database import check_database_health
healthy, message = check_database_health()
print(f'Database health: {message}')
"
```

### 6. Verify Installation

```bash
# Check Python environment
source venv/bin/activate
python --version
pip list | grep fastapi

# Run code quality checks
black --check .
flake8 .
```

## 🧪 Development Workflow

### Database Operations

```bash
# Start database
cd docker && docker-compose up -d postgres

# Stop database
cd docker && docker-compose down

# View database logs
cd docker && docker-compose logs postgres

# Reset database (removes all data)
cd docker && docker-compose down -v && docker-compose up -d postgres
```

### Testing

```bash
# Run all tests
source venv/bin/activate
pytest app/tests/ -v

# Run database tests specifically
pytest app/tests/test_database_*.py -v

# Run FastAPI application tests
pytest app/tests/test_application.py -v
pytest app/tests/test_health.py -v
pytest app/tests/test_error_handling.py -v
pytest app/tests/test_cors.py -v
pytest app/tests/test_logging.py -v

# Run geocoding and distance calculation tests (Sprint 4)
pytest app/tests/test_address_validation.py -v
pytest app/tests/test_distance_calculation.py -v
pytest app/tests/test_geocoding_service.py -v
pytest app/tests/test_geocoding_reliability.py -v
pytest app/tests/test_geocoding_integration.py -v

# Run distance endpoint tests (Sprint 5)
pytest app/tests/test_distance_endpoint.py -v
pytest app/tests/test_distance_validation.py -v
pytest app/tests/test_distance_geocoding_errors.py -v
pytest app/tests/test_distance_database.py -v
pytest app/tests/test_distance_e2e.py -v

# Run end-to-end tests with real APIs (optional)
SKIP_E2E_TESTS=false pytest app/tests/test_distance_e2e.py -v

# Run tests with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest app/tests/test_environment.py -v
```

### Code Quality Tools

```bash
# Format code with Black
black .

# Lint with Flake8
flake8 .

# Check code quality (run before commits)
black --check . && flake8 .
```

### Git Workflow

```bash
# Work on feature branches
git checkout develop
git checkout -b feature/your-feature-name

# Follow conventional commits
git commit -m "feat: add new feature"
git commit -m "fix: resolve bug"
git commit -m "docs: update documentation"

# Push and create PR
git push -u origin feature/your-feature-name
```

## 📁 Project Structure

```
/
├── app/                    # Backend FastAPI application
│   ├── api/               # REST endpoint definitions
│   ├── models/            # Database models and schemas
│   ├── services/          # Business logic (geocoding service)
│   ├── utils/             # Helper functions (validation, distance calc, logging)
│   └── tests/             # Unit and integration tests
├── frontend/              # SvelteKit application
├── docker/                # Container configurations
├── project-planning/      # Sprint documentation and planning
├── requirements.txt       # Python dependencies
├── requirements-dev.txt   # Development dependencies
├── .env.example          # Environment variables template
├── pyproject.toml        # Black and coverage configuration
├── .flake8               # Flake8 linting configuration
└── pytest.ini            # pytest configuration
```

## 🎯 API Endpoints

### Current Endpoints (Sprints 1-5)

- `GET /` - Root endpoint with API information
- `GET /api/v1/health` - Comprehensive health check
  - Returns system status, database connectivity, and external API status
- `GET /api/v1/health/database` - Database-specific health check
- `GET /api/v1/health/nominatim` - Nominatim API-specific health check
- `GET /docs` - Interactive OpenAPI documentation (Swagger UI)
- `GET /redoc` - ReDoc API documentation
- `GET /openapi.json` - OpenAPI schema

### Distance Calculation Endpoint (Sprint 5)

#### `POST /api/v1/distance` - Calculate Distance Between Addresses

Calculate the distance between two addresses using geocoding and the Haversine formula.

**Request Body:**
```json
{
  "source_address": "1600 Amphitheatre Parkway, Mountain View, CA",
  "destination_address": "1 Apple Park Way, Cupertino, CA"
}
```

**Response (200 OK):**
```json
{
  "id": 123,
  "source_address": "1600 Amphitheatre Parkway, Mountain View, CA",
  "destination_address": "1 Apple Park Way, Cupertino, CA",
  "source_lat": 37.4224764,
  "source_lng": -122.0842499,
  "destination_lat": 37.3349,
  "destination_lng": -122.009,
  "source_coords": [37.4224764, -122.0842499],
  "destination_coords": [37.3349, -122.009],
  "distance_km": 11.2,
  "created_at": "2025-06-30T10:30:45.123456"
}
```

**Error Responses:**
- `400 Bad Request` - Address not found during geocoding
- `422 Unprocessable Entity` - Invalid request format or validation error
- `503 Service Unavailable` - Geocoding service unavailable
- `500 Internal Server Error` - Database or internal system error

**Example with curl:**
```bash
curl -X POST "http://localhost:8000/api/v1/distance" \
     -H "Content-Type: application/json" \
     -d '{
       "source_address": "Empire State Building, New York, NY",
       "destination_address": "Statue of Liberty, New York, NY"
     }'
```

### Geocoding & Distance Services (Sprint 4)

The application includes comprehensive geocoding and distance calculation capabilities:

- **Address Validation**: Input sanitization and validation preventing XSS/SQL injection
- **Nominatim Geocoding**: Async API client with rate limiting and error handling
- **Distance Calculation**: Haversine formula with support for km/miles units
- **Geographic Utilities**: Bearing calculation, bounding boxes, coordinate validation

### Future Endpoints (Coming in Next Sprints)

- `GET /api/v1/history` - Retrieve past queries (paginated) (Sprint 6)

## 🔧 Development Commands

```bash
# Complete setup from scratch
git clone https://github.com/AdamCooke00/delivery-distance-tracker.git
cd delivery-distance-tracker
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt requirements-dev.txt
cp .env.example .env
cd docker && docker-compose up -d postgres && cd ..
python3 -c "from app.utils.database import initialize_database; print(initialize_database())"

# Start FastAPI backend development server
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Access the API
# - API Root: http://localhost:8000/
# - Health Check: http://localhost:8000/api/v1/health
# - API Documentation: http://localhost:8000/docs
# - ReDoc Documentation: http://localhost:8000/redoc

# Start frontend development server (when implemented)
cd frontend
npm run dev

# Database health check
python3 -c "from app.utils.database import check_database_health; print(check_database_health())"
```

## 🗄️ Database Schema

The application uses PostgreSQL with the following main table:

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

-- Performance indexes
CREATE INDEX idx_distance_queries_created_at ON distance_queries(created_at);
CREATE INDEX idx_distance_queries_addresses ON distance_queries(source_address, destination_address);
```

## 🤝 Contributing

1. Follow the 8-sprint development approach outlined in `project-planning/sprints/`
2. Complete acceptance criteria before moving to the next sprint
3. Maintain 80%+ test coverage
4. Use conventional commit messages
5. Update documentation as needed

## 📞 Support

- Review sprint documentation in `project-planning/sprints/`
- Check test cases for validation examples
- Refer to `project-planning/stack-decision.md` for architectural decisions

## 📝 License

This project is part of the Bain assessment and is for educational purposes.