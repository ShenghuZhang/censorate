# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Censorate is an **AI code generation platform**. Describe requirements → AI generates structured PRD → user confirms → AI generates complete runnable code → user reviews → pushed to GitHub. The main working directory is `censorate-system/`.

**Tech stack**: FastAPI (Python 3.11) + Next.js 16 (TypeScript) + PostgreSQL + Redis + Claude API + GitHub API.

## Quick Start

```bash
# Start all services (backend port 8216, frontend port 3000)
./run.sh start

# Stop all services
./run.sh stop

# Setup: create venv, install deps
./run.sh setup
```

## Development Commands

### Backend (FastAPI)

```bash
cd censorate-system/backend

# Run server
python main.py                          # port 8216, auto-reload

# Install deps
pip install -r requirements.txt

# Tests
pytest                                  # all tests
python -m pytest tests/unit/ -v         # unit tests
```

### Frontend (Next.js 16)

```bash
cd censorate-system/frontend

npm run dev          # dev server (port 3000)
npm run build        # production build
```

## Architecture

### System Flow

```
User Story → [Claude API] → PRD (user confirms)
    → [Claude API] → Architecture Design (user approves)
    → [Claude API] → Code Generation (auto review)
    → User approves → [GitHub API] → Push to repo
```

### Backend Layers

```
API Layer (app/api/v1/endpoints/)
    ↓
Service Layer (app/services/)         ← business logic, orchestrator
    ↓
Agent Layer (app/agents_v2/)          ← Claude API calls
    ↓
Model Layer (app/models/)             ← SQLAlchemy ORM (6 models)
```

**Key Backend Directories**:
- `app/api/v1/endpoints/` — auth, templates, generation_projects, pipeline, generated_files, github
- `app/schemas/` — Pydantic schemas (template, generation_project, prd, architecture, review)
- `app/services/` — claude_service (Anthropic SDK wrapper), pipeline_orchestrator (ties agents together), github_service (Git Trees API push)
- `app/agents_v2/` — 5 agents: requirement_analysis → architect → code_generator → code_review → github_push
- `app/models/` — 6 models: User, Template, GenerationProject, GeneratedFile, PipelineStep, GitHubRepo
- `app/core/` — Config (pydantic-settings), JWT security, database (init_db + migrate_to_v2)
- `app/state_machine/` — generation_state_machine (9 states: draft→confirmed→designing→generating→reviewing→ready→pushing→completed→failed)
- `app/seed_data/` — Default template seed (FastAPI + Next.js monorepo)

### Frontend

- **Framework**: Next.js 16.2.3 App Router + TypeScript + Tailwind CSS
- **State (Zustand)**: 2 stores — templateStore, generationProjectStore
- **Key Components**: generation/ (NewProjectForm, ProjectDetail, PipelineProgress)
- **Pages**: /dashboard (main), /projects/[id] (detail), /login
- **API Client**: `lib/api/` (client.ts, templates.ts, generation-projects.ts)

## Models

| Model | Key Fields |
|-------|-----------|
| Template | name, slug, tech_stack (JSON), is_monorepo, config |
| GenerationProject | name, user_story, status, template_id, prd_content, architecture_design, repo_url |
| GeneratedFile | project_id, file_path, content, language, step, status |
| PipelineStep | project_id, step_type, status, result, error, retry_count |
| GitHubRepo | project_id, repo_name, owner, url, push_status, commit_sha |
| User | username, email, hashed_password |

## Pipeline State Machine

`draft → confirmed → designing → generating → reviewing → ready → pushing → completed`

All states can transition to `failed`. Failed can retry to `draft` or `confirmed`. Back transitions allowed.

## API Endpoints

| Prefix | Routes |
|--------|--------|
| `/auth` | login, register |
| `/templates` | GET list, GET by id |
| `/generation-projects` | CRUD + confirm PRD / approve architecture / approve code / retry / cancel |
| `/pipeline` | GET /projects/{id}/steps |
| `/generated-files` | GET list, GET detail with content |
| `/github` | GET /projects/{id}/github |

## Important Notes

1. **Ports**: Backend 8216, Frontend 3000, DB 5432, Redis 6379
2. **Claude API**: Set `CLAUDE_API_KEY` in `.env`. Model defaults to `claude-3-5-sonnet-20240620`
3. **GitHub**: Set `GITHUB_ACCESS_TOKEN` + `GITHUB_USERNAME` in `.env` for code push
4. **Agent pipeline runs via FastAPI BackgroundTasks** — frontend polls every 3s for progress
5. **Generation templates** are seeded into DB on startup. Default: FastAPI + Next.js monorepo
6. **DB init**: `init_db()` creates tables and seeds templates. `migrate_to_v2()` drops all + recreates
7. **No more Hermes, Skill Manager, MinIO** — those were removed in the v2 transformation
