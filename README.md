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
- Node.js 18+ and npm (for frontend development)
- Git
- Docker & Docker Compose

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
# CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173
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

### 6. Set Up Frontend

```bash
# Install frontend dependencies
cd frontend
npm install

# Verify frontend setup
npm run build
npm run lint

# Return to root directory
cd ..
```

### 7. Verify Installation

```bash
# Check Python environment
source venv/bin/activate
python --version
pip list | grep fastapi

# Check frontend environment
cd frontend
node --version
npm --version
cd ..

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

# Run history endpoint tests (Sprint 6)
pytest app/tests/test_history_endpoint.py -v
pytest app/tests/test_history_filtering.py -v
pytest app/tests/test_history_sorting.py -v
pytest app/tests/test_history_validation.py -v
pytest app/tests/test_history_performance.py -v
pytest app/tests/test_history_security.py -v

# Run end-to-end tests with real APIs (optional)
SKIP_E2E_TESTS=false pytest app/tests/test_distance_e2e.py -v

# Run tests with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest app/tests/test_environment.py -v
```

### Frontend Development

```bash
# Start frontend development server
cd frontend
npm run dev
# Access at: http://localhost:5173

# Run frontend tests
npm test
npm run test:ui  # Interactive test UI

# Frontend code quality
npm run lint     # ESLint
npm run format   # Prettier formatting

# Build for production
npm run build
npm run preview  # Preview production build

# Return to root directory
cd ..
```

### Code Quality Tools

```bash
# Backend code quality
black .          # Format code with Black
flake8 .         # Lint with Flake8
black --check . && flake8 .  # Check before commits

# Frontend code quality
cd frontend
npm run lint     # ESLint checking
npm run format   # Prettier formatting
cd ..

# Full project quality check
black --check . && flake8 . && cd frontend && npm run lint && cd ..
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
│   │   ├── distance.py    # Distance calculation endpoint
│   │   ├── health.py      # Health check endpoints
│   │   ├── history.py     # Query history endpoint
│   │   └── routes.py      # Main router configuration
│   ├── models/            # Database models and schemas
│   │   ├── database.py    # SQLAlchemy configuration
│   │   └── distance_query.py # Distance query model & schemas
│   ├── services/          # Business logic (geocoding service)
│   │   ├── distance_service.py # Distance calculation service
│   │   └── geocoding.py   # Nominatim geocoding service
│   ├── utils/             # Helper functions (validation, distance calc, logging)
│   └── tests/             # Unit and integration tests
├── frontend/              # SvelteKit frontend application
│   ├── src/               # Source code
│   │   ├── lib/           # Shared components and utilities
│   │   │   ├── components/ # Reusable UI components
│   │   │   ├── services/  # API service layer
│   │   │   │   └── api.ts # Type-safe API client
│   │   │   └── utils/     # Frontend utilities
│   │   ├── routes/        # SvelteKit file-based routing
│   │   │   ├── +layout.svelte    # Main layout component
│   │   │   ├── +page.svelte      # Distance calculator page
│   │   │   └── history/          # History page route
│   │   │       └── +page.svelte  # Historical queries view
│   │   ├── app.css        # Global styles with TailwindCSS
│   │   ├── app.html       # HTML template
│   │   └── test-setup.ts  # Test configuration
│   ├── static/            # Static assets
│   ├── package.json       # Frontend dependencies
│   ├── svelte.config.js   # SvelteKit configuration
│   ├── tailwind.config.js # TailwindCSS configuration
│   ├── tsconfig.json      # TypeScript configuration
│   ├── vite.config.ts     # Vite bundler configuration
│   └── vitest.config.ts   # Vitest testing configuration
├── docker/                # Container configurations
│   ├── docker-compose.yml # PostgreSQL database setup
│   └── init.sql          # Database schema initialization
├── project-planning/      # Sprint documentation and planning
├── requirements.txt       # Python dependencies
├── requirements-dev.txt   # Development dependencies
├── .env.example          # Environment variables template
├── pyproject.toml        # Black and coverage configuration
├── .flake8               # Flake8 linting configuration
└── pytest.ini            # pytest configuration
```

## 🎨 Frontend Features

The SvelteKit frontend provides a clean, responsive web interface for the distance calculation service:

### 🏠 Distance Calculator Page (`/`)
- **Interactive Form**: Source and destination address input fields
- **Unit Selection**: Choose between miles, kilometers, or both
- **Real-time Validation**: Form validation with disabled states
- **Live Results**: Distance calculations displayed in selected units
- **Error Handling**: User-friendly error messages for failed geocoding
- **Loading States**: Visual feedback during API calls
- **Mobile Responsive**: Full-width layout optimized for all screen sizes

### 📊 Historical Queries Page (`/history`)
- **Paginated Table**: View past distance calculations
- **Load More**: Incremental loading for large datasets
- **Interactive Rows**: Click history items to prefill calculator
- **Date Formatting**: Human-readable timestamps
- **Empty States**: Helpful messages when no data exists
- **Error Recovery**: Graceful handling of API failures
- **Responsive Design**: Optimized table layout for mobile devices

### 🔧 Technical Features
- **Type-safe API Integration**: Full TypeScript coverage with backend schema matching
- **Svelte 5 Runes**: Modern reactive state management
- **TailwindCSS v4**: Custom theme with consistent design system
- **URL Parameter Handling**: Seamless navigation with data prefilling
- **Real-time Form Validation**: Immediate feedback on input changes
- **Accessibility Compliance**: ARIA labels, keyboard navigation, semantic HTML
- **Error Boundaries**: Comprehensive error handling and user feedback
- **Test Coverage**: 23 comprehensive tests covering components and API integration

### 🎯 User Experience
- **Intuitive Navigation**: Simple two-page application with clear routing
- **Instant Feedback**: Loading states and error messages provide immediate user feedback
- **Data Persistence**: All calculations automatically saved and retrievable
- **Cross-platform**: Works seamlessly on desktop, tablet, and mobile devices
- **Fast Performance**: Optimized bundle size and lazy loading

## 🎯 API Endpoints

### Current Endpoints (Sprints 1-6)

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

### Query History Endpoint (Sprint 6)

#### `GET /api/v1/history` - Retrieve Past Distance Queries

Retrieve paginated history of distance calculations with filtering, searching, and sorting capabilities.

**Query Parameters:**
- `limit` (int, default: 10): Number of items to return (1-100)
- `offset` (int, default: 0): Number of items to skip for pagination
- `start_date` (datetime): Filter results from this date (ISO format)
- `end_date` (datetime): Filter results up to this date (ISO format)
- `search` (string): Search term for filtering by addresses
- `sort_by` (string, default: "created_at"): Field to sort by
  - Options: `created_at`, `distance_km`, `source_address`, `destination_address`
- `sort_order` (string, default: "desc"): Sort order (`asc` or `desc`)

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": 123,
      "source_address": "1600 Amphitheatre Parkway, Mountain View, CA",
      "destination_address": "1 Apple Park Way, Cupertino, CA",
      "source_lat": 37.4224764,
      "source_lng": -122.0842499,
      "destination_lat": 37.3349,
      "destination_lng": -122.009,
      "distance_km": 11.2,
      "created_at": "2025-06-30T10:30:45.123456"
    }
  ],
  "total": 156,
  "limit": 10,
  "offset": 0,
  "has_more": true
}
```

**Example Requests:**

```bash
# Basic pagination
curl "http://localhost:8000/api/v1/history?limit=20&offset=40"

# Filter by date range
curl "http://localhost:8000/api/v1/history?start_date=2025-06-01&end_date=2025-06-30"

# Search in addresses
curl "http://localhost:8000/api/v1/history?search=New%20York"

# Sort by distance (largest first)
curl "http://localhost:8000/api/v1/history?sort_by=distance_km&sort_order=desc"

# Combined filters
curl "http://localhost:8000/api/v1/history?search=California&limit=5&sort_by=created_at&sort_order=asc"
```

**Error Responses:**
- `422 Unprocessable Entity` - Invalid query parameters (negative limit/offset, invalid date format, etc.)
- `500 Internal Server Error` - Database error

**Security Features:**
- **Pydantic Validation**: All parameters validated at model level with comprehensive error handling
- **SQL Injection Prevention**: Parameterized queries and input sanitization prevent injection attacks
- **Dynamic Attribute Protection**: Secure column mapping eliminates `getattr()` vulnerabilities
- **Input Sanitization**: Search terms sanitized to remove dangerous characters
- **Rate Limiting**: Built-in parameter constraints (limit: 1-100, offset: ≥0) prevent abuse

### Geocoding & Distance Services (Sprint 4)

The application includes comprehensive geocoding and distance calculation capabilities:

- **Address Validation**: Input sanitization and validation preventing XSS/SQL injection
- **Nominatim Geocoding**: Async API client with rate limiting and error handling
- **Distance Calculation**: Haversine formula with support for km/miles units
- **Geographic Utilities**: Bearing calculation, bounding boxes, coordinate validation

### Future Endpoints (Coming in Next Sprints)

- Frontend application with interactive UI (Sprint 7)
- Deployment and production configuration (Sprint 8)

## 🔧 Development Commands

### Full-Stack Setup from Scratch

```bash
# Clone and setup the project
git clone https://github.com/AdamCooke00/delivery-distance-tracker.git
cd delivery-distance-tracker

# Backend setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt requirements-dev.txt
cp .env.example .env

# Frontend setup
cd frontend
npm install
cd ..

# Database setup
cd docker && docker-compose up -d postgres && cd ..
python3 -c "from app.utils.database import initialize_database; print(initialize_database())"
```

### Development Servers

```bash
# Terminal 1: Start database (if not running)
cd docker && docker-compose up postgres

# Terminal 2: Start FastAPI backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 3: Start frontend development server
cd frontend
npm run dev
```

### Access the Application

- **Frontend UI**: http://localhost:5173/
- **API Root**: http://localhost:8000/
- **API Health Check**: http://localhost:8000/api/v1/health
- **API Documentation**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc

### Development Workflow

```bash
# Run all tests (backend + frontend)
source venv/bin/activate
pytest app/tests/ -v
cd frontend && npm test && cd ..

# Code quality checks
black --check . && flake8 .
cd frontend && npm run lint && cd ..

# Build frontend for production
cd frontend
npm run build
npm run preview  # Preview production build
cd ..

# Database operations
cd docker
docker-compose logs postgres        # View database logs
docker-compose down -v              # Reset database (removes data)
docker-compose up -d postgres       # Restart database
cd ..

# Health checks
python3 -c "from app.utils.database import check_database_health; print(check_database_health())"
curl http://localhost:8000/api/v1/health
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

## 🔧 Troubleshooting

### Frontend Issues

**CORS Errors**
```bash
# Error: "Access to fetch at 'http://localhost:8000' has been blocked by CORS policy"
# Solution: Update CORS origins in environment
export CORS_ORIGINS="http://localhost:3000,http://localhost:5173"
# Then restart the backend server
```

**Frontend Won't Start**
```bash
# Check Node.js version
node --version  # Should be 18+

# Clear dependencies and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**API Connection Failed**
```bash
# Verify backend is running
curl http://localhost:8000/api/v1/health

# Check if ports are in use
lsof -i :8000  # Backend
lsof -i :5173  # Frontend
```

### Backend Issues

**Database Connection Failed**
```bash
# Check if PostgreSQL container is running
docker ps | grep postgres

# Restart database
cd docker && docker-compose down && docker-compose up -d postgres
```

**Import Errors**
```bash
# Ensure virtual environment is activated
source venv/bin/activate
which python  # Should point to venv/bin/python

# Reinstall dependencies
pip install -r requirements.txt requirements-dev.txt
```

### Common Solutions

**Port Conflicts**
- Backend (8000): Change in `uvicorn` command
- Frontend (5173): Change in `vite.config.ts`
- Database (5432): Change in `docker-compose.yml`

**Environment Variables**
- Copy `.env.example` to `.env`
- Update CORS origins to include your frontend port
- Restart services after environment changes

**Clean Reset**
```bash
# Full reset (removes all data)
docker-compose down -v
rm -rf frontend/node_modules frontend/.svelte-kit
cd frontend && npm install && cd ..
cd docker && docker-compose up -d postgres && cd ..
```

## 📞 Support

- Review sprint documentation in `project-planning/sprints/`
- Check test cases for validation examples
- Refer to `project-planning/stack-decision.md` for architectural decisions
- Frontend issues: Check browser console and network tab
- Backend issues: Check FastAPI logs and `/docs` endpoint

## 📝 License

This project is for educational purposes.