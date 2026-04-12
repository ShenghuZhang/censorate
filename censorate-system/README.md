# Censorate Management System

AI-native requirement management system organized by Projects with "AI First, Human Check" philosophy.

## Features

- **Project-Based Namespacing**: All entities (Requirements, Tasks, Test Cases) exist within a Project namespace
- **Two Project Types**:
  - Non-Technical: Focused on business requirements and design (4 lanes)
  - Technical: Includes GitHub repo integration (6 lanes)
- **Kanban Board**: Visual workflow management with drag-drop functionality
- **REQ-ID Tracking**: Persistent REQ-XXXX IDs across all phases
- **AI-Human Collaboration**: AI suggestions with human approval workflow
- **Modular Frontend**: Component-based architecture with state management

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm or yarn

### Starting the System

1. **Clone the repository**
   ```bash
   cd stratos-system
   ```

2. **Start Backend**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python -m uvicorn main:app --reload --port 8216
   ```

3. **Start Frontend** (in a new terminal)
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8216
   - API Documentation: http://localhost:8216/docs

## Project Structure

```
stratos-system/
├── backend/
│   ├── main.py                 # FastAPI application entry point
│   ├── database.py             # Database configuration
│   ├── requirements.txt        # Python dependencies
│   ├── Dockerfile              # Backend Docker configuration
│   └── app/
│       ├── api/
│       │   ├── deps.py         # API dependencies
│       │   └── v1/
│       │       ├── router.py      # API router
│       │       └── endpoints/     # API endpoints
│       │           ├── projects.py
│       │           ├── requirements.py
│       │           ├── tasks.py
│       │           ├── test_cases.py
│       │           └── agents.py
│       ├── core/
│       │   ├── config.py       # Application configuration
│       │   ├── security.py     # JWT & security
│       │   ├── cache.py        # Redis cache
│       │   ├── logger.py       # Logging setup
│       │   └── database.py     # Database setup
│       ├── models/             # SQLAlchemy models
│       │   ├── base.py
│       │   ├── project.py
│       │   ├── requirement.py
│       │   ├── task.py
│       │   ├── test_case.py
│       │   ├── user.py
│       │   ├── github_repo.py
│       │   ├── team_member.py
│       │   ├── lane_role.py
│       │   └── agent_execution.py
│       ├── schemas/            # Pydantic schemas
│       │   ├── project.py
│       │   ├── requirement.py
│       │   ├── task.py
│       │   └── agent.py
│       ├── state_machine/
│       │   └── requirement_state_machine.py
│       ├── services/
│       │   ├── deepagent_service.py
│       │   └── lark_service.py
│       ├── agents/
│       │   ├── base_agent.py
│       │   ├── analysis_agent.py
│       │   ├── design_agent.py
│       │   ├── development_agent.py
│       │   └── testing_agent.py
│       ├── skills/
│       │   ├── analysis/SKILL.md
│       │   ├── design/SKILL.md
│       │   ├── development/SKILL.md
│       │   └── testing/SKILL.md
│       └── repositories/
│
├── frontend/
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── next.config.ts
│   ├── Dockerfile
│   └── app/
│       ├── layout.tsx
│       ├── page.tsx
│       ├── globals.css
│       ├── pages/
│       │   ├── KanbanPage.tsx
│       │   └── TeamPage.tsx
│       ├── components/
│       │   ├── kanban/
│       │   │   ├── KanbanBoard.tsx
│       │   │   ├── Swimlane.tsx
│       │   │   └── RequirementCard.tsx
│       │   ├── team/
│       │   │   ├── AgentCard.tsx
│       │   │   ├── AgentMemoryViewer.tsx
│       │   │   └── AddAgentDialog.tsx
│       │   └── requirement/
│       │       └── RequirementDetail.tsx
│       ├── stores/
│       │   ├── teamStore.ts
│       │   └── requirementStore.ts
│       ├── hooks/
│       │   └── useAIAgents.ts
│       └── lib/
│           └── api/
│               └── client.ts
│
├── docker-compose.yml        # Docker Compose configuration
├── .env.example            # Environment variables example
└── start.sh                # Quick start script
```

## Technology Stack

### Backend

- FastAPI 0.104.1
- SQLAlchemy 2.0.23
- Pydantic 2.5.0
- Uvicorn (ASGI server)
- SQLite (default, can be switched to PostgreSQL)
- Redis (caching)

### Frontend

- Next.js 16.2.3
- React 19.2.4
- TypeScript 5
- Tailwind CSS 4
- Zustand (state management)
- @dnd-kit (drag and drop)
- Lucide React (icons)

### AI Integrations

- Claude API (Anthropic)
- OpenAI API (GPT-4, Embeddings)
- DeepAgents framework
- Lark (Feishu) integration

## API Endpoints

### Projects

- `GET /api/v1/projects` - List all projects
- `POST /api/v1/projects` - Create project
- `GET /api/v1/projects/{id}` - Get project details
- `PUT /api/v1/projects/{id}` - Update project
- `DELETE /api/v1/projects/{id}` - Delete project

### Requirements

- `GET /api/v1/projects/{project_id}/requirements` - List requirements
- `POST /api/v1/projects/{project_id}/requirements` - Create requirement
- `GET /api/v1/requirements/{id}` - Get requirement details
- `PUT /api/v1/requirements/{id}` - Update requirement
- `DELETE /api/v1/requirements/{id}` - Delete requirement
- `POST /api/v1/requirements/{id}/transition` - Transition status

### Agents

- `GET /api/v1/projects/{project_id}/agents` - List team members and agents
- `POST /api/v1/projects/{project_id}/agents` - Create AI agent
- `GET /api/v1/agents/{id}` - Get agent details
- `PUT /api/v1/agents/{id}` - Update agent
- `DELETE /api/v1/agents/{id}` - Delete agent
- `GET /api/v1/agents/{id}/memory` - Get agent memory
- `POST /api/v1/agents/{id}/memory` - Update agent memory
- `POST /api/v1/agents/{id}/execute` - Execute agent

## Development

### Adding New Features

1. Backend:
   - Create API endpoint in `backend/app/api/v1/endpoints/`
   - Add schema in `backend/app/schemas/`
   - Update model in `backend/app/models/`

2. Frontend:
   - Add frontend component in `frontend/app/components/`
   - Update state/actions for new operations in `frontend/app/stores/`

### Database

The system uses SQLite by default for development. For production, switch to PostgreSQL by updating the `DATABASE_URL` in the `.env` file.

## Configuration

Copy `.env.example` to `.env` and configure:

- Database connection
- Redis connection
- API keys (Claude, OpenAI, Lark, DeepAgents)
- JWT secret

## Docker

The system can be run using Docker Compose:

```bash
docker-compose up -d
```

This will start:
- Backend API (port 8000)
- Frontend (port 3000)
- PostgreSQL database (port 5432)
- Redis (port 6379)

## License

MIT License - See LICENSE file for details.
