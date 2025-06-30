# Sprint 1: Project Foundation & Setup

## 🎯 Objective
Establish the foundational project structure, development environment, and Git workflow according to our defined architecture and development standards.

## 📋 Acceptance Criteria

### 1. Repository & Git Setup
- [x] Initialize Git repository
- [ ] Create and push `develop` branch
- [ ] Set up `.gitignore` file for Python and Node.js
- [ ] Create initial `README.md` with project overview
- [ ] Implement conventional commit message format

### 2. Project Structure Creation
- [ ] Create exact directory structure as defined in stack decision:
  ```
  /app
    /api - REST endpoint definitions
    /models - Database models and schemas  
    /services - Business logic (geocoding, distance calc)
    /utils - Helper functions and utilities
    /tests - Unit and integration tests
  /frontend - SvelteKit application
  /docker - Container configurations
  requirements.txt - Python dependencies
  ```

### 3. Python Development Environment
- [ ] Create Python virtual environment using `python3 -m venv venv`
- [ ] Create `requirements.txt` with core dependencies:
  ```
  fastapi>=0.104.0
  uvicorn[standard]>=0.24.0
  sqlalchemy>=2.0.0
  psycopg2-binary>=2.9.0
  pydantic>=2.4.0
  httpx>=0.25.0
  pytest>=7.4.0
  python-multipart>=0.0.6
  python-dotenv>=1.0.0
  ```
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Create `requirements-dev.txt` with development tools:
  ```
  black>=23.0.0
  flake8>=6.0.0
  pytest-cov>=4.0.0
  pytest-asyncio>=0.21.0
  ```

### 4. Environment Configuration
- [ ] Create `.env.example` template with required environment variables:
  ```
  DATABASE_URL=postgresql://user:password@localhost:5432/delivery_tracker
  NOMINATIM_BASE_URL=https://nominatim.openstreetmap.org
  LOG_LEVEL=INFO
  ```
- [ ] Create `.env` file for local development (add to .gitignore)
- [ ] Set up environment variable loading with python-dotenv

### 5. Code Quality Setup
- [ ] Create `pyproject.toml` with Black configuration
- [ ] Create `.flake8` configuration file
- [ ] Create `pytest.ini` configuration file

### 6. README.md Documentation
- [ ] Update README.md to reflect current repository state
- [ ] Document prerequisites: Python 3.8+, Git
- [ ] Include complete setup instructions:
  - Clone repository steps
  - Virtual environment creation and activation
  - Dependencies installation from requirements.txt
  - Environment variable setup from .env.example
- [ ] Document development workflow and code quality tools
- [ ] Include commands to run tests and code formatting

## 🧪 Test Cases That Must Pass

### Test Case 1: Directory Structure Validation
```bash
# All required directories exist
test -d app/api && test -d app/models && test -d app/services && test -d app/utils && test -d app/tests
test -d frontend && test -d docker
echo "✅ Directory structure validated"
```

### Test Case 2: Python Environment Validation
```bash
# Virtual environment exists and is activated
source venv/bin/activate
python --version | grep "Python 3"
pip list | grep fastapi
pip list | grep uvicorn
echo "✅ Python environment validated"
```

### Test Case 3: Git Workflow Validation
```bash
# Branches exist and are properly configured
git branch --list | grep main
git branch --list | grep develop
git log --oneline -1 | grep -E "^[a-f0-9]+ (feat|fix|chore|docs):"
echo "✅ Git workflow validated"
```

### Test Case 4: Environment Configuration Test
```python
# File: app/tests/test_environment.py
import os
from dotenv import load_dotenv

def test_environment_variables_loaded():
    load_dotenv()
    assert os.getenv('DATABASE_URL') is not None
    assert os.getenv('NOMINATIM_BASE_URL') is not None
    assert os.getenv('LOG_LEVEL') is not None
    print("✅ Environment configuration validated")
```

### Test Case 5: Code Quality Tools Test
```bash
# Code formatting and linting tools work
echo "print('hello world')" > test_file.py
black test_file.py --check
flake8 test_file.py
rm test_file.py
echo "✅ Code quality tools validated"
```

## 🔧 Implementation Steps

### Step 1: Git Repository Setup
1. Ensure you're in the project root: `/mnt/e/Code/delivery-distance-tracker`
2. Create develop branch: `git checkout -b develop`
3. Create .gitignore file with Python, Node.js, and environment exclusions
4. Push develop branch: `git push -u origin develop`

### Step 2: Directory Structure Creation
1. Create all required directories using `mkdir -p` commands
2. Add `.gitkeep` files to empty directories to track them in Git
3. Verify structure matches exactly what's defined in stack decision

### Step 3: Python Environment Setup
1. Create virtual environment: `python3 -m venv venv`
2. Activate environment: `source venv/bin/activate`
3. Create requirements.txt with exact versions specified
4. Install all dependencies and verify successful installation

### Step 4: Environment & Configuration Files
1. Create all configuration files (.env.example, .flake8, pyproject.toml, pytest.ini)
2. Set up proper environment variable structure
3. Test configuration loading

### Step 5: Validation & Documentation
1. Run all test cases to ensure everything is properly configured
2. Update README.md with setup instructions
3. Create initial commit with conventional commit format

## 📝 Git Workflow Instructions

### Branch Strategy
- Work on `feature/sprint-01-foundation` branch
- All commits must follow conventional commit format:
  - `feat:` for new features
  - `chore:` for maintenance tasks
  - `docs:` for documentation
  - `test:` for test additions

### Commit Process
1. Create feature branch: `git checkout -b feature/sprint-01-foundation`
2. Make changes following acceptance criteria
3. Stage changes: `git add .`
4. Commit with proper format: `git commit -m "feat: establish project foundation and development environment"`
5. Push branch: `git push -u origin feature/sprint-01-foundation`

## 🔒 Security Requirements
- [ ] `.env` file must be in `.gitignore`
- [ ] No hardcoded sensitive values in any committed files
- [ ] Environment variables properly scoped and documented

## 📊 Quality Gates
- [ ] All test cases pass
- [ ] Code passes Black formatting check
- [ ] Code passes Flake8 linting
- [ ] 100% of acceptance criteria completed
- [ ] README.md updated with setup instructions

## 🎁 Deliverables
1. Complete project directory structure
2. Configured Python virtual environment with all dependencies
3. Git repository with proper branching strategy
4. Environment configuration template and local setup
5. Code quality tools configured and working
6. Initial documentation in README.md
7. All test cases passing

## 🚫 Exit Criteria
**This sprint is complete when:**
- All 5 test cases pass without errors
- All acceptance criteria checkboxes are marked complete
- Feature branch is ready for merge to develop
- Documentation is updated and accurate
- Environment can be replicated by another developer following README instructions

## 🔄 Next Sprint Preview
Sprint 2 will build upon this foundation by setting up the PostgreSQL database with Docker, creating the initial database schema, and establishing database connectivity patterns.