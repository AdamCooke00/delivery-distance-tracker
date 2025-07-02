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
- Docker & Docker Compose (required for PostgreSQL database)

> **⚠️ Important**: Even for local development, Docker is required to run the PostgreSQL database. The application expects PostgreSQL to be running on port 5432.

## 🚀 Quick Start

### Clone the Repository

```bash
git clone https://github.com/AdamCooke00/delivery-distance-tracker.git
cd delivery-distance-tracker
```

### Docker Quick Start (Recommended)

```bash
# Copy environment variables template
cp .env.example .env

# Start the entire application with one command
docker-compose up --build

# Access the application:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Documentation: http://localhost:8000/docs
```

That's it! The complete application is now running with the database initialized.

### Manual Setup (Alternative)

> **Note**: This setup still requires Docker for the PostgreSQL database. You cannot run the application without a database.

```bash
# FIRST: Start the PostgreSQL database (required!)
docker-compose up -d postgres

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt
pip install -r backend/requirements-dev.txt
```

### Set Up Database with Docker

```bash
# Start PostgreSQL database only
docker-compose up -d postgres

# Verify database is running
docker-compose ps
docker-compose logs postgres | grep "database system is ready"
```

### Configure Environment Variables

```bash
# Copy backend environment template
cp .env.example .env

# Copy frontend environment template
cp frontend/.env.example frontend/.env

# Edit .env file with your backend configuration
# DATABASE_URL=postgresql://delivery_user:delivery_password@localhost:5432/delivery_tracker
# POSTGRES_USER=delivery_user
# POSTGRES_PASSWORD=delivery_password
# POSTGRES_DB=delivery_tracker
# NOMINATIM_BASE_URL=https://nominatim.openstreetmap.org
# CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173
# LOG_LEVEL=INFO

# Edit frontend/.env file with your frontend configuration
# VITE_API_URL=http://localhost:8000/api/v1  # For development
# VITE_API_URL=https://your-api.com/api/v1  # For production
```

### Initialize Database Schema

```bash
# Activate virtual environment
source venv/bin/activate

# Initialize database tables
python3 -c "
import sys; sys.path.append('backend')
from app.utils.database import initialize_database
success, message = initialize_database()
print(f'Database initialization: {message}')
"

# Verify database health
python3 -c "
import sys; sys.path.append('backend')
from app.utils.database import check_database_health
healthy, message = check_database_health()
print(f'Database health: {message}')
"
```

### Set Up Frontend

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

### Verify Installation

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
cd backend && black --check . && flake8 . && cd ..
```

## 🧪 Development Workflow

### Database Operations

```bash
# Start database
docker-compose up -d postgres

# Stop database
docker-compose down

# View database logs
docker-compose logs postgres

# Reset database (removes all data)
docker-compose down -v && docker-compose up -d postgres
```

### Testing

```bash
# IMPORTANT: Start the database before running tests
docker-compose up -d postgres

# Activate virtual environment (required for all test commands)
source venv/bin/activate

# Run all tests
cd backend && python -m pytest app/tests/ -v

# Run database tests specifically
cd backend && python -m pytest app/tests/test_database_*.py -v

# Run FastAPI application tests
cd backend && python -m pytest app/tests/test_application.py -v
cd backend && python -m pytest app/tests/test_health.py -v
cd backend && python -m pytest app/tests/test_error_handling.py -v
cd backend && python -m pytest app/tests/test_cors.py -v
cd backend && python -m pytest app/tests/test_logging.py -v

# Run geocoding and distance calculation tests (Sprint 4)
cd backend && python -m pytest app/tests/test_address_validation.py -v
cd backend && python -m pytest app/tests/test_distance_calculation.py -v
cd backend && python -m pytest app/tests/test_geocoding_service.py -v
cd backend && python -m pytest app/tests/test_geocoding_reliability.py -v
cd backend && python -m pytest app/tests/test_geocoding_integration.py -v

# Run distance endpoint tests (Sprint 5)
cd backend && python -m pytest app/tests/test_distance_endpoint.py -v
cd backend && python -m pytest app/tests/test_distance_validation.py -v
cd backend && python -m pytest app/tests/test_distance_geocoding_errors.py -v
cd backend && python -m pytest app/tests/test_distance_database.py -v
cd backend && python -m pytest app/tests/test_distance_e2e.py -v

# Run history endpoint tests (Sprint 6)
cd backend && python -m pytest app/tests/test_history_endpoint.py -v
cd backend && python -m pytest app/tests/test_history_filtering.py -v
cd backend && python -m pytest app/tests/test_history_sorting.py -v
cd backend && python -m pytest app/tests/test_history_validation.py -v
cd backend && python -m pytest app/tests/test_history_performance.py -v
cd backend && python -m pytest app/tests/test_history_security.py -v

# Run end-to-end tests with real APIs (optional)
cd backend && SKIP_E2E_TESTS=false python -m pytest app/tests/test_distance_e2e.py -v

# Run tests with coverage
cd backend && python -m pytest --cov=app --cov-report=html

# Run specific test file
cd backend && python -m pytest app/tests/test_environment.py -v
```

### Frontend Development

```bash
# Start frontend development server
cd frontend
npm run dev
# Access at: http://localhost:5173

# Run frontend tests (from frontend directory)
cd frontend
npm test              # Runs tests in watch mode
npm test -- --run     # Runs tests once and exits
npm run test:ui       # Interactive test UI

# Frontend code quality (from frontend directory)
cd frontend
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
cd backend && black .          # Format code with Black
cd backend && flake8 .         # Lint with Flake8
cd backend && black --check . && flake8 .  # Check before commits

# Frontend code quality
cd frontend
npm run lint     # ESLint checking
npm run format   # Prettier formatting
cd ..

# Full project quality check
cd backend && black --check . && flake8 . && cd ../frontend && npm run lint && cd ..
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
├── backend/                # Backend FastAPI application
│   ├── Dockerfile         # Backend container configuration
│   ├── app/               # FastAPI application code
│   │   ├── api/           # REST endpoint definitions
│   │   │   ├── distance.py    # Distance calculation endpoint
│   │   │   ├── health.py      # Health check endpoints
│   │   │   ├── history.py     # Query history endpoint
│   │   │   └── routes.py      # Main router configuration
│   │   ├── models/        # Database models and schemas
│   │   │   ├── database.py    # SQLAlchemy configuration
│   │   │   └── distance_query.py # Distance query model & schemas
│   │   ├── services/      # Business logic (geocoding service)
│   │   │   ├── distance_service.py # Distance calculation service
│   │   │   └── geocoding.py   # Nominatim geocoding service
│   │   ├── utils/         # Helper functions (validation, distance calc, logging)
│   │   └── tests/         # Unit and integration tests
│   ├── requirements.txt   # Python dependencies
│   ├── requirements-dev.txt # Development dependencies
│   ├── pyproject.toml     # Python configuration
│   ├── pytest.ini        # Test configuration
│   └── .flake8           # Flake8 linting configuration
├── frontend/              # SvelteKit frontend application
│   ├── Dockerfile         # Frontend container configuration
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
├── docker-compose.yml     # Docker orchestration configuration
├── init.sql              # Database schema initialization
├── project-planning/      # Sprint documentation and planning
└── .env.example          # Environment variables template
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
- **Streamlined Display**: Clean table layout with essential information
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
  "distance_km": 11.2
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
- `search` (string): Search term for filtering by addresses
- `sort_by` (string, default: "id"): Field to sort by
  - Options: `id`, `distance_km`, `source_address`, `destination_address`
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
      "distance_km": 11.2
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

# Search in addresses
curl "http://localhost:8000/api/v1/history?search=New%20York"

# Sort by distance (largest first)
curl "http://localhost:8000/api/v1/history?sort_by=distance_km&sort_order=desc"

# Combined filters
curl "http://localhost:8000/api/v1/history?search=California&limit=5&sort_by=id&sort_order=asc"
```

**Error Responses:**
- `422 Unprocessable Entity` - Invalid query parameters (negative limit/offset, invalid sort field, etc.)
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
pip install -r backend/requirements.txt backend/requirements-dev.txt
cp .env.example .env

# Frontend setup
cd frontend
npm install
cd ..

# Database setup
docker-compose up -d postgres
python3 -c "import sys; sys.path.append('backend'); from app.utils.database import initialize_database; print(initialize_database())"
```

### Development Servers

```bash
# Terminal 1: Start database (REQUIRED - must be running first!)
docker-compose up -d postgres

# Verify database is running
docker-compose ps
# Should show: delivery_tracker_db ... Up ... 5432/tcp

# Terminal 2: Start FastAPI backend
source venv/bin/activate
cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

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
cd backend && python -m pytest app/tests/ -v && cd ..
cd frontend && npm test && cd ..

# Code quality checks
cd backend && black --check . && flake8 . && cd ..
cd frontend && npm run lint && cd ..

# Build frontend for production
cd frontend
npm run build
npm run preview  # Preview production build
cd ..

# Database operations
docker-compose logs postgres        # View database logs
docker-compose down -v              # Reset database (removes data)
docker-compose up -d postgres       # Restart database

# Health checks
python3 -c "import sys; sys.path.append('backend'); from app.utils.database import check_database_health; print(check_database_health())"
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
    distance_km DECIMAL(10, 3)
);

-- Performance indexes
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
docker-compose up -d postgres
```

## 📞 Support

- Review sprint documentation in `project-planning/sprints/`
- Check test cases for validation examples
- Refer to `project-planning/stack-decision.md` for architectural decisions
- Frontend issues: Check browser console and network tab
- Backend issues: Check FastAPI logs and `/docs` endpoint

## 📝 License

This project is for educational purposes.