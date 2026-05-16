# Censorate Management System - Technical Architecture Document

## 1. System Architecture Overview

### Current Architecture (2026)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     Web Browser (Next.js :3000)                       │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│               Backend API (FastAPI :8216)                            │
│  • Projects/Requirements/Tasks • AI Agents • Skills • Remote Agents  │
│  • Attachments • Comments • Notifications • Integrations             │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        ▼                           ▼                           ▼
┌──────────────┐          ┌──────────────┐          ┌──────────────┐
│  PostgreSQL  │          │    Redis     │          │    MinIO     │
│  :5432       │          │   :6379      │          │  :9000/:9001 │
└──────────────┘          └──────────────┘          └──────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        ▼                           ▼                           ▼
┌──────────────┐          ┌──────────────┐          ┌──────────────┐
│    Hermes    │          │Skill Manager │          │  Init Demo  │
│  (Gateway)   │          │  (Daemon)    │          │  (Optional)  │
│  :8642       │          │   :8765      │          │              │
└──────────────┘          └──────────────┘          └──────────────┘
                                    │
                                    ▼
                      ┌─────────────────────────┐
                      │   hermes_data Volume    │
                      │   (Shared between      │
                      │   Hermes & SkillMgr)  │
                      └─────────────────────────┘
```

### Key Architectural Features

1. **Skill Manager Daemon** - Independent webhook-driven service
2. **Shared Hermes Data** - Co-located skill storage
3. **MinIO Object Storage** - Attachments and skills files
4. **Multi-AI Provider** - Claude, OpenAI, DeepSeek
5. **Healthcheck-based Dependencies** - Robust service startup

---

## 2. Technology Stack

### Frontend
- **Framework**: Next.js 16+ (App Router)
- **UI**: shadcn/ui + Tailwind CSS
- **State**: Zustand + React Query
- **Drag & Drop**: @dnd-kit/core

### Backend
- **Framework**: FastAPI 0.104+
- **Database**: PostgreSQL 15+ (Primary) + SQLite (Dev fallback)
- **ORM**: SQLAlchemy 2.0
- **Cache**: Redis 7+
- **Auth**: JWT + OAuth2
- **Validation**: Pydantic 2.0

### AI Services
- **Primary**: Claude 3.5 Sonnet
- **Fallback**: OpenAI GPT-4
- **DeepAgent**: DeepSeek API + Framework
- **Agent Platform**: Hermes with Skills

### Storage
- **Object Storage**: MinIO
- **Buckets**: `censorate` (attachments), `censorate-skills` (skills)

---

## 3. Data Model

### Core Entities

```
Projects
  ├── Requirements (with req_number)
  │   ├── Tasks
  │   ├── Test Cases
  │   ├── Attachments
  │   ├── Comments
  │   └── Status History
  ├── Team Members
  ├── Lane Roles
  ├── GitHub Repos
  ├── Remote Agents
  ├── Skills
  └── Automation Rules

Other Entities:
  ├── Users
  ├── Notifications
  └── Agent Executions
```

### Key Models

1. **projects** - Project management with technical/non-technical types
2. **requirements** - Requirements with status, priority, AI metadata
3. **requirement_status_history** - Full audit trail of state changes
4. **tasks** - Task breakdowns with GitHub PR links
5. **test_cases** - Test case management
6. **remote_agents** - External AI agent configuration
7. **skills** - Skill definitions with files
8. **skill_files** - Skill file versioning
9. **attachments** - File attachments
10. **comments** - Collaboration comments
11. **notifications** - User notifications
12. **agent_executions** - AI agent execution history

---

## 4. API Module Overview

### Core Modules (api/v1/endpoints/)

| Module | Key Endpoints |
|--------|--------------|
| projects | CRUD, upgrade, link repo |
| requirements | CRUD, transition, analyze, history, attachments, comments |
| tasks | CRUD, generate-tests |
| test_cases | CRUD, run |
| remote_agents | CRUD, sync, test-connection |
| skills | CRUD, file upload/download |
| notifications | Get, mark read, delete |
| automation_rules | CRUD, test |
| analytics | cycle-time, cfd, efficiency, bottlenecks |
| agents | execute, get executions |
| auth | login, register, refresh |
| profile | user profile management |
| github_repos | GitHub repo management |

### Skill Manager Webhook

- **POST** `/webhook/agent-updated` - Backend notifies Skill Manager of skill changes
- Payload includes agent info, capabilities, and skill files

---

## 5. Skill System Architecture

### Synchronization Flow

```
Backend Skill CRUD
    ↓
Webhook to Skill Manager (with full skill data)
    ↓
Skill Manager saves to hermes_data/skills/
    ↓
Hermes uses updated skills
```

### Skill Storage

- **Database** - `skills` and `skill_files` tables
- **MinIO** - `censorate-skills` bucket
- **Local** - `hermes_data/skills/` (shared volume)

### Skill Manager Daemon

- Runs as independent service on port 8765
- Webhook-only mode (no polling)
- Shares `hermes_data` volume with Hermes

---

## 6. Storage Architecture

### Storage Service

Abstracted storage supporting both MinIO and local:

```python
class StorageService:
    storage_type: 'minio' or 'local'

    save_file(filename, content, content_type) → path
    get_file(path) → bytes
    delete_file(path)
```

### MinIO Layout

```
censorate/
└── attachments/{project_id}/[requirements|tasks]/{id}/

censorate-skills/
└── {skill_id}/[SKILL.md, requirements.txt, ...]
```

---

## 7. Deployment Architecture

### Docker Compose Services

| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| db | postgres:15 | 5432 | Database |
| redis | redis:7-alpine | 6379 | Cache |
| hermes | nousresearch/hermes-agent:latest | 8642 | Agent Gateway |
| skill-manager | Custom build (daemon/) | 8765 | Skill Sync Daemon |
| minio | minio/minio | 9000, 9001 | Object Storage |
| backend | Custom build (backend/) | 8216 | Backend API |
| frontend | Custom build (frontend/) | 3000 | Frontend UI |
| init_demo | Custom build (backend/) | - | Demo data init (optional) |

### Volumes

- `postgres_data` - Database persistence
- `redis_data` - Redis persistence
- `minio_data` - MinIO object storage
- `hermes_data` - Shared Hermes skill storage

---

## 8. Project Structure

### Backend (censorate-system/backend/)

```
app/
├── api/v1/endpoints/     - API route handlers (15+ modules)
├── core/                 - Config, security, cache, logger
├── models/               - SQLAlchemy models (15+ models)
├── schemas/              - Pydantic schemas
├── repositories/         - Data access layer
├── services/             - Business logic
│   ├── storage_service.py
│   ├── skill_service.py
│   ├── remote_agent_service.py
│   └── notification_service.py
├── agents/               - AI agent implementations
├── skills/               - Built-in skills (SKILL.md)
├── state_machine/        - Requirement state management
└── utils/                - Helpers and validators

scripts/
├── init_mock_data.py
└── docker-init-demo.sh
```

### Daemon (censorate-system/daemon/)

```
skill_manager.py       - Skill Manager daemon
requirements.txt
Dockerfile
```

### Frontend (censorate-system/frontend/)

```
app/
├── components/
│   ├── kanban/
│   ├── team/
│   ├── requirement/
│   ├── skills/
│   └── agents/
├── hooks/               - Custom hooks
├── stores/              - Zustand state stores
└── lib/api/             - API client modules
```

---

## 9. Key Integrations

### Backend ↔ Skill Manager
- Webhook at `/webhook/agent-updated`
- Payload includes agent info, capabilities, skill files
- Skill Manager saves to shared `hermes_data` volume

### Backend ↔ MinIO
- Storage service abstracts MinIO
- Fallback to local storage for dev

### Backend ↔ Hermes
- DeepAgentService integrates with Hermes
- Agent executions tracked in database

---

## 10. Environment Configuration

### Backend Config (app/core/config.py)

Key settings:
- Database & Redis connections
- AI provider API keys (Claude, OpenAI, DeepSeek)
- Skill Manager webhook URL
- MinIO or local storage selection
- Upload size limits
- JWT configuration

### Docker Compose Env

Root `.env` configures:
- Database credentials
- API keys
- MinIO credentials
- Hermes config
- Init demo toggle

---

## 11. Quick Start

### Full Docker Deployment

```bash
# Setup
cd /Users/moya/Workspace/stichdemo
cp .env.example .env
# Edit .env with your keys

# Start
docker-compose up -d

# Access
# Frontend: http://localhost:3000
# Backend Docs: http://localhost:8216/docs
# MinIO Console: http://localhost:9001

# Stop
docker-compose down
```

### Local Development

```bash
# Backend
cd censorate-system/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py

# Frontend
cd censorate-system/frontend
npm install
npm run dev
```

---

## 12. 2026 Architectural Updates Summary

Major additions/changes:

1. **Skill Manager Daemon** - Independent webhook-driven service
2. **Shared Hermes Data Volume** - Co-located skill storage
3. **MinIO Storage** - Object storage for attachments and skills
4. **Remote Agents API** - External AI agent management
5. **Skills API** - Full skill CRUD and file management
6. **Notifications System** - Real-time user notifications
7. **Attachments & Comments** - Collaboration features
8. **Agent Executions** - AI execution tracking
9. **Status History** - Full audit trail
10. **Healthcheck-based Startup** - Robust service dependencies
11. **Init Demo Service** - Optional demo data initialization
