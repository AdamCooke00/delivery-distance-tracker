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
- Node.js 16+ (for frontend development)
- Docker & Docker Compose (for full setup)

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

### 3. Configure Environment Variables

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your configuration
# DATABASE_URL=postgresql://user:password@localhost:5432/delivery_tracker
# NOMINATIM_BASE_URL=https://nominatim.openstreetmap.org
# LOG_LEVEL=INFO
```

### 4. Verify Installation

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

### Code Quality Tools

```bash
# Format code with Black
black .

# Lint with Flake8
flake8 .

# Run tests with coverage
pytest

# Run specific test file
pytest app/tests/test_environment.py -v
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
│   ├── services/          # Business logic (geocoding, distance calc)
│   ├── utils/             # Helper functions and utilities
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

## 🎯 API Endpoints (Future)

- `POST /distance` - Calculate distance between addresses
- `GET /history` - Retrieve past queries (paginated)
- `GET /health` - System health check

## 🔧 Development Commands

```bash
# Start backend development server (when implemented)
source venv/bin/activate
uvicorn app.main:app --reload

# Start frontend development server (when implemented)
cd frontend
npm run dev

# Run full test suite
pytest app/tests/

# Check code coverage
pytest --cov=app --cov-report=html
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