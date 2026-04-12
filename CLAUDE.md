# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Stratos is an AI-native requirement management system organized by Projects with "AI First, Human Check" philosophy. The main working directory is `stratos-system/`.

## Quick Start Commands

```bash
# Start both backend and frontend services
./run.sh start

# Stop all services
./run.sh stop

# Check service status
./run.sh status

# Setup project environment
./run.sh setup
```

## Development Commands

### Backend (FastAPI)

```bash
cd stratos-system/backend

# Start backend server (port 8216)
python main.py

# Start with auto-reload
uvicorn main:app --reload --port 8216

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest
```

### Frontend (Next.js)

```bash
cd stratos-system/frontend

# Start dev server (port 3000)
npm run dev

# Build for production
npm run build

# Install dependencies
npm install
```

### Testing

```bash
# Backend unit tests
cd stratos-system/backend
pytest

# Frontend E2E tests (Playwright)
cd stratos-system/frontend
npx playwright test
```

## Architecture

### Backend Architecture

The backend follows a layered architecture pattern:

```
API Layer (app/api/v1/)
    ↓
Service Layer (app/services/) - Business logic
    ↓
Repository Layer (app/repositories/) - Data access
    ↓
Model Layer (app/models/) - SQLAlchemy ORM
```

**Key Directories**:
- `app/api/v1/endpoints/` - API route handlers
- `app/services/` - Business logic (deepagent_service.py, requirement_service.py, etc.)
- `app/repositories/` - Database access (BaseRepository pattern)
- `app/models/` - SQLAlchemy models (Project, Requirement, Task, User, etc.)
- `app/core/` - Configuration, security, database, logging
- `app/agents/` - AI Agent implementations (analysis_agent.py, design_agent.py, etc.)
- `app/skills/` - Agent skill definitions (analysis/, design/, development/, testing/)
- `app/state_machine/` - Requirement state transitions

### Frontend Architecture

- **Framework**: Next.js 16.2.3 with App Router
- **State Management**: Zustand stores (`app/stores/`)
- **Component Structure**:
  - `app/components/kanban/` - Kanban board components
  - `app/components/team/` - Team and agent management
  - `app/components/requirement/` - Requirement detail views
- **API Client**: `app/lib/api/` - API integration layer
- **Custom Hooks**: `app/hooks/` - Reusable logic

## Important Notes

1. **Port Configuration**: The backend runs on port 8216 (not 8026), frontend on 3000

2. **Environment Variables**:
   - Backend: `stratos-system/backend/.env` (use .env.example as template)
   - Frontend: `stratos-system/frontend/.env.local` with `NEXT_PUBLIC_API_URL=http://localhost:8216/api/v1`

3. **Project Types**:
   - Non-Technical: 4 lanes (Business requirements focused)
   - Technical: 6 lanes (Includes GitHub repo integration)

4. **REQ-ID Tracking**: Requirements have persistent REQ-XXXX IDs that remain constant across all phases

5. **AI Agent System**:
   - Skills are defined in `backend/app/skills/` as SKILL.md files
   - Agents are implemented in `backend/app/agents/` extending BaseAgent
   - Agent execution records are tracked in `agent_execution` table

## Database

- **Development**: SQLite (database.db)
- **Production**: PostgreSQL (configure via DATABASE_URL in .env)
- **Migrations**: Alembic is included for database migrations

## API Documentation

FastAPI auto-generated docs available at: http://localhost:8216/docs

## Testing Strategy

- **Unit Tests**: `backend/tests/unit/` - pytest
- **Integration Tests**: `backend/tests/integration/` - pytest
- **E2E Tests**: `tests/e2e/` - Playwright

## Common Tasks

When adding a new feature:

1. **Backend**:
   - Create model in `app/models/`
   - Create repository in `app/repositories/` (inheriting from BaseRepository)
   - Create service in `app/services/`
   - Create schema in `app/schemas/`
   - Create endpoint in `app/api/v1/endpoints/`
   - Register router in `app/api/v1/router.py`

2. **Frontend**:
   - Create component in `app/components/`
   - Add API client functions in `app/lib/api/`
   - Update Zustand store in `app/stores/`
   - Create custom hook in `app/hooks/` if needed

3. **AI Agent**:
   - Create agent in `app/agents/` extending BaseAgent
   - Define skills in `app/skills/` as SKILL.md files
   - Register agent in `app/agents/registry.py`
