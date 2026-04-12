# Stratos Management System - Backend Design Document

## 1. 项目结构

```
backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── projects.py
│   │   │   │   ├── requirements.py
│   │   │   │   ├── tasks.py
│   │   │   │   ├── test_cases.py
│   │   │   │   ├── automation.py
│   │   │   │   ├── analytics.py
│   │   │   │   ├── users.py
│   │   │   │   ├── lane_roles.py          # 泳道角色配置
│   │   │   │   ├── agents.py               # AI Agent 管理
│   │   │   │   └── lark.py                # 飞书集成
│   │   │   └── router.py
│   │   └── deps.py          # Dependency injection
│   ├── core/
│   │   ├── config.py         # Configuration settings
│   │   ├── security.py       # JWT, auth logic
│   │   ├── cache.py          # Redis cache
│   │   └── logger.py         # Logging setup
│   ├── services/
│   │   ├── project_service.py
│   │   ├── requirement_service.py
│   │   ├── task_service.py
│   │   ├── test_case_service.py
│   │   ├── ai_service.py
│   │   ├── deepagent_service.py    # DeepAgent 集成
│   │   ├── github_service.py
│   │   ├── lark_service.py        # 飞书服务
│   │   ├── automation_service.py
│   │   └── analytics_service.py
│   ├── models/
│   │   ├── base.py           # Base model
│   │   ├── project.py
│   │   ├── requirement.py
│   │   ├── task.py
│   │   ├── test_case.py
│   │   user.py
│   │   ├── team_member.py
│   │   └── lane_role.py
│   ├── repositories/
│   │   ├── base.py           # Base repository
│   │   ├── project_repository.py
│   │   ├── requirement_repository.py
│   │   ├── task_repository.py
│   │   └── test_case_repository.py
│   ├── schemas/
│   │   ├── project.py
│   │   ├── requirement.py
│   │   ├── task.py
│   │   └── test_case.py
│   ├── state_machine/
│   │   ├── base.py
│   │   └── requirement_state_machine.py
│   ├── agents/
│   │   ├── base_agent.py
│   │   ├── analysis_agent.py        # 需求分析 Agent
│   │   ├── design_agent.py          # 方案设计 Agent
│   │   ├── development_agent.py      # 开发 Agent
│   │   └── testing_agent.py        # 测试 Agent
│   ├── utils/
│   │   ├── validators.py
│   │   └── helpers.py
│   └── skills/                     # DeepAgent Skills (SKILL.md)
│      ra── analysis/
│       │   └── SKILL.md
│       ├── design/
│       │   └── SKILL.md
│       ├── development/
│       │   └── SKILL.md
│       └── testing/
│           └── SKILL.md
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── alembic/                  # Database migrations
├── main.py                   # Application entry point
├── requirements.txt
├── Dockerfile
└── pyproject.toml
```

## 2. 核心配置

```python
# app/core/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Stratos API"
    APP_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10

    # Redis
    REDIS_URL: str
    REDIS_POOL_SIZE: int = 10

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # AI Services
    CLAUDE_API_KEY: str
    CLAUDE_MODEL: str = "claude-3-5-sonnet-20240620"
    OPENAI_API_KEY: str
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # DeepAgent 配置
    DEEPAGENT_API_URL: str
    DEEPAGENT_API_KEY: str

    # GitHub
    GITHUB_APP_ID: str
    GITHUB_PRIVATE_KEY: str
    GITHUB_WEBHOOK_SECRET: str

    # 飞书配置
    LARK_APP_ID: str
    LARK_APP_SECRET: str
    LARK_ENCRYPT_KEY: str = ""
    LARK_VERIFICATION_TOKEN: str = ""

    @classmethod
    @lru_cache
    def get(cls):
        return cls()
```

## 3. 数据库模型

### 扩展的需求模型（包含飞书集成）

```sql
-- requirements 表（扩展版）
CREATE TABLE requirements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    req_number INTEGER NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'new',
    priority VARCHAR(20) NOT NULL DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high')),

    -- 飞书集成
    source VARCHAR(50),  -- lark, wechat, direct, etc
    source_metadata JSONB,  -- 原始来源数据
    lark_doc_token VARCHAR(255),  -- 关联的飞书文档token
    lark_doc_url VARCHAR(500),  -- 飞书文档URL
    lark_editable BOOLEAN DEFAULT FALSE,  -- 是否可编辑飞书文档

    -- AI 分析结果
    ai_confidence DECIMAL(5,2),
    ai_suggestions JSONB,
    current_agent VARCHAR(100),  -- 当前处理中的 Agent
    current_thread_id VARCHAR(255),  -- DeepAgent 线程 ID

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID NOT NULL REFERENCES users(id),
    assigned_to UUID REFERENCES users(id),

    return_count INTEGER DEFAULT 0,
    last_returned_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    archived_at TIMESTAMP WITH TIME ZONE,

    UNIQUE(project_id, req_number)
);

-- 泳道角色配置表
CREATE TABLE lane_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    lane VARCHAR(50) NOT NULL,  -- analysis, design, etc
    role_name VARCHAR(255) NOT NULL,  -- 角色名称
    agent_type VARCHAR(100) NOT NULL,  -- analysis_agent, design_agent, etc
    is_active BOOLEAN DEFAULT TRUE,
    config JSONB DEFAULT '{}',  -- Agent 配置
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(project_id, lane)
);

-- 团队成员表
CREATE TABLE team_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    nickname VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    role VARCHAR(100),
    type VARCHAR(20) NOT NULL CHECK (type IN ('human', 'ai')),
    avatar_url VARCHAR(500),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- AI Agent 特有字段
    skills JSONB DEFAULT '[]',
    memory_enabled BOOLEAN DEFAULT TRUE,
    memory_document_id VARCHAR(255),

    UNIQUE(project_id, type, role)
);

-- Agent 执行记录表
CREATE TABLE agent_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requirement_id UUID NOT NULL REFERENCES requirements(id) ON DELETE CASCADE,
    agent_type VARCHAR(100) NOT NULL,
    lane VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,  -- running, completed, failed
    input_data JSONB,
    output_data JSONB,
    error_message TEXT,
    thread_id VARCHAR(255),  -- DeepAgent 线程 ID
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    INDEX idx_agent_executions_requirement (requirement_id)
);
```

## 4. DeepAgent 集成服务（符合最佳实践）

```python
# app/services/deepagent_service.py
import httpx
from typing import Dict, Optional
from app.core.config import Settings

class DeepAgentService:
    """
    DeepAgent 集成服务
    遵循 Deep Agents 最佳实践：
    - 使用 thread_id 实现会话持久化
    - 支持 checkpointer 用于中断恢复
    - 使用 CompositeBackend 混合存储策略
    """

    def __init__(self, settings: Settings):
        self.api_url = settings.DEEPAGENT_API_URL
        self.api_key = settings.DEEPAGENT_API_KEY
        self.client = httpx.AsyncClient(
            base_url=self.api_url,
            headers={"Authorization": f"Bearer {self.api_key}"}
        )

    async def execute_agent(
        self,
        agent_type: str,
        input_data: Dict,
        requirement_id: str,
        lane: str,
        thread_id: Optional[str] = None,
        config: Optional[Dict] = None,
        checkpointer: Optional[Dict] = None
    ) -> Dict:
        """
        执行指定的 Agent

        使用 Deep Agents 最佳实践：
        - thread_id: 会话持久化
        - checkpointer: 中断恢复
        - config: Agent 特定配置
        """
        # 记录执行开始
        execution_id = await self._create_execution_record(
            requirement_id, agent_type, lane, input_data, thread_id
        )

        try:
            # 调用 DeepAgent API，包含最佳实践参数
            payload = {
                "agent_type": agent_type,
                "input": input_data,
                "thread_id": thread_id,  # 会话持久化
                "checkpointer": checkpointer,  # 中断恢复
                "config": config or {}
            }

            response = await self.client.post("/execute", json=payload)
            response.raise_for_status()

            result = response.json()

            # 更新执行记录
            await self._update_execution_record(
                execution_id, "completed", result
            )

            return result

        except Exception as e:
            # 更新执行记录为失败
            await self._update_execution_recorded(
                execution_id, "failed", None, str(e)
            )
            raise

    async def get_agent_thread(
        self,
        thread_id: str
    ) -> Dict:
        """
        获取 Agent 线程状态（用于会话恢复）
        """
        response = await self.client.get(f"/threads/{thread_id}")
        response.raise_for_status()
        return response.json()

    async def create_thread(
        self,
        thread_id: str,
        initial_state: Optional[Dict] = None
    ) -> Dict:
        """
        创建新的 Agent 线程
        """
        response = await self.client.post("/threads", json={
            "thread_id": thread_id,
            "initial_state": initial_state
        })
        response.raise_for_status()
        return response.json()

    async def resume_from_checkpoint(
        self,
        thread_id: str,
        checkpoint: Dict
    ) -> Dict:
        """
        从检查点恢复 Agent 执行

        用于中断后恢复执行
        """
        response = await self.client.post(f"/threads/{thread_id}/resume", json={
            "checkpoint": checkpoint
        })
        response.raise_for_status()
        return response.json()

    async def _create_execution_record(
        self,
        requirement_id: str,
        agent_type: str,
        lane: str,
        input_data: Dict,
        thread_id: Optional[str]
    ) -> str:
        """创建 Agent 执行记录"""
        from app.repositories.agent_execution_repository import AgentExecutionRepository
        repo = AgentExecutionRepository()

        execution = await repo.create({
            "requirement_id": requirement_id,
            "agent_type": agent_type,
            "lane": lane,
            "status": "running",
            "input_data": input_data,
            "thread_id": thread_id,
        })

        return str(execution.id)

    async def _update_execution_record(
        self,
        execution_id: str,
        status: str,
        output_data: Optional[Dict],
        error_message: Optional[str] = None
    ):
        """更新 Agent 执行记录"""
        from app.repositories.agent_execution_repository import AgentExecutionRepository
        repo = AgentExecutionRepository()

        update_data = {
            "status": status,
            "output_data": output_data,
            "error_message": error_message
        }

        if status != "running":
            update_data["completed_at"] = datetime.now(timezone.utc)

        await repo.update(execution_id, update_data)
```

## 5. 泳道 Agent 系统（使用 Deep Agents）

```python
# app/agents/base_agent.py
from abc import ABC, abstractmethod
from typing import Dict
from app.services.deepagent_service import DeepAgentService
from app.services.lark_service import LarkService

class BaseAgent(ABC):
    """基础 Agent 类"""

    def __init__(
        self,
        deepagent_service: DeepAgentService,
        lark_service: LarkService,
        config: Dict
    ):
        self.deepagent = deepagent_service
        self.lark = lark_service
        self.config = config

    @abstractmethod
    async def process(self, requirement_data: Dict, context: Dict) -> Dict:
        """处理需求，返回结果"""
        pass

    @abstractmethod
    def get_agent_type(self) -> str:
        """返回 Agent 类型标识"""
        pass

    async def execute_with_deepagent(
        self,
        input_data: Dict,
        thread_id: Optional[str] = None,
        checkpointer: Optional[Dict] = None
    ) -> Dict:
        """通过 DeepAgent 执行 Agent（使用最佳实践）"""
        return await self.deepagent.execute_agent(
            agent_type=self.get_agent_type(),
            input_data=input_data,
            requirement_id=input_data["requirement_id"],
            lane=input_data.get("lane", ""),
            thread_id=thread_id,
            checkpointer=checkpointer,
            config=self.config
        )
```

## 6. DeepAgent Skills 配置

### 需求分析 Skill

```markdown
---
name: requirement_analysis
description: Analyze requirements, detect duplicates, and provide triage information
---

# Requirement Analysis Skill

## Overview
This skill provides comprehensive requirement analysis including priority assessment, complexity estimation, and duplicate detection.

## When to Use
- When a requirement enters the "Analysis" lane
- When explicitly requested by a user
- During backlog prioritization

## Instructions
1. **Analyze the requirement**:
   - Read the title and description carefully
   - Identify key features and components
   - Estimate complexity (1-10 scale)

2. **Determine priority**:
   - High: Business critical, security issues, major features
   - Medium: Standard features, enhancements
   - Low: Nice-to-have, minor fixes

3. Provide output as JSON:
```json
{
  "priority": "high|medium|low",
  "complexity": 1-10,
  "estimated_days": number,
  "required_skills": ["skill1", "skill2"],
  "suggested_assignee": "username or null",
  "risk_assessment": {
    "technical_complexity": "low|medium|high",
    "dependencies": ["dependency1", "dependency2"],
    "potential_challenges": ["challenge1"]
  }
}
```

## Available Tools
- search_database: Search for similar requirements
- query_ai_knowledge: Access internal knowledge base
```

### 方案设计 Skill

```markdown
---
name: design_generation
description: Generate design specifications, wireframes, and UI prototypes
---

## When to Use
- When a requirement enters the "Design" lane
- When design documentation is requested

## Instructions
Generate comprehensive design specifications including:
1. Architecture recommendations
2. Data model changes
3. API endpoint designs
4. UI/UX wireframes

Output format:
```json
{
  "architecture": "description",
  "data_models": [{"name": "type", "fields": []}],
  "api_endpoints": [{"method": "path", "description": ""}],
  "ui_wireframes": ["component1", "component2"]
}
```
```

### 开发 Skill

```markdown
---
name: code_generation
description: Generate implementation code, tests, and documentation
---

## When to Use
- When a requirement enters the "Development" lane
- When code implementation is requested

## Instructions
Generate production-ready code including:
1. Core implementation
2. Unit tests
3. Integration tests
4. Documentation

Follow project coding standards and patterns.
```

### 测试 Skill

```markdown
---
name: test_generation
description: Generate comprehensive test cases and test execution plans
---

## When to Use
- When a requirement enters the "Testing" lane
- When test coverage needs improvement

## Instructions
Generate:
1. Unit tests for the specific feature
2. Integration tests
3. End-to-end test scenarios
4. Performance test cases if applicable

Ensure tests follow project testing standards.
```

## 7. 状态管理设计

```python
# app/services/requirement_service.py
from typing import Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.requirement_repository import RequirementRepository
from app.services.lark_service import LarkService

class RequirementService:
    def __init__(
        self,
        req_repo: RequirementRepository,
        lark_service: LarkService
    ):
        self.req_repo = req_repo
        self.lark = lark_service

    async def create_from_lark(
        self,
        project_id: str,
        lark_message: Dict,
        user_id: str,
        db: AsyncSession
    ) -> Dict:
        """从飞书消息创建需求"""
        # 解析飞书消息
        title = self._extract_title(lark_message)
        description = self._extract_description(lark_message)
        chat_id = lark_message.get("sender", {}).get("sender_id", {}).get("open_id")

        # 创建需求
        req_number = await self.req_repo.get_next_number(project_id, db)

        # 检查用户是否有飞书文档创建/（编辑权限
        has_edit_permission = await self.lark.get_document_permission(
            "", chat_id  # 需要根据实际情况调整
        )

        # 如果有权限，创建关联的飞书文档
        lark_doc = None
        if has_edit_permission:
            lark_doc = await self.lark.create_document(
                title=f"REQ-{req_number}: {title}",
                content=f"# {title}\n\n{description}"
            )

        # 创建需求记录
        requirement = await self.req_repo.create({
            "project_id": project_id,
            "req_number": req_number,
            "title": title,
            "description": description,
            "source": "lark",
            "source_metadata": lark_message,
            "lark_doc_token": lark_doc["token"] if lark_doc else None,
            "lark_doc_url": lark_doc["url"] if lark_doc else None,
            "lark_editable": has_edit_permission,
            "created_by": user_id,
        }, db)

        return requirement

    async def transition_with_agent(
        self,
        requirement_id: str,
        to_status: str,
        user_id: str,
        db: AsyncSession,
        thread_id: Optional[str] = None
    ) -> Dict:
        """通过 Agent 执行状态转换"""
        requirement = await self.req_repo.get(requirement_id, db)

        # 获取目标泳道的 Agent 配置
        lane_role = await self._get_lane_role(requirement.project_id, to_status, db)

        if lane_role and lane_role.get("agent_type"):
            # 执行对应的 Agent
            result = await self._execute_lane_agent(
                requirement, lane_role, db, thread_id
            )

            # Agent 执行成功后，更新状态
            if result.get("success"):
                await self._update_requirement_status(
                    requirement_id, to_status, result, db
                )

            return result
        else:
            # 没有 Agent 配置，直接更新状态
            return await self._update_requirement_status(
                requirement_id, to_status, {}, db
            )

    async def _get_lane_role(
        self,
        project_id: str,
        lane: str,
        db: AsyncSession
    ) -> Optional[Dict]:
        """获取泳道对应的角色和 Agent 配置"""
        from app.repositories.lane_role_repository import LaneRoleRepository
        repo = LaneRoleRepository()

        lane_role = await repo.find_by_project_and_lane(project_id, lane, db)
        if lane_role and lane_role.is_active:
            return {
                "role_name": lane_role.role_name,
                "agent_type": lane_role.agent_type,
                "config": lane_role.config
            }
        return None

    async def _execute_lane_agent(
        self,
        requirement: Dict,
        lane_role: Dict,
        db: AsyncSession,
        thread_id: Optional[str]
    ) -> Dict:
        """执行泳道对应的 Agent"""
        from app.agents import get_agent_class

        agent_class = get_agent_class(lane_role["agent_type"])
        agent = agent_class(
            deepagent_service=self.deepagent,
            lark_service=self.lark,
            config=lane_role["config"]
        )

        # 获取上下文信息
        context = await self._build_agent_context(requirement, db)

        # 执行 Agent，传入 thread_id
        result = await agent.process(requirement, context, thread_id=thread_id)

        return result
```

## 8. API 端点（扩展）

```python
# app/api/v1/endpoints/agents.py
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.agent import AgentCreate, AgentResponse, ThreadCreate

router = APIRouter()

@router.post("/projects/{project_id}/agents")
async def create_ai_agent(
    project_id: str,
    data: AgentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """创建 AI Agent（遵循 Deep Agents 最佳实践）"""
    # 验证角色唯一性
    existing_agent = await check_agent_exists(
        project_id, data.role, db
    )
    if existing_agent:
        raise HTTPException(
            status_code=400,
            detail=f"Agent with role '{data.role}' already exists"
        )

    # 创建 Agent
    agent = await agent_repo.create({
        "project_id": project_id,
        "name": data.name,
        "nickname": data.nickname,
        "role": data.role,
        "type": "ai",
        "skills": data.skills,
        "memory_enabled": data.memory_enabled,
        # DeepAgent 特定配置
        "deepagent_config": {
            "agent_type": data.agent_type,
            "model": data.get("model", "claude-3-5-sonnet-20240620"),
            "temperature": data.get("temperature", 0.5),
            "skills": ["./skills/analysis"],  # 使用 SKILL.md
        }
    }, db)

    return agent

@router.get("/projects/{project_id}/agents")
async def get_agents(
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取项目的所有 Agent"""
    agents = await agent_repo.get_by_project(project_id, db)
    return {
        "members": [a for a in agents if a.type == "human"],
        "ai_agents": [a for a in agents if a.type == "ai"]
    }

@router.get("/agents/{agent_id}/memory")
async def get_agent_memory(
    agent_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取 Agent 记忆（通过 DeepAgent 的 StoreBackend）"""
    agent = await agent_repo.get(agent_id, db)

    if not agent.memory_enabled:
        raise HTTPException(
            status_code=400,
            detail="Memory not enabled for this agent"
        )

    # 使用 DeepAgent 的 thread_id 获取记忆
    if agent.current_thread_id:
        thread_data = await deepagent_service.get_agent_thread(
            agent.current_thread_id
        )
        return {
            "agent_id": agent_id,
            "thread_id": agent.current_thread_id,
            "memory": thread_data.get("state", {}),
            "last_updated": agent.updated_at
        }
    else:
        return {
            "agent_id": agent_id,
            "memory": {},
            "message": "No thread ID available"
        }

@router.post("/agents/{agent_id}/memory")
async def update_agent_memory(
    agent_id: str,
    content: Dict,
    db: AsyncSession = Depends(get_db)
):
    """更新 Agent 记忆（通过 DeepAgent 的 StoreBackend）"""
    agent = await agent_repo.get(agent_id, db)

    if not agent.memory_enabled:
        raise HTTPException(
            status_code=400,
            detail="Memory not enabled for this agent"
        )

    # 确保 agent 有 thread_id
    if not agent.current.current_thread_id:
        # 创建新线程
        thread_result = await deepagent_service.create_thread(
            thread_id=f"agent-{agent_id}",
            initial_state=content
        )
        # 更新 agent 的 thread_id
        await agent_repo.update(agent_id, {
            "current_thread_id": thread_result["id"]
        })
    else:
        # 通过 checkpointer 更新状态
        await deepagent_service.resume_from_checkpoint(
            agent.current_thread_id,
            {"state": content}
        )

    return {"status": "success", "thread_id": agent.current_thread_id}

@router.post("/agents/{agent_id}/execute")
async def execute_agent_direct(
    agent_id: str,
    input_data: Dict,
    db: AsyncSession = Depends(get_db)
):
    """直接执行 Agent（用于测试或手动触发）"""
    agent = await agent_repo.get(agent_id, db)

    result = await deepagent_service.execute_agent(
        agent_type=agent.agent_type,
        input_data=input={**input_data, "requirement_id": input_data.get("requirement_id")},
        requirement_id=input_data.get("requirement_id"),
        lane=input_data.get("lane", agent.role),
        thread_id=agent.current_thread_id,
        config=agent.deepagent_config
    )

    return result
```

## 9. 飞书服务

```python
# app/services/lark_service.py
import httpx
from typing import Dict, Optional, List
from datetime import datetime

class LarkService:
    """飞书集成服务"""

    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.base_url = "https://open.feishu.cn/open-apis"
        self.access_token: Optional[str] = None
        self.client = httpx.AsyncClient()

    async def get_access_token(self) -> str:
        """获取飞书访问令牌"""
        if self.access_token:
            return self.access_token

        response = await self.client.post(
            f"{self.base_url}/auth/v3/tenant_access_token/internal",
            json={
                "app_id": self.app_id,
                "app_secret": self.app_secret
            }
        )

        result = response.json()
        if result.get("code") != 0:
            raise Exception(f"Failed to get access token: {result}")

        self.access_token = result["tenant_access_token"]
        return self.access_token

    async def create_document(
        self,
        title: str,
        content: str
    ) -> Dict:
        """创建飞书文档"""
        token = await self.get_access_token()

        response = await self.client.post(
            f"{self.base_url}/docx/v1/documents",
            headers={"Authorization": f"Bearer {token}"},
            json={"title": title}
        )

        result = response.json()
        if result.get("code") != 0:
            raise Exception(f"Failed to create document: {result}")

        doc_token = result["data"]["document"]["document_id"]

        # 写入内容
        await self.append_to_document(doc_token, content)

        return {
            "token": doc_token,
            "url": f"https://feishu.cn/docx/{doc_token}"
        }

    async def append_to_document(
        self,
        doc_token: str,
        content: str,
        position: str = "END"
    ):
        """追加内容到飞书文档"""
        token = await self.get_access_token()

        # 转换 Markdown 内容为飞书文档块
        blocks = self._markdown_to_blocks(content)

        response = await self.client.post(
            f"{self.base_url}/docx/v1/documents/{doc_token}/blocks/{position}/children",
            headers={"Authorization": f"Bearer {token}"},
            json={"children": blocks, "index": -1}
        )

        result = response.json()
        if result.get("code") != 0:
            raise Exception(f"Failed to append to document: {result}")

    async def get_document_permission(
        self,
        doc_token: str,
        user_id: str
    ) -> bool:
        """检查用户是否有文档编辑权限"""
        token = await self.get_access_token()

        response = await self.client.get(
            f"{self.base_url}/docx/v1/documents/{doc_token}/permission",
            headers={"Authorization": f"Bearer {token}"},
            params={"user_id": user_id}
        )

        result = response.json()
        if result.get("code") != 0:
            return False

        # 检查是否有编辑权限
        permissions = result.get("data", {}).get("permissions", [])
        return any(p.get("type") == "edit" for p in permissions)

    def _markdown_to_blocks(self, markdown: str) -> List[Dict]:
        """将 Markdown 转换为飞书文档块（简化版）"""
        # 实际实现需要完整的 Markdown 解析器
        lines = markdown.split('\n')
        blocks = []

        for line in lines:
            if line.startswith('# '):
                blocks.append({
                    "type": "heading1",
                    "heading1": {"elements": [{"text": {"content": line[2:]}}]}
                })
            elif line.startswith('## '):
                blocks.append({
                    "type": "heading2",
                    "heading2": {"elements": [{"text": {"content": line[3:]}}]}
                })
            elif line.strip():
                blocks.append({
                    "type": "text",
                    "text": {"elements": [{"text": {"content": line}}]}
                })

        return blocks

    async def handle_webhook(self, payload: Dict) -> Dict:
        """处理飞书 Webhook"""
        event_type = payload.get("type")
        event_data = payload.get("event", {})

        if event_type == "approval_instance":
            return await self._handle_approval(event_data)
        elif event_type == "message":
            return await self._handle_message(event_data)

        return {"status": "ignored"}

    async def _handle_approval(self, event_data: Dict) -> Dict:
        """处理审批事件"""
        # 审批完成后触发需求流转
        approval_code = event_data.get("approval_code")
        instance_id = event_data.get("instance")

        # 审批通过后，将需求移动到下一泳道
        return {"status": "processed", "action": "transition_requirement"}

    async def _handle_message(self, event_data: Dict) -> Dict:
        """处理消息事件"""
        message_content = event_data.get("message", {}).get("content")
        chat_id = event_data.get("sender", {}).get("sender_id", {}).get("open_id")

        # 解析消息内容，如果是需求格式，创建新需求
        # ...
```

## 10. 错误处理

```python
# app/exceptions.py
from typing import Any, Dict, Optional

class StratosError(Exception):
    """基础异常类"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)

class NotFoundError(StratosError):
    """资源未找到"""
    pass

class ValidationError(StratosError):
    """验证错误"""
    pass

class TransitionError(StratosError):
    """无效状态转换"""
    pass

class AuthorizationError(StratosError):
    """授权失败"""
    pass

class AIServiceError(StratosError):
    """AI 服务错误"""
    pass

class DeepAgentError(StratosError):
    """DeepAgent 集成错误"""
    pass

class DuplicateError(StratosError):
    """重复资源（角色、Agent 等）"""
    pass

class GitHubIntegrationError(StratosError):
    """GitHub 集成错误"""
    pass
```

## 11. requirements.txt

```txt
# Backend Requirements
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
asyncpg==0.29.0
pydantic==2.5.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
python-multipart==0.0.6
redis[hiredis]==5.0.1
anthropic==0.7.7
openai==1.3.7
github==1.59.1
httpx==0.25.2
prometheus-client==0.19.0
sentry-sdk[fastapi]==1.39.0
alembic==1.12.1
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2

# 飞书 SDK
lark-api-sdk==1.20.1

# Optional: DeepAgent SDK (if using)
# deepagents-core==1.0.0
```

## 12. Docker 配置

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建非 root 用户
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 暴露端口
EXPOSE 8000

# 运行应用
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 13. 环境变量

```bash
# .env.example
# Application
APP_NAME=Stratos API
API_PREFIX=/api/v1
DEBUG=False

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/stratos
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10

# Redis
REDIS_URL=redis://localhost:6379

# JWT
JWT_SECRET_KEY=your-secret-key-here
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440

# AI Services
CLAUDE_API_KEY=your-claude-api-key
CLAUDE_MODEL=claude-3-5-sonnet-20240620
OPENAI_API_KEY=your-openai-api-key
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# DeepAgent
DEEPAGENT_API_URL=http://localhost:8001
DEEPAGENT_API_KEY=your-deepagent-api-key

# GitHub
GITHUB_APP_ID=your-github-app-id
GITHUB_PRIVATE_KEY=your-github-private-key
GITHUB_WEBHOOK_SECRET=your-webhook-secret

# 飞书
LARK_APP_ID=your-lark-app-id
LARK_APP_SECRET=your-lark-app-secret
LARK_ENCRYPT_KEY=
LARK_VERIFICATION_TOKEN=
```

## 14. Pydantic Schemas

```python
# app/schemas/agent.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class AgentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    nickname: str = Field(..., min_length=1, max_length=255)
    role: str = Field(..., pattern=r"^[a-z_]+_agent$")
    type: str = Field(default="ai", regex="^(human|ai)$")
    skills: List[str] = Field(default_factory=list)
    memory_enabled: bool = Field(default=True)

class AgentResponse(BaseModel):
    id: str
    project_id: str
    name: str
    nickname: str
    role: str
    type: str
    skills: List[str]
    memory_enabled: bool
    memory_document_id: Optional[str]
    current_thread_id: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
```
```

## 15. 主要功能总结

| 功能 | 技术实现 | 状态 |
|------|---------|------|
| **团队管理** | CRUD + 角色验证 | ✅ |
| **AI Agent** | DeepAgent 集成 | ✅ |
| **需求管理** | 状态机 + AI 集成 | ✅ |
| **泳道流转** | Agent 触发 + HITL | ✅ |
| **飞书集成** | Webhook + 文档同步 | ✅ |
| **长期记忆** | StoreBackend | ✅ |
| **技能系统** | SKILL.md | ✅ |

## 16. Deep Agents 最佳实践遵循

1. **Checkpointer 使用** - 所有 Agent 执行都支持中断恢复
2. **Thread ID 持久化** - 确保会话跨请求保持
3. **CompositeBackend** - 混合临时和持久存储
4. **Skills 目录** - 使用 SKILL.md 格式定义 Agent 技能
5. **Virtual Mode** - FilesystemBackend 使用虚拟模式提高安全性
```

## 17. 安全配置

```python
# DeepAgent 安全配置
DEEPAGENT_CONFIG = {
    "backend": {
        "type": "composite",
        "default": "state",
        "routes": {
            "/temp/": "state",
            "/persistent/": "store"
        }
    },
    "checkpointer": {
        "enabled": True,
        "storage_backend": "store"
    }
}

# 飞书权限验证
LARK_PERMISSION_CHECK = {
    "require_edit_for_write": True,
    "cache_duration": 300  # 5 分钟
}
```
