# Claude Memory - Delivery Distance Tracker

## 🎯 Project Context
- **Type**: Delivery Distance Tracker (Bain Assessment)
- **Stack**: FastAPI + SvelteKit + PostgreSQL + Docker
- **Architecture**: Monolithic MVP with 8-sprint development approach

## 🔧 Development Practices

### Branching Strategy
```
main (production) → develop (integration) → feature/sprint-XX-name
```

### Commit Conventions
- `feat:` - New features
- `fix:` - Bug fixes  
- `chore:` - Maintenance
- `docs:` - Documentation
- `test:` - Tests

### Testing Standards
- **Coverage Target**: 80%
- **Backend**: pytest, mock external APIs
- **Frontend**: Jest + Testing Library
- **E2E**: Playwright

### Code Quality Tools
- **Python**: Black (format), Flake8 (lint)
- **Frontend**: Prettier (format), ESLint (lint)

## 🚀 Sprint Workflow
- **Total**: 8 sprints (Foundation → Database → API → Geocoding → Distance → History → Frontend → Deployment)
- **Process**: Complete acceptance criteria → pass 5 test cases → implement → commit

### Sprint Completion Process
- **IMPORTANT**: Only update sprint checkboxes at the very end of sprint completion
- Review entire sprint file to verify all acceptance criteria were met
- Check boxes for completed items and add notes for any deviations or differences
- Add completion summary with date and key deliverables at end of sprint file
- Create feature branch, commit with conventional format, merge to develop

## 📁 Key File Navigation

### Planning & Architecture
- Sprint details: `project-planning/sprints/sprint-XX-name.md`
- Tech decisions: `project-planning/stack-decision.md`
- Sprint overview: `project-planning/sprints/README.md`

### Implementation Structure
```
/app                 # Backend (FastAPI)
  /api              # REST endpoints
  /models           # DB models & schemas
  /services         # Business logic
  /utils            # Helpers
  /tests            # Backend tests
/frontend           # SvelteKit app
/docker             # Container configs
```

## ⚡ Essential Commands

### Testing
```bash
pytest app/tests/              # Backend tests
npm test                       # Frontend tests (in /frontend)
```

### Code Quality
```bash
black .                        # Format Python
flake8                         # Lint Python
```

### Development
```bash
docker-compose up              # Start services
uvicorn app.main:app --reload  # Start FastAPI
npm run dev                    # Start SvelteKit (in /frontend)
```

## 📊 API Design (Quick Reference)
- `POST /distance` - Calculate distance between addresses
- `GET /history` - Retrieve past queries (paginated)
- `GET /health` - System health check

## 🗄️ Database
- **Table**: `distance_queries` (id, addresses, coordinates, distance_km, created_at)
- **Indexes**: created_at, addresses (for performance)


---
*Update this file as project evolves. Keep it concise - detailed info lives in planning docs.*