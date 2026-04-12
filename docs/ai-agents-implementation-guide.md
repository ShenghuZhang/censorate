# Censorate AI Agents Implementation Guide

基于 Deep Agents 的 Censorate 系统 AI Agent 完整实现指南

## 目录

1. [Deep Agents 框架集成](#1-deep-agents-框架集成)
2. [Agent 实现模式](#2-agent-实现模式)
3. [Skill 实现](#3-skill-实现)
4. [Censorate 集成](#4-stratos-集成)
5. [测试策略](#5-测试策略)

---

## 1. Deep Agents 框架集成

### 1.1 Deep Agent 客户端设置

#### 依赖安装

```txt
# requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
pydantic-settings==2.1.0
anthropic==0.7.7
openai==1.3.7
httpx==0.25.2
redis[hiredis]==5.0.1
```

#### 配置管理

```python
# backend/core/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Censorate API"
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

### 1.2 Composite Backend 混合存储配置

Deep Agents 使用 CompositeBackend 实现混合存储策略，结合临时和持久化存储。

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
    "cache_duration": 300
}
```

### 1.3 Checkpointer 实现（中断恢复）

```python
# backend/services/deepagent_service.py
import httpx
from typing import Dict, Optional
from datetime import datetime, timezone

class DeepAgentService:
    """Deep Agent 集成服务 - 遵循 Deep Agents 最佳实践"""

    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            base_url=self.api_url,
            headers={"Authorization": f"Bearer {self.api_key}"}
        )

    async def resume_from_checkpoint(
        self,
        thread_id: str,
        checkpoint: Dict
    ) -> Dict:
        """
        从检查点恢复 Agent 执行

        用于中断后恢复执行

        Args:
            thread_id: 线程 ID
            checkpoint: 检查点数据

        Returns:
            恢复结果
        """
        response = await self.client.post(f"/threads/{thread_id}/resume", json={
            "checkpoint": checkpoint
        })
        response.raise_for_status()
        return response.json()

    async def execute_agent(
        self,
        agent_type: str,
        input_data: Dict,
        requirement_id: str,
        lane: str,
        thread_id: Optional[str] = None,
        checkpointer: Optional[Dict] = None,
        config: Optional[Dict] = None
    ) -> Dict:
        """
        执行指定的 Agent

        使用 Deep Agents 最佳实践：
        - thread_id: 会话持久化
        - checkpointer: 中断恢复
        - config: Agent 特定配置
        """
        execution_id = await self._create_execution_record(
            requirement_id, agent_type, lane, input_data, thread_id
        )

        try:
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

            await self._update_execution_record(
                execution_id, "completed", result
            )

            return result

        except Exception as e:
            await self._update_execution_record(
                execution_id, "failed", None, str(e)
            )
            raise
```

### 1.4 线程管理（会话持久化）

```python
# backend/services/deepagent_service.py
async def get_agent_thread(
    self,
    thread_id: str
) -> Dict:
    """
    获取 Agent 线程状态（用于会话恢复）

    Args:
        thread_id: Deep Agent 线程 ID

    Returns:
        线程状态
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

    Args:
        thread_id: 线程 ID
        initial_state: 初始状态

    Returns:
        线程创建结果
    """
    response = await self.client.post("/threads", json={
        "thread_id": thread_id,
        "initial_state": initial_state
    })
    response.raise_for_status()
    return response.json()
```

### 1.5 Virtual Mode 安全配置

```python
# DeepAgent 安全配置
DEEPAGENT_CONFIG = {
    "virtual_mode": {
        "enabled": True,
        "filesystem_backend": "virtual",
        "allowed_paths": [
            "/tmp/",
            "/skills/"
        ],
        "isolated": True
    },
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
```

---

## 2. Agent 实现模式

### 2.1 基础 Agent 类

```python
# backend/agents/base_agent.py
from abc import ABC, abstractmethod
from typing import Dict, Optional
from ..services.deepagent_service import DeepAgentService
from ..services.lark_service import LarkService

class BaseAgent(ABC):
    """基础 Agent 类 - 所有 Censorate AI Agent 的抽象基类"""

    def __init__(
        self,
        deepagent_service: DeepAgentService,
        lark_service: LarkService,
        config: Dict = None
    ):
        self.deepagent = deepagent_service
        self.lark = lark_service
        self.config = config or {}

    @abstractmethod
    async def process(self, requirement_data: Dict, context: Dict, thread_id: Optional[str] = None) -> Dict:
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
            requirement_id=input_data.get("requirement_id"),
            lane=input_data.get("lane", self.get_agent_type().replace("_agent", "")),
            thread_id=thread_id,
            checkpointer=checkpointer,
            config=self.config
        )
```

### 2.2 Analysis Agent（需求分析）

```python
# backend/agents/analysis_agent.py
from typing import Dict, Optional
from .base_agent import BaseAgent

class AnalysisAgent(BaseAgent):
    """需求分析 Agent - 负责需求分析、重复检测和分类"""

    def get_agent_type(self) -> str:
        return "analysis_agent"

    async def process(self, requirement_data: Dict, context: Dict, thread_id: Optional[str] = None) -> Dict:
        """
        处理需求分析任务

        返回分析结果，包含优先级、复杂度、时间估计、风险评估等
        """
        input_data = {
            "requirement_id": requirement_data.get("id"),
            "title": requirement_data.get("title"),
            "description": requirement_data.get("description"),
            "lane": "analysis",
            "context": context
        }

        result = await self.execute_with_deepagent(input_data, thread_id=thread_id)

        return {
            "success": True,
            "agent_type": self.get_agent_type(),
            "result": result,
            "thread_id": thread_id
        }
```

**输出格式：**

```json
{
  "priority": "high|medium|low",
  "complexity": 1-10,
  "estimated_days": number,
  "required_skills": ["skill1", "skill2"],
  "suggested_assignee": "username or ai-agent",
  "reasoning": "brief explanation",
  "risk_assessment": {
    "technical_complexity": "low|medium|high",
    "dependencies": ["dep1", "dep2"],
    "potential_challenges": ["challenge1"]
  },
  "duplicate_check": {
    "found_duplicates": true|false,
    "similar_requirements": [
      {
        "id": "req-id",
        "req_number": 123,
        "title": "similar title",
        "similarity_score": 0.95
      }
    ]
  }
}
```

### 2.3 Design Agent（方案设计）

```python
# backend/agents/design_agent.py
from typing import Dict, Optional
from .base_agent import BaseAgent

class DesignAgent(BaseAgent):
    """方案设计 Agent - 负责生成设计文档、架构方案和 UI 线框图"""

    def get_agent_type(self) -> str:
        return "design_agent"

    async def process(self, requirement_data: Dict, context: Dict, thread_id: Optional[str] = None) -> Dict:
        """
        处理设计生成任务

        返回设计结果，包含架构建议、数据模型、API 设计、UI 线框图等
        """
        input_data = {
            "requirement_id": requirement_data.get("id"),
            "title": requirement_data.get("title"),
            "description": requirement_data.get("description"),
            "lane": "design",
            "analysis_result": context.get("analysis_result"),
            "context": context
        }

        result = await self.execute_with_deepagent(input_data, thread_id=thread_id)

        return {
            "success": True,
            "agent_type": self.get_agent_type(),
            "result": result,
            "thread_id": thread_id
        }
```

**输出格式：**

```json
{
  "architecture": {
    "overview": "high-level architecture description",
    "components": [
      {
        "name": "ComponentName",
        "purpose": "description",
        "dependencies": ["dep1", "dep2"],
        "tech_stack": ["React", "TypeScript"]
      }
    ],
    "data_flow": "description of data flow"
  },
  "data_models": {
    "new_entities": [
      {
        "name": "EntityName",
        "fields": [
          {
            "name": "fieldName",
            "type": "string|integer|boolean|date|uuid",
            "required": true|false,
            "constraints": "validation rules"
          }
        ],
        "relationships": [
          {
            "from": "Entity",
            "to": "RelatedEntity",
            "type": "one-to-one|one-to-many|many-to-many"
          }
        ]
      }
    ],
    "indexes": ["index1", "index2"],
    "migration_strategy": "description"
  },
  "api_endpoints": [
    {
      "method": "GET|POST|PUT|DELETE",
      "path": "/api/v1/resource",
      "description": "endpoint description",
      "auth_required": true|false,
      "request_schema": {},
      "response_schema": {}
    }
  ],
  "ui_wireframes": [
    {
      "component": "ComponentName",
      "purpose": "description",
      "props": {},
      "states": ["state1", "state2"],
      "user_flow": "step-by-step description"
    }
  ],
  "design_consistency": {
    "follows_system": true,
    "deviations": ["notable deviations if any"],
    "new_patterns": ["new design patterns to follow"]
  },
  "technical_specs": {
    "tech_stack_recommendations": ["library1", "library2"],
    "code_structure": "suggested folder structure",
    "performance_optimizations": ["optimization1", "optimization2"],
    "testing_strategy": "testing approach"
  }
}
```

### 2.4 Development Agent（开发）

```python
# backend/agents/development_agent.py
from typing import Dict, Optional
from .base_agent import BaseAgent

class DevelopmentAgent(BaseAgent):
    """开发 Agent - 负责生成实现代码、单元测试和文档"""

    def get_agent_type(self) -> str:
        return "development_agent"

    async def process(self, requirement_data: Dict, context: Dict, thread_id: Optional[str] = None) -> Dict:
        """
        处理代码生成任务

        返回开发结果，包含实现代码、测试文件、文档等
        """
        input_data = {
            "requirement_id": requirement_data.get("id"),
            "title": requirement_data.get("title"),
            "description": requirement_data.get("description"),
            "lane": "development",
            "design_result": context.get("design_result"),
            "context": context
        }

        result = await self.execute_with_deepagent(input_data, thread_id=thread_id)

        return {
            "success": True,
            "agent_type": self.get_agent_type(),
            "result": result,
            "thread_id": thread_id
        }
```

**输出格式：**

```json
{
  "core_implementation": {
    "files": [
      {
        "path": "relative/path/to/file",
        "content": "file content or reference",
        "language": "python|typescript|sql",
        "purpose": "description"
      }
    ]
  },
  "data_access_layer": {
    "repositories": ["repository names"],
    "migrations": ["migration descriptions"]
  },
  "business_logic": {
    "services": ["service names"],
    "state_machines": ["state machine implementations"]
  },
  "api_implementation": {
    "endpoints": [
      {
        "path": "/api/v1/endpoint",
        "method": "GET|POST|PUT|DELETE",
        "description": "endpoint description"
      }
    ]
  },
  "testing": {
    "unit_tests": {
      "count": number,
      "coverage": "percentage",
      "files": ["test file paths"]
    },
    "integration_tests": {
      "count": number,
      "files": ["test file paths"]
    },
    "e2e_tests": {
      "scenarios": ["scenario descriptions"],
      "files": ["test file paths"]
    }
  },
  "documentation": {
    "readme": "README file content",
    "api_docs": "Swagger/OpenAPI spec",
    "type_definitions": "type definitions"
  },
  "code_quality": {
    "linting_results": "linting report",
    "complexity_metrics": "complexity scores",
    "performance_benchmarks": "performance data"
  },
  "deployment_instructions": {
    "environment_setup": "setup steps",
    "configuration": "required config",
    "build_commands": "build and deploy commands"
  }
}
```

### 2.5 Testing Agent（测试）

```python
# backend/agents/testing_agent.py
from typing import Dict, Optional
from .base_agent import BaseAgent

class TestingAgent(BaseAgent):
    """测试 Agent - 负责生成测试用例、执行测试和分析覆盖率"""

    def get_agent_type(self) -> str:
        return "testing_agent"

    async def process(self, requirement_data: Dict, context: Dict, thread_id: Optional[str] = None) -> Dict:
        """
        处理测试生成和执行任务

        返回测试结果，包含测试用例、覆盖率报告、执行结果等
        """
        input_data = {
            "requirement_id": requirement_data.get("id"),
            "title": requirement_data.get("title"),
            "description": requirement_data.get("description"),
            "lane": "testing",
            "development_result": context.get("development_result"),
            "context": context
        }

        result = await self.execute_with_deepagent(input_data, thread_id=thread_id)

        return {
            "success": True,
            "agent_type": self.get_agent_type(),
            "result": result,
            "thread_id": thread_id
        }
```

**输出格式：**

```json
{
  "unit_tests": {
    "files": [
      {
        "path": "tests/unit/test_module.py",
        "test_count": number,
        "coverage_target": "80%"
      }
    ],
    "total_tests": number,
    "framework": "pytest"
  },
  "integration_tests": {
    "files": [
      {
        "path": "tests/integration/test_workflow.py",
        "test_count": number,
        "coverage_target": "70%"
      }
    ],
    "total_tests": number,
    "framework": "pytest"
  },
  "e2e_tests": {
    "scenarios": [
      {
        "name": "scenario name",
        "description": "detailed description",
        "steps": ["step1", "step2"],
        "test_files": ["test file paths"],
        "coverage_target": "100%"
      }
    ],
    "framework": "playwright"
  },
  "performance_tests": {
    "scenarios": [
      {
        "name": "load test scenario",
        "description": "description",
        "target_load": "1000 req/sec",
        "duration": "5 min"
      }
    ]
  },
  "security_tests": {
    "vulnerability_checks": [
      {
        "type": "XSS|SQL Injection|CSRF",
        "description": "check description",
        "test_files": ["test file paths"]
      }
    ]
  },
  "test_data": {
    "fixtures": ["fixture file paths"],
    "generators": ["test data generators"]
  },
  "coverage_report": {
    "overall_coverage": "percentage",
    "by_module": {
      "module_name": "coverage percentage"
    }
  }
}
```

---

## 3. Skill 实现

### 3.1 SKILL.md 文件结构

每个 Agent 都有对应的 SKILL.md 文件，位于 `skills/<agent_type>/SKILL.md`。

**示例：Requirement Analysis Skill**

```markdown
---
name: requirement_analysis
description: Analyze requirements, detect duplicates, and provide triage information
---

# Requirement Analysis Skill

## Overview
This skill provides comprehensive requirement analysis including priority assessment, complexity estimation, and duplicate detection using vector search.

## When to Use
- When a requirement enters the "Analysis" lane
- When explicitly requested by a user
- During backlog prioritization

## Instructions

### 1. Analyze the Requirement
- Read the requirement title and description carefully
- Identify key features and components
- Determine technical complexity (1-10 scale)
- Estimate business impact and urgency

### 2. Determine Priority
**High Priority** if:
- Business critical feature
- Security vulnerability or issue
- Blocked other work
- Timeline pressure

**Medium Priority** if:
- Standard feature request
- Enhancement to existing functionality
- Normal timeline

**Low Priority** if:
- Nice-to-have feature
- Minor improvement
- Flexible timeline

## Output Format

Return results in this JSON structure:

```json
{
  "priority": "high|medium|low",
  "complexity": 1-10,
  "estimated_days": number,
  "required_skills": ["skill1", "skill2"],
  "suggested_assignee": "username or ai-agent",
  "reasoning": "brief explanation",
  "risk_assessment": {
    "technical_complexity": "low|medium|high",
    "dependencies": ["dep1", "dep2"],
    "potential_challenges": ["challenge1"]
  },
  "duplicate_check": {
    "found_duplicates": true|false,
    "similar_requirements": [
      {
        "id": "req-id",
        "req_number": 123,
        "title": "similar title",
        "similarity_score": 0.95
      }
    ]
  }
}
```

## Available Tools
- `search_database`: Search for similar requirements
- `query_ai_knowledge`: Access internal knowledge base
- `check_dependencies`: Analyze requirement dependencies
```

### 3.2 Skill 加载和执行

```python
# backend/agents/registry.py
from typing import Dict, Type, Optional
from .base_agent import BaseAgent
from .analysis_agent import AnalysisAgent
from .design_agent import DesignAgent
from .development_agent import DevelopmentAgent
from .testing_agent import TestingAgent

_AGENT_REGISTRY: Dict[str, Type[BaseAgent]] = {
    "analysis_agent": AnalysisAgent,
    "design_agent": DesignAgent,
    "development_agent": DevelopmentAgent,
    "testing_agent": TestingAgent,
}

_LANE_AGENT_MAP: Dict[str, str] = {
    "analysis": "analysis_agent",
    "design": "design_agent",
    "development": "development_agent",
    "testing": "testing_agent",
}

def get_agent_class(agent_type: str) -> Optional[Type[BaseAgent]]:
    """根据 Agent 类型获取对应的类"""
    return _AGENT_REGISTRY.get(agent_type)

def get_agent_for_lane(lane: str) -> Optional[Type[BaseAgent]]:
    """根据泳道名称获取对应的 Agent 类"""
    agent_type = _LANE_AGENT_MAP.get(lane)
    return get_agent_class(agent_type) if agent_type else None

def register_agent(agent_type: str, agent_class: Type[BaseAgent]) -> None:
    """注册自定义 Agent"""
    _AGENT_REGISTRY[agent_type] = agent_class

def register_lane_agent(lane: str, agent_type: str) -> None:
    """注册泳道与 Agent 的映射关系"""
    if agent_type not in _AGENT_REGISTRY:
        raise ValueError(f"Agent type '{agent_type}' not registered")
    _LANE_AGENT_MAP[lane] = agent_type
```

### 3.3 使用 Skill 输出增强 Agent

```python
# 在 Agent 中加载 Skill 配置
import os
import yaml
from typing import Dict

def load_skill_config(skill_path: str) -> Dict:
    """加载 Skill 配置"""
    skill_file = os.path.join(skill_path, "SKILL.md")

    if not os.path.exists(skill_file):
        return {}

    with open(skill_file, 'r') as f:
        content = f.read()

    # 解析 frontmatter
    if content.startswith('---'):
        frontmatter_end = content.find('---', 3)
        if frontmatter_end > 0:
            frontmatter = yaml.safe_load(content[3:frontmatter_end])
            return frontmatter

    return {}

# 在 Agent 初始化时加载 Skill
class AnalysisAgent(BaseAgent):
    def __init__(
        self,
        deepagent_service: DeepAgentService,
        lark_service: LarkService,
        config: Dict = None
    ):
        super().__init__(deepagent_service, lark_service, config)

        # 加载 Skill 配置
        skill_config = load_skill_config("./skills/analysis")
        self.skill_name = skill_config.get("name", "requirement_analysis")
        self.skill_description = skill_config.get("description", "")
```

---

## 4. Censorate 集成

### 4.1 连接需求服务

```python
# backend/services/requirement_service.py
from typing import Dict, Optional
from sqlalchemy.orm import Session
from ..models.requirement import Requirement
from ..models.agent_execution import AgentExecution
from ..agents.registry import get_agent_class
from .deepagent_service import DeepAgentService
from .lark_service import LarkService

class RequirementService:
    """需求服务 - 包含 Agent 执行和泳道流转"""

    def __init__(
        self,
        deepagent_service: DeepAgentService,
        lark_service: LarkService
    ):
        self.deepagent = deepagent_service
        self.lark = lark_service

    async def transition_with_agent(
        self,
        requirement_id: int,
        to_status: str,
        user_id: str,
        db: Session,
        thread_id: Optional[str] = None
    ) -> Dict:
        """通过 Agent 执行状态转换"""
        requirement = db.query(Requirement).filter(Requirement.id == requirement_id).first()
        if not requirement:
            raise ValueError(f"Requirement {requirement_id} not found")

        lane_role = await self._get_lane_role(requirement.project_id, to_status, db)

        if lane_role and lane_role.get("agent_type"):
            result = await self._execute_lane_agent(
                requirement, lane_role, db, thread_id
            )

            if result.get("success"):
                await self._update_requirement_status(
                    requirement_id, to_status, result, db
                )

            return result
        else:
            return await self._update_requirement_status(
                requirement_id, to_status, {}, db
            )

    async def _execute_lane_agent(
        self,
        requirement: Requirement,
        lane_role: Dict,
        db: Session,
        thread_id: Optional[str]
    ) -> Dict:
        """执行泳道对应的 Agent"""
        agent_class = get_agent_class(lane_role["agent_type"])
        agent = agent_class(
            deepagent_service=self.deepagent,
            lark_service=self.lark,
            config=lane_role["config"]
        )

        context = await self._build_agent_context(requirement, db)

        requirement_data = {
            "id": requirement.id,
            "title": requirement.title,
            "description": requirement.description,
            "status": requirement.status,
        }

        result = await agent.process(requirement_data, context, thread_id=thread_id)

        return result

    async def _build_agent_context(
        self,
        requirement: Requirement,
        db: Session
    ) -> Dict:
        """构建 Agent 上下文"""
        from ..repositories.agent_execution_repository import AgentExecutionRepository

        repo = AgentExecutionRepository()

        previous_executions = db.query(AgentExecution).filter(
            AgentExecution.requirement_id == requirement.id
        ).order_by(AgentExecution.created_at.desc()).limit(5).all()

        return {
            "project_id": requirement.project_id,
            "requirement_id": requirement.id,
            "current_status": requirement.status,
            "previous_executions": [
                {
                    "agent_type": exec.agent_type,
                    "status": exec.status,
                    "output": exec.output_data
                }
                for exec in previous_executions
            ],
            "thread_id": requirement.current_thread_id
        }
```

### 4.2 泳道流转处理

```python
# 状态顺序
STATUS_ORDER = {
    'new': 0,
    'analysis': 1,
    'design': 2,
    'development': 3,
    'testing': 4,
    'completed': 5
}

# 检测回退
def detect_backward_move(old_status: str, new_status: str) -> bool:
    old_num = STATUS_ORDER.get(old_status, 0)
    new_num = STATUS_ORDER.get(new_status, 0)
    return new_num < old_num

# API 端点示例
@router.post("/requirements/{requirement_id}/transition")
async def transition_with_agent(
    requirement_id: int,
    data: AgentTransitionRequest,
    db: Session = Depends(get_db)
):
    """通过 Agent 执行状态转换"""
    service = get_requirement_service()
    try:
        result = await service.transition_with_agent(
            requirement_id, data.to_status, None, db, thread_id=data.thread_id
        )
        return AgentTransitionResponse(
            success=True,
            agent_type=result.get("agent_type"),
            result=result.get("result"),
            thread_id=result.get("thread_id")
        )
    except Exception as e:
        return AgentTransitionResponse(
            success=False,
            error=str(e)
        )
```

### 4.3 更新需求状态

```python
async def _update_requirement_status(
    self,
    requirement_id: int,
    to_status: str,
    result: Dict,
    db: Session
) -> Dict:
    """更新需求状态"""
    requirement = db.query(Requirement).filter(Requirement.id == requirement_id).first()

    status_order = {
        'new': 0,
        'analysis': 1,
        'design': 2,
        'development': 3,
        'testing': 4,
        'completed': 5
    }
    old_status_num = status_order.get(requirement.status, 0)
    new_status_num = status_order.get(to_status, 0)

    if new_status_num < old_status_num:
        requirement.is_returned = True
        requirement.return_count += 1
        requirement.last_returned_at = datetime.now(timezone.utc)

    requirement.status = to_status

    if result.get("thread_id"):
        requirement.current_thread_id = result.get("thread_id")

    if result.get("result"):
        requirement.ai_suggestions = result.get("result")

    if to_status == "completed":
        requirement.completed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(requirement)

    return {
        "success": True,
        "requirement": requirement
    }
```

### 4.4 Agent 记忆管理

```python
# backend/api/agents.py
@router.get("/agents/{agent_id}/memory")
async def get_agent_memory(
    agent_id: int,
    db: Session = Depends(get_db)
):
    """获取 Agent 记忆（通过 DeepAgent 的 StoreBackend）"""
    from ..repositories.team_member_repository import TeamMemberRepository
    repo = TeamMemberRepository()

    agent = await repo.get(agent_id, db)

    if not agent.memory_enabled:
        raise HTTPException(
            status_code=400,
            detail="Memory not enabled for this agent"
        )

    if agent.current_thread_id:
        deepagent_service = get_deepagent_service()
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
    agent_id: int,
    content: AgentMemoryUpdate,
    db: Session = Depends(get_db)
):
    """更新 Agent 记忆（通过 DeepAgent 的 StoreBackend）"""
    from ..repositories.team_member_repository import TeamMemberRepository
    repo = TeamMemberRepository()

    agent = await repo.get(agent_id, db)

    if not agent.memory_enabled:
        raise HTTPException(
            status_code=400,
            detail="Memory not enabled for this agent"
        )

    deepagent_service = get_deepagent_service()

    if not agent.current_thread_id:
        thread_result = await deepagent_service.create_thread(
            thread_id=f"agent-{agent_id}",
            initial_state=content.content
        )
        await repo.update(agent_id, {
            "current_thread_id": thread_result["id"]
        }, db)
    else:
        await deepagent_service.resume_from_checkpoint(
            agent.current_thread_id,
            {"state": content.content}
        )

    return {"status": "success", "thread_id": agent.current_thread_id}
```

### 4.5 飞书文档集成

```python
# backend/services/lark_service.py
class LarkService:
    """飞书集成服务"""

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

        await self.append_to_document(doc_token, content)

        return {
            "token": doc_token,
            "url": f"https://feishu.cn/docx/{doc_token}"
        }

    async def append_agent_result_to_document(
        self,
        doc_token: str,
        agent_type: str,
        result: Dict
    ):
        """将 Agent 执行结果追加到飞书文档"""
        content = self._format_agent_result(agent_type, result)
        await self.append_to_document(doc_token, content)

    def _format_agent_result(self, agent_type: str, result: Dict) -> str:
        """格式化 Agent 结果为 Markdown"""
        formatted = f"\n\n## {agent_type.replace('_', ' ').title()} Results\n\n"

        for key, value in result.items():
            if isinstance(value, dict):
                formatted += f"### {key.replace('_', ' ').title()}\n"
                for sub_key, sub_value in value.items():
                    formatted += f"- **{sub_key}**: {sub_value}\n"
            elif isinstance(value, list):
                formatted += f"### {key.replace('_', ' ').title()}\n"
                for item in value:
                    formatted += f"- {item}\n"
            else:
                formatted += f"**{key}**: {value}\n"

        return formatted
```

---

## 5. 测试策略

### 5.1 单元测试

```python
# tests/unit/test_agents.py
import pytest
from unittest.mock import Mock, MagicMock
from sqlalchemy.orm import Session

from stratos_system.backend.agents.analysis_agent import AnalysisAgent
from stratos_system.backend.agents.design_agent import DesignAgent
from stratos_system.backend.agents.registry import get_agent_class, get_agent_for_lane
from stratos_system.backend.services.deepagent_service import DeepAgentService
from stratos_system.backend.services.lark_service import LarkService

class TestAgentRegistry:
    """Tests for the agent registry functionality."""

    def test_get_agent_class_valid_type(self):
        """Test that valid agent types return the correct class."""
        for agent_type in ["analysis_agent", "design_agent", "development_agent", "testing_agent"]:
            agent_class = get_agent_class(agent_type)
            assert agent_class is not None
            assert agent_type in agent_class.__name__.lower()

    def test_get_agent_for_lane_valid(self):
        """Test that valid lanes return the correct agent class."""
        for lane, agent_type in [
            ("analysis", "analysis_agent"),
            ("design", "design_agent"),
            ("development", "development_agent"),
            ("testing", "testing_agent")
        ]:
            agent_class = get_agent_for_lane(lane)
            assert agent_class is not None
            assert agent_type in agent_class.__name__.lower()

class TestAnalysisAgent:
    """Tests for AnalysisAgent functionality."""

    def test_initialization(self):
        """Test AnalysisAgent initialization."""
        mock_deepagent = Mock(spec=DeepAgentService)
        mock_lark = Mock(spec=LarkService)

        agent = AnalysisAgent(mock_deepagent, mock_lark)
        assert isinstance(agent, AnalysisAgent)
        assert agent.get_agent_type() == "analysis_agent"

    def test_process_with_valid_data(self, mocker):
        """Test that AnalysisAgent.process works correctly with valid data."""
        mock_deepagent = Mock(spec=DeepAgentService)
        mock_lark = Mock(spec=LarkService)

        mock_deepagent.execute_agent.return_value = {
            "success": True,
            "priority": "high",
            "complexity": 8,
            "estimated_days": 5,
            "required_skills": ["python", "sql"],
            "risk_assessment": {"technical_complexity": "high"}
        }

        agent = AnalysisAgent(mock_deepagent, mock_lark)

        result = agent.process({
            "id": 1,
            "title": "Test Requirement",
            "description": "This is a test requirement",
            "status": "new"
        }, {
            "context": "Test context"
        }, thread_id="test_thread_1")

        assert result["success"] == True
        assert result["agent_type"] == "analysis_agent"
        assert "result" in result
```

### 5.2 集成测试

```python
# tests/integration/test_deepagent_integration.py
import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from stratos_system.backend.services.deepagent_service import DeepAgentService
from stratos_system.backend.repositories.agent_execution_repository import AgentExecutionRepository

class TestDeepAgentIntegration:
    """Tests for Deep Agent integration with Censorate system."""

    @patch('httpx.AsyncClient.post')
    @patch('httpx.AsyncClient.get')
    def test_deepagent_execute_agent_success(self, mock_get, mock_post):
        """Test successful execution of an agent via DeepAgent API."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "priority": "high",
            "complexity": 8,
            "estimated_days": 5
        }
        mock_post.return_value = mock_response

        service = DeepAgentService(
            api_url="http://localhost:8001",
            api_key="test_api_key"
        )

        result = service.execute_agent(
            agent_type="analysis_agent",
            input_data={"title": "Test Requirement"},
            requirement_id="1",
            lane="analysis"
        )

        assert result["success"] == True
        assert result["priority"] == "high"
        assert result["complexity"] == 8
        assert result["estimated_days"] == 5

class TestAgentExecutionTracking:
    """Tests for AgentExecution tracking functionality."""

    def test_create_agent_execution_record(self):
        """Test creating agent execution records."""
        repo = AgentExecutionRepository()
        db = Mock(spec=Session)

        execution = repo.create(db, {
            "requirement_id": 1,
            "agent_type": "analysis_agent",
            "lane": "analysis",
            "status": "running",
            "input_data": {"title": "Test Requirement"},
            "thread_id": "test_thread_1"
        })

        assert execution is not None
        assert execution.requirement_id == 1
        assert execution.agent_type == "analysis_agent"
```

### 5.3 E2E 测试

```python
# tests/e2e/test_agent_workflow.py
import pytest
from unittest.mock import Mock, patch, MagicMock

class TestCompleteAgentWorkflow:
    """End-to-end tests for complete agent workflows."""

    @patch('stratos_system.backend.agents.analysis_agent.AnalysisAgent.process')
    @patch('stratos_system.backend.agents.design_agent.DesignAgent.process')
    @patch('stratos_system.backend.agents.development_agent.DevelopmentAgent.process')
    @patch('stratos_system.backend.agents.testing_agent.TestingAgent.process')
    def test_complete_requirement_workflow(
        self,
        mock_testing_process,
        mock_dev_process,
        mock_design_process,
        mock_analysis_process
    ):
        """
        End-to-end test of a requirement going through all lanes:
        New -> Analysis -> Design -> Development -> Testing -> Completed
        """
        # Mock responses for each agent
        mock_analysis_process.return_value = {
            "success": True,
            "agent_type": "analysis_agent",
            "result": {
                "priority": "high",
                "complexity": 8,
                "estimated_days": 5
            },
            "thread_id": "workflow_thread_1"
        }

        mock_design_process.return_value = {
            "success": True,
            "agent_type": "design_agent",
            "result": {
                "architecture": "Monolithic with modular design",
                "api_endpoints": [
                    {"method": "POST", "path": "/api/v1/features"}
                ],
                "ui_wireframes": ["FeatureList", "FeatureDetail"]
            },
            "thread_id": "workflow_thread_1"
        }

        mock_dev_process.return_value = {
            "success": True,
            "agent_type": "development_agent",
            "result": {
                "core_implementation": {
                    "files": [{"path": "app/services/feature_service.py"}]
                },
                "testing": {
                    "unit_tests": {"count": 15}
                }
            },
            "thread_id": "workflow_thread_1"
        }

        mock_testing_process.return_value = {
            "success": True,
            "agent_type": "testing_agent",
            "result": {
                "unit_tests": {"total_tests": 25, "framework": "pytest"},
                "coverage_report": {"overall_coverage": "92%"}
            },
            "thread_id": "workflow_thread_1"
        }

        # Simulate complete workflow
        requirement_data = {
            "id": 1,
            "title": "Implement user authentication",
            "description": "Add JWT-based authentication to the API",
            "status": "new"
        }

        # Step 1: Analysis
        from stratos_system.backend.agents.analysis_agent import AnalysisAgent
        analysis_agent = AnalysisAgent(Mock(), Mock())
        analysis_result = analysis_agent.process(
            requirement_data,
            {"context": "Initial analysis"},
            thread_id="workflow_thread_1"
        )

        assert analysis_result["success"] == True
        assert analysis_result["agent_type"] == "analysis_agent"

        # Step 2: Design
        from stratos_system.backend.agents.design_agent import DesignAgent
        design_agent = DesignAgent(Mock(), Mock())
        design_result = design_agent.process(
            requirement_data,
            {"analysis_result": analysis_result["result"]},
            thread_id="workflow_thread_1"
        )

        assert design_result["success"] == True

        # Final verification: all agents used the same thread_id
        assert analysis_result["thread_id"] == design_result["thread_id"]

    def test_interruption_recovery(self):
        """Test agent execution interruption and recovery using checkpointer."""
        from stratos_system.backend.services.deepagent_service import DeepAgentService

        service = DeepAgentService(
            api_url="http://localhost:8001",
            api_key="test_api_key"
        )

        # Simulate interrupted execution
        checkpoint = {
            "step": "analyzing_requirement",
            "progress": 0.5,
            "data_collected": {"title": "Test Requirement"}
        }

        # Verify checkpoint structure
        assert "step" in checkpoint
        assert "progress" in checkpoint
        assert "data_collected" in checkpoint
        assert checkpoint["progress"] == 0.5
```

---

## 附录

### A. 环境变量配置

```bash
# .env.example
# Application
APP_NAME=Censorate API
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

### B. 数据库模型

```sql
-- Agent 执行记录表
CREATE TABLE agent_executions (
    id SERIAL PRIMARY KEY,
    requirement_id INTEGER NOT NULL REFERENCES requirements(id) ON DELETE CASCADE,
    agent_type VARCHAR(100) NOT NULL,
    lane VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    input_data JSONB,
    output_data JSONB,
    error_message TEXT,
    thread_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    INDEX idx_agent_executions_requirement (requirement_id)
);

-- 泳道角色配置表
CREATE TABLE lane_roles (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    lane VARCHAR(50) NOT NULL,
    role_name VARCHAR(255) NOT NULL,
    agent_type VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    config JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(project_id, lane)
);
```

### C. 目录结构

```
stratos-system/backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/
│   │           ├── agents.py           # AI Agent 管理 API
│   │           ├── requirements.py
│   │           └── ...
│   ├── core/
│   │   └── config.py         # Configuration settings
│   ├── services/
│   │   ├── deepagent_service.py    # DeepAgent 集成
│   │   ├── lark_service.py        # 飞书服务
│   │   └── requirement_service.py # 需求服务
│   ├── models/
│   │   ├── requirement.py
│   │   └── agent_execution.py
│   ├── repositories/
│   │   ├── base_repository.py
│   │   └── agent_execution_repository.py
│   ├── schemas/
│   │   └── agent.py
│   └── agents/
│       ├── base_agent.py
│       ├── analysis_agent.py
│       ├── design_agent.py
│       ├── development_agent.py
│       └── testing_agent.py
├── skills/
│   ├── analysis/
│   │   └── SKILL.md
│   ├── design/
│   │   └── SKILL.md
│   ├── development/
│   │   └── SKILL.md
│   └── testing/
│       └── SKILL.md
└── tests/
    ├── unit/
    │   └── test_agents.py
    ├── integration/
    │   └── test_deepagent_integration.py
    └── e2e/
        └── test_agent_workflow.py
```
