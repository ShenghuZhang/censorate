# Stratos Management System - Technical Architecture Document

## 1. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Web Browser / Client                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTPS / WebSocket
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           API Gateway / Load Balancer                   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
         ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
         │  Frontend      │ │  Backend API    │ │  AI Service     │
         │  (Next.js)     │ │  (FastAPI)      │ │  (Claude API)   │
         └─────────────────┘ └─────────────────┘ └─────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
         ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
         │  PostgreSQL     │ │  Redis Cache    │ │  GitHub API     │
         │  (Primary DB)   │ │  (Session/State)│ │  (Integration)  │
         └─────────────────┘ └─────────────────┘ └─────────────────┘
```

## 2. Technology Stack

### Frontend
- **Framework**: Next.js 14 (App Router)
- **UI Components**: shadcn/ui + Tailwind CSS
- **State Management**: Zustand + React Query
- **Drag & Drop**: @dnd-kit/core
- **Charts**: Recharts
- **Forms**: React Hook Form + Zod
- **Typography**: Manrope (Google Fonts)

### Backend
- **Framework**: FastAPI 0.100+
- **Database**: PostgreSQL 15+ with PostGIS
- **ORM**: SQLAlchemy 2.0
- **Cache**: Redis 7+
- **Async**: asyncio + uvicorn
- **Validation**: Pydantic 2.0
- **Auth**: JWT + OAuth2

### AI Services
- **Primary**: Claude 3.5 Sonnet API (Anthropic)
- **Fallback**: GPT-4 Turbo (OpenAI)
- **Embeddings**: OpenAI text-embedding-3-small
- **Vector Store**: pgvector (PostgreSQL extension)

### DevOps & Infrastructure
- **Container**: Docker + Docker Compose
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus + Grafana
- **Logging**: OpenTelemetry + Loki
- **Secrets**: AWS Secrets Manager / HashiCorp Vault

## 3. Database Schema

### Entity Relationship Diagram

```
┌──────────────┐       ┌──────────────┐
│   Project    │──────►│  Requirement  │
└──────────────┘       └──────────────┘
        │                      │
        │                      ├──────►┌─────────┐
        │                      │       │  Task   │
        │                      │       └─────────┘
        │                      │              │
        │                      │              ▼
        │                      │       ┌──────────────┐
        │                      └──────►│  TestCase    │
        │                              └──────────────┘
        │
        ▼
┌──────────────┐
│ GitHubRepo   │
└──────────────┘
```

### Table: projects
```sql
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    project_type VARCHAR(20) NOT NULL CHECK (project_type IN ('non_technical', 'technical')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID NOT NULL REFERENCES users(id),
    settings JSONB DEFAULT '{}',
    archived_at TIMESTAMP WITH TIME ZONE,
    INDEX idx_projects_slug (slug),
    INDEX idx_projects_type (project_type),
    INDEX idx_projects_created_by (created_by)
);
```

### Table: requirements
```sql
CREATE TABLE requirements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    req_number INTEGER NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'new',
    priority VARCHAR(20) NOT NULL DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high')),
    source VARCHAR(50),
    source_metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID NOT NULL REFERENCES users(id),
    assigned_to UUID REFERENCES users(id),
    ai_confidence DECIMAL(5,2),
    ai_suggestions JSONB,
    return_count INTEGER DEFAULT 0,
    last_returned_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    archived_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(project_id, req_number),
    INDEX idx_requirements_project (project_id),
    INDEX idx_requirements_status (status),
    INDEX idx_requirements_priority (priority),
    INDEX idx_requirements_assigned (assigned_to),
    INDEX idx_requirements_ai_confidence (ai_confidence)
);
```

### Table: requirement_transitions
```sql
CREATE TABLE requirement_transitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requirement_id UUID NOT NULL REFERENCES requirements(id) ON DELETE CASCADE,
    from_status VARCHAR(50),
    to_status VARCHAR(50) NOT NULL,
    reason TEXT,
    created_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    INDEX idx_transitions_requirement (requirement_id),
    INDEX idx_transitions_created (created_at)
);
```

### Table: tasks
```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requirement_id UUID NOT NULL REFERENCES requirements(id) ON DELETE CASCADE,
    task_number INTEGER NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    estimate_hours DECIMAL(5,2),
    github_pr_url VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID NOT NULL REFERENCES users(id),
    assigned_to UUID REFERENCES users(id),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(requirement_id, task_number),
    INDEX idx_tasks_requirement (requirement_id),
    INDEX idx_tasks_status (status),
    INDEX idx_tasks_assigned (assigned_to)
);
```

### Table: test_cases
```sql
CREATE TABLE test_cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requirement_id UUID NOT NULL REFERENCES requirements(id) ON DELETE CASCADE,
    test_number INTEGER NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    type VARCHAR(50) NOT NULL CHECK (type IN ('unit', 'integration', 'e2e', 'manual')),
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    github_run_url VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID NOT NULL REFERENCES users(id),
    UINDEX UNIQUE (requirement_id, test_number),
    INDEX idx_test_cases_requirement (requirement_id),
    INDEX idx_test_cases_status (status)
);
```

### Table: task_test_cases (Many-to-Many)
```sql
CREATE TABLE task_test_cases (
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    test_case_id UUID NOT NULL REFERENCES test_cases(id) ON DELETE CASCADE,
    PRIMARY KEY (task_id, test_case_id)
);
```

### Table: github_repos
```sql
CREATE TABLE github_repos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    owner VARCHAR(255) NOT NULL,
    repo VARCHAR(255) NOT NULL,
    installation_id BIGINT,
    webhook_id BIGINT,
    last_synced_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(project_id, owner, repo),
    INDEX idx_github_repos_project (project_id)
);
```

### Table: automation_rules
```sql
CREATE TABLE automation_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    trigger_type VARCHAR(50) NOT NULL,
    trigger_config JSONB NOT NULL,
    conditions JSONB DEFAULT '[]',
    actions JSONB NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID NOT NULL REFERENCES users(id),
    INDEX idx_automation_rules_project (project_id),
    INDEX idx_automation_rules_active (project_id, is_active)
);
```

### Table: users
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    avatar_url VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    INDEX idx_users_email (email)
);
```

## 4. API Architecture

### API Layer Structure

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           API Gateway                                   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
         ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
         │  Projects API   │ │ Requirements API│ │  Tasks API      │
         └─────────────────┘ └─────────────────┘ └─────────────────┘
                    │               │               │
                    └───────────────┼───────────────┘
                                    ▼
         ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
         │  AI Services    │ │  GitHub Service │ │  Analytics API  │
         └─────────────────┘ └─────────────────┘ └─────────────────┘
```

### REST API Endpoints

#### Projects
```
GET    /api/v1/projects                    # List projects
POST   /api/v1/projects                    # Create project
GET    /api/v1/projects/{id}               # Get project details
PUT    /api/v1/projects/{id}               # Update project
DELETE /api/v1/projects/{id}               # Delete project
POST   /api/v1/projects/{id}/upgrade      # Upgrade to technical
POST   /api/v1/projects/{id}/link-repo     # Link GitHub repo
```

#### Requirements
```
GET    /api/v1/projects/{project_id}/requirements
POST   /api/v1/projects/{project_id}/requirements
GET    /api/v1/requirements/{id}
PUT    /api/v1/requirements/{id}
DELETE /api/v1/requirements/{id}
POST   /api/v1/requirements/{id}/transition
POST   /api/v1/requirements/{id}/ai-analyze
GET    /api/v1/requirements/{id}/history
```

#### Tasks
```
GET    /api/v1/requirements/{req_id}/tasks
POST   /api/v1/requirements/{req_id}/tasks
GET    /api/v1/tasks/{id}
PUT    /api/v1/tasks/{id}
DELETE /api/v1/tasks/{id}
POST   /api/v1/tasks/{id}/generate-tests
```

#### Test Cases
```
GET    /api/v1/requirements/{req_id}/test-cases
POST   /api/v1/requirements/{req_id}/test-cases
GET    /api/v1/test-cases/{id}
PUT    /api/v1/test-cases/{id}
DELETE /api/v1/test-cases/{id}
POST   /api/v1/test-cases/{id}/run
```

#### Automation
```
GET    /api/v1/projects/{project_id}/automation-rules
POST   /api/v1/projects/{project_id}/automation-rules
GET    /api/v1/automation-rules/{id}
PUT    /api/v1/automation-rules/{id}
DELETE /api/v1/automation-rules/{id}
POST   /api/v1/automation-rules/{id}/test
```

#### Analytics
```
GET    /api/v1/projects/{project_id}/analytics/cycle-time
GET    /api/v1/projects/{project_id}/analytics/cfd
GET    /api/v1/projects/{project_id}/analytics/efficiency
GET    /api/v1/projects/{project_id}/analytics/bottlenecks
```

## 5. State Machine Architecture

### Requirement State Machine

```python
class RequirementState:
    NEW = "new"
    ANALYSIS = "analysis"
    DESIGN = "design"
    DEVELOPMENT = "development"
    TESTING = "testing"
    COMPLETED = "completed"

class RequirementStateMachine:
    NON_TECHNICAL_TRANSITIONS = {
        RequirementState.NEW: [RequirementState.ANALYSIS],
        RequirementState.ANALYSIS: [RequirementState.DESIGN, RequirementState.NEW],
        RequirementState.DESIGN: [RequirementState.ANALYSIS, RequirementState.COMPLETED],
        RequirementState.COMPLETED: [RequirementState.DESIGN]
    }

    TECHNICAL_TRANSITIONS = {
        RequirementState.NEW: [RequirementState.ANALYSIS],
        RequirementState.ANALYSIS: [RequirementState.DESIGN, RequirementState.NEW],
        RequirementState.DESIGN: [RequirementState.ANALYSIS, RequirementState.DEVELOPMENT],
        RequirementState.DEVELOPMENT: [RequirementState.DESIGN, RequirementState.TESTING],
        RequirementState.TESTING: [RequirementState.DEVELOPMENT, RequirementState.COMPLETED],
        RequirementState.COMPLETED: [RequirementState.TESTING]
    }

    @staticmethod
    def can_transition(from_state, to_state, project_type):
        transitions = (
            RequirementStateMachine.TECHNICAL_TRANSITIONS
            if project_type == "technical"
            else RequirementStateMachine.NON_TECHNICAL_TRANSITIONS
        )
        return to_state in transitions.get(from_state, [])

    @staticmethod
    def is_backward_transition(from_state, to_state, project_type):
        transitions = (
            RequirementStateMachine.TECHNICAL_TRANSITIONS
            if project_type == "technical"
            else RequirementStateMachine.NON_TECHNICAL_TRANSITIONS
        )
        state_order = [RequirementState.NEW, RequirementState.ANALYSIS, RequirementState.DESIGN,
                       RequirementState.DEVELOPMENT, RequirementState.TESTING, RequirementState.COMPLETED]
        try:
            return state_order.index(to_state) < state_order.index(from_state)
        except ValueError:
            return False
```

## 6. AI Service Architecture

### AI Service Layer

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        AI Service Manager                               │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        ▼                           ▼                           ▼
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  Triage Service │      │  Duplicate      │      │  Task Breakdown │
│                 │      │  Detection      │      │  Generator      │
└─────────────────┘      └─────────────────┘      └─────────────────┘
        │                           │                           │
        ▼                           ▼                           ▼
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  Claude API     │      │  Embedding +    │      │  Claude API     │
│  (Direct)       │      │  Vector Search  │      │  (Prompt)       │
└─────────────────┘      └─────────────────┘      └─────────────────┘
```

### AI Triage Service

```python
class AITriageService:
    """
    Analyzes incoming requirements and provides:
    - Priority classification
    - Complexity estimation
    - Skill requirements
    - Suggested assignees
    """

    async def triage_requirement(self, requirement: Requirement) -> TriageResult:
        prompt = self._build_triage_prompt(requirement)
        response = await self.claude_client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )

        result = self._parse_triage_response(response)
        await self._update_requirement_with_triage(requirement.id, result)
        return result

    def _build_triage_prompt(self, requirement: Requirement) -> str:
        return f"""Analyze this requirement and provide a JSON response:

Title: {requirement.title}
Description: {requirement.description}

Return JSON with:
{{
  "priority": "high" | "medium" | "low",
  "complexity": 1-10,
  "estimated_days": number,
  "required_skills": ["skill1", "skill2"],
  "suggested_assignee": "username or null",
  "reasoning": "brief explanation"
}}
"""
```

### Duplicate Detection Service

```python
class DuplicateDetectionService:
    """
    Detects duplicate or similar requirements using:
    - Semantic similarity (embeddings + cosine similarity)
    - Exact title matching
    - Keyword overlap
    """

    async def find_duplicates(
        self,
        requirement: Requirement,
        threshold: float = 0.85
    ) -> List[PotentialDuplicate]:
        # Get embedding for new requirement
        embedding = await self._get_embedding(requirement)

        # Search for similar requirements in the same project
        similar = await self.vector_store.similarity_search(
            vector=embedding,
            collection=f"project_{requirement.project_id}",
            threshold=threshold,
            limit=10
        )

        # Calculate detailed similarity scores
        duplicates = []
        for req_id, score in similar:
            other_req = await self.repo.get(req_id)
            similarity = await self._calculate_detailed_similarity(
                requirement, other_req
            )
            if similarity.overall_score >= threshold:
                duplicates.append(PotentialDuplicate(
                    requirement_id=other_req.id,
                    req_number=other_req.req_number,
                    title=other_req.title,
                    overall_score=similarity.overall_score,
                    title_similarity=similarity.title_similarity,
                    description_similarity=similarity.description_similarity,
                    keyword_overlap=similarity.keyword_overlap
                ))

        return sorted(duplicates, key=lambda x: x.overall_score, reverse=True)

    async def _get_embedding(self, requirement: Requirement) -> List[float]:
        text = f"{requirement.title} {requirement.description}"
        response = await self.openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
```

### Task Breakdown Generator

```python
class TaskBreakdownGenerator:
    """
    Generates development task breakdowns from requirements
    """

    async def generate_tasks(
        self,
        requirement: Requirement,
        include_tests: bool = True
    ) -> List[GeneratedTask]:
        prompt = self._build_breakdown_prompt(requirement, include_tests)
        response = await self.claude_client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        )

        tasks = self._parse_task_response(response)
        return tasks

    def _build_breakdown_prompt(
        self,
        requirement: Requirement,
        include_tests: bool
    ) -> str:
        return f"""Break down this requirement into development tasks:

Title: {requirement.title}
Description: {requirement.description}

Return JSON array of tasks:
[
  {{
    "title": "task title",
    "description": "detailed description",
    "estimated_hours": number,
    "dependencies": ["task_index or null"],
    "test_cases": ["test description"] if include_tests else []
  }}
]

Break down into atomic, completable tasks.
"""
```

## 7. GitHub Integration Architecture

### GitHub Service Components

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      GitHub Integration Service                          │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        ▼                           ▼                           ▼
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  Webhook        │      │  PR Sync       │      │  Commit Linking │
│  Handler        │      │  Service        │      │  Service        │
└─────────────────┘      └─────────────────┘      └─────────────────┘
```

### Webhook Handling

```python
class GitHubWebhookHandler:
    async def handle_webhook(self, payload: dict, signature: str):
        # Verify webhook signature
        if not self._verify_signature(payload, signature):
            raise HTTPException(status_code=401)

        event_type = payload.get("action")

        if event_type == "opened":
            await self._handle_pr_opened(payload)
        elif event_type == "closed":
            await self._handle_pr_closed(payload)
        elif event_type == "synchronize":
            await self._handle_pr_updated(payload)

    async def _handle_pr_opened(self, payload: dict):
        pr_data = {
            "number": payload["pull_request"]["number"],
            "title": payload["pull_request"]["title"],
            "url": payload["pull_request"]["html_url"],
            "author": payload["pull_request"]["user"]["login"],
            "branch": payload["pull_request"]["head"]["ref"]
        }

        # Find associated task from PR title pattern "TASK-XXX: title"
        task_number = self._extract_task_number(pr_data["title"])
        if task_number:
            await self.task_repo.update_pr_url(task_number, pr_data["url"])
```

## 8. Automation Engine Architecture

### Automation Rule Engine

```python
class AutomationEngine:
    """
    Evaluates and executes automation rules based on events
    """

    async def process_event(self, event: AutomationEvent):
        # Get all active rules for the project
        rules = await self.rule_repo.get_active_rules(event.project_id)

        for rule in rules:
            # Check if rule matches trigger
            if self._matches_trigger(rule, event):
                # Check conditions
                if await self._check_conditions(rule, event):
                    # Execute actions
                    await self._execute_actions(rule, event)

    def _matches_trigger(self, rule: AutomationRule, event: AutomationEvent) -> bool:
        trigger_type = rule.trigger_config["type"]
        return trigger_type == event.type

    async def _check_conditions(
        self,
        rule: AutomationRule,
        event: AutomationEvent
    ) -> bool:
        for condition in rule.conditions:
            if not await self._evaluate_condition(condition, event):
                return False
        return True

    async def _execute_actions(
        self,
        rule: AutomationRule,
        event: AutomationEvent
    ):
        for action in rule.actions:
            action_type = action["type"]
            if action_type == "send_notification":
                await self._send_notification(action, event)
            elif action_type == "assign_user":
                await self._assign_user(action, event)
            elif action_type == "update_field":
                await self._update_field(action, event)
```

## 9. Analytics Engine Architecture

### Cycle Time Calculator

```python
class CycleTimeCalculator:
    """
    Calculates cycle time metrics for requirements
    """

    async def calculate_project_cycle_time(
        self,
        project_id: str,
        from_date: datetime,
        to_date: datetime
    ) -> CycleTimeMetrics:
        requirements = await self.req_repo.get_completed_in_range(
            project_id, from_date, to_date
        )

        cycle_times = []
        for req in requirements:
            transitions = await self.transition_repo.get_by_requirement(req.id)
            cycle_time = self._calculate_total_cycle_time(transitions)
            cycle_times.append(cycle_time)

        return CycleTimeMetrics(
            average=sum(cycle_times) / len(cycle_times),
            median=statistics.median(cycle_times),
            p90=statistics.quantiles(cycle_times, n=10)[8],
            min=min(cycle_times),
            max=max(cycle_times),
            count=len(cycle_times)
        )
```

### CFD (Cumulative Flow Diagram) Generator

```python
class CFDGenerator:
    """
    Generates Cumulative Flow Diagram data
    """

    async def generate_cfd(
        self,
        project_id: str,
        from_date: datetime,
        to_date: datetime
    ) -> List[CFDDataPoint]:
        # Get all transitions in the period
        transitions = await self.transition_repo.get_in_range(
            project_id, from_date, to_date
        )

        # Build cumulative counts per lane per day
        daily_counts = defaultdict(lambda: defaultdict(int))

        for transition in transitions:
            day = transition.created_at.date()
            daily_counts[day][transition.to_status] += 1

        # Calculate cumulative values
        cfd_data = []
        cumulative = defaultdict(int)

        for day in sorted(daily_counts.keys()):
            for lane, count in daily_counts[day].items():
                cumulative[lane] += count

            cfd_data.append(CFDDataPoint(
                date=day,
                new=cumulative["new"],
                analysis=cumulative["analysis"],
                design=cumulative["design"],
                development=cumulative["development"],
                testing=cumulative["testing"],
                completed=cumulative["completed"]
            ))

        return cfd_data
```

## 10. Security Architecture

### Authentication & Authorization

```python
# JWT Authentication
class JWTAuthenticator:
    def create_token(self, user_id: str) -> str:
        payload = {
            "sub": user_id,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        return jwt.encode(payload, self.secret_key, algorithm="HS256")

    def verify_token(self, token: str) -> str:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload["sub"]
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

# Project-Based Authorization
class ProjectAuthorizer:
    async def check_access(
        self,
        user_id: str,
        project_id: str,
        required_permission: str
    ) -> bool:
        project = await self.project_repo.get(project_id)

        # Project creator has all permissions
        if project.created_by == user_id:
            return True

        # Check project membership
        membership = await self.membership_repo.get(user_id, project_id)
        if not membership:
            return False

        return required_permission in membership.permissions
```

### Data Isolation

All queries include project_id filtering to ensure data isolation:

```python
class RequirementRepository:
    async def get_all(self, project_id: str, user_id: str) -> List[Requirement]:
        """Always filters by project_id for security"""
        await self.authorizer.check_access(user_id, project_id, "read")

        query = select(Requirement).where(
            Requirement.project_id == project_id
        )
        return await self.db.execute(query)
```

## 11. Caching Strategy

### Cache Layers

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Application Layer                             │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         Redis Cache (L1)                               │
│  - Session data                                                        │
│  - Hot project data (1 hour)                                           │
│  - User permissions (30 min)                                            │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        PostgreSQL Database (L2)                         │
│  - Persistent data storage                                             │
│  - Query result caching via prepared statements                        │
└─────────────────────────────────────────────────────────────────────────┘
```

### Cache Keys Pattern

```python
class CacheKeys:
    PROJECT = "project:{project_id}"
    PROJECT_REQUIREMENTS = "project:{project_id}:requirements"
    REQUIREMENT = "requirement:{requirement_id}"
    USER_PERMISSIONS = "user:{user_id}:permissions:{project_id}"
    ANALYTICS_CFD = "analytics:cfd:{project_id}:{date_range_hash}"
```

## 12. Error Handling Strategy

### Error Types

```python
class StratosError(Exception):
    """Base exception for Stratos errors"""

class NotFoundError(StratosError):
    """Resource not found"""

class ValidationError(StratosError):
    """Validation error"""

class TransitionError(StratosError):
    """Invalid state transition"""

class AuthorizationError(StratosError):
    """Authorization failure"""

class AIServiceError(StratosError):
    """AI service error"""

class GitHubIntegrationError(StratosError):
    """GitHub integration error"""
```

### Global Error Handler

```python
@app.exception_handler(StratosError)
async def stratos_error_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"error": exc.__class__.__name__, "message": str(exc)}
    )

@app.exception_handler(NotFoundError)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "not_found", "message": str(exc)}
    )
```

## 13. Monitoring & Observability

### Metrics Collection

```python
# Prometheus metrics
from prometheus_client import Counter, Histogram, Gauge

requirement_created = Counter(
    'stratos_requirement_created_total',
    'Total number of requirements created',
    ['project_id', 'priority']
)

requirement_transition_duration = Histogram(
    'stratos_requirement_transition_duration_seconds',
    'Time requirements spend in each lane',
    ['from_state', 'to_state']
)

active_requirements = Gauge(
    'stratos_active_requirements',
    'Number of active requirements',
    ['project_id', 'state']
)

api_request_duration = Histogram(
    'stratos_api_request_duration_seconds',
    'API request duration',
    ['endpoint', 'method']
)
```

### Distributed Tracing

```python
from opentelemetry import trace
tracer = trace.get_tracer(__name__)

@tracer.start_as_current_span("create_requirement")
async def create_requirement(project_id: str, data: dict):
    current_span = trace.get_current_span()
    current_span.set_attribute("project_id", project_id)
    current_span.set_attribute("priority", data.get("priority"))

    # ... implementation ...
```

## 14. Deployment Architecture

### Docker Services

```yaml
# docker-compose.yml
version: '3.8'

services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://api:8000

  api:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/stratos
      - REDIS_URL=redis://redis:6379
      - CLAUDE_API_KEY=${CLAUDE_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=stratos
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  postgres_data:
  redis_data:
  grafana_data:
```
