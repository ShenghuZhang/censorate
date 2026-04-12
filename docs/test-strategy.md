# Stratos Management System - Test Strategy and QA Plan

## 1. 测试覆盖目标

| 测试类型 | 目标覆盖率 | 优先级 |
|----------|------------|----------|
| 单元测试 | ≥ 80% | P0 (最高) |
| 集成测试 | ≥ 70% | P1 |
| E2E 测试 | 关键流程 100% | P0 |
| API 测试 | 所有端点 100% | P0 |
| 性能测试 | 关键接口 | P1 |

## 2. 测试环境

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Staging Environment                         │
├─────────────────────────────────────────────────────────────────────────┤
│  - 最新代码部署                                                     │
│  - 完整数据库（测试数据）                                            │
│  - Redis 缓存                                                       │
│  - DeepAgent 服务                                                     │
│  - 飞书集成（测试应用）                                              │
│  - GitHub 集成                                                      │
└─────────────────────────────────────────────────────────────────────────┘
```

## 3. 单元测试策略

### 后端单元测试

```python
# tests/unit/services/test_requirement_service.py
import pytest
from unittest.mock import Mock, AsyncMock
from app.services.requirement_service import RequirementService

class TestRequirementService:
    @pytest.mark.asyncio
    async def test_create_requirement(self):
        """测试创建需求"""
        mock_repo = AsyncMock()
        mock_lark_service = Mock()

        service = RequirementService(mock_repo, mock_lark_service)

        mock_repo.get_next_number.return_value = 1

        result = await service.create_requirement(
            project_id="proj-1",
            data={
                "title": "Test Requirement",
                "description": "Test description",
                "priority": "high"
            },
            user_id="user-1",
            db=AsyncMock()
        )

        assert result is not None
        assert result.title == "Test Requirement"
        assert result.req_number == 1

    @pytest.mark.asyncio
    async def test_validate_transition_valid(self):
        """测试有效状态转换"""
        service = RequirementService(...)

        result = await service.validate_transition(
            requirement_id="req-1",
            from_status="new",
            to_status="analysis",
            db=AsyncMock()
        )

        assert result.valid is True
        assert result.requires_ai_approval is True

    @pytest.mark.asyncio
    async def test_validate_transition_invalid(self):
        """测试无效状态转换"""
        service = RequirementService(...)

        with pytest.raises(TransitionError):
            await service.validate_transition(
                requirement_id="req-1",
                from_status="new",
                to_status="completed",  # 跳过中间状态
                db=AsyncMock()
            )

    @pytest.mark.asyncio
    async def test_reject_requirement(self):
        """测试需求拒绝（拖回）"""
        service = RequirementService(...)

        result = await service.reject_requirement(
            requirement_id="req-1",
            new_status="analysis",
            reason="需要更多信息",
            user_id="user-1",
            db=AsyncMock()
        )

        assert result.return_count == 1
        assert result.status == "analysis"
```

### AI Service 单元测试

```python
# tests/unit/services/test_ai_service.py
class TestAIService:
    @pytest.mark.asyncio
    async def test_triage_requirement(self):
        """测试需求分析"""
        mock_claude = AsyncMock()
        service = AIService(settings, mock_claude, mock_openai)

        mock_claude.messages.create.return_value = Mock(
            content=[Mock(text='{"priority": "high", "complexity": 8}')]
        )

        result = await service.triage_requirement(
            Requirement(title="Test", description="...")
        )

        assert result.priority == "high"
        assert result.complexity == 8

    @pytest.mark.asyncio
    async def test_find_duplicates(self):
        """测试重复检测"""
        service = AIService(...)

        duplicates = await service.find_duplicates(
            requirement=Requirement(title="User Login"),
            threshold=0.85
        )

        assert isinstance(duplicates, list)
        # 验证按相似度排序
        if len(duplicates) > 1:
            assert duplicates[0].overall_score >= duplicates[1].overall_score
```

### DeepAgent Service 单元测试

```python
# tests/unit/services/test_deepagent_service.py
class TestDeepAgentService:
    @pytest.mark.asyncio
    async def test_execute_agent_success(self):
        """测试 Agent 执行成功"""
        service = DeepAgentService(settings)

        mock_response = {
            "success": True,
            "content": "Analysis complete",
            "suggestions": ["建议1", "建议2"]
        }

        with patch.object(service.client, 'post', return_value=Mock(json=AsyncMock(return_value=mock_response))):
        result = await service.execute_agent(
                agent_type="analysis_agent",
                input_data={"title": "Test"},
                requirement_id="req-1",
                lane="analysis"
            )

        assert result["success"] is True
        assert result["content"] == "Analysis complete"

    @pytest.mark.asyncio
    async def test_execute_agent_failure(self):
        """测试 Agent 执行失败"""
        service = DeepAgentService(settings)

        with patch.object(service.client, 'post', side_effect=Exception("API Error")):
            with pytest.raises(AgentExecutionError):
                await service.execute_agent(
                    agent_type="analysis_agent",
                    input_data={},
                    requirement_id="req-1",
                    lane="analysis"
                )
```

### 飞书服务单元测试

```python
# tests/unit/services/test_lark_service.py
class TestLarkService:
    @pytest.mark.asyncio
    async def test_create_document(self):
        """测试创建飞书文档"""
        service = LarkService(app_id, app_secret)

        with patch.object(service.client, 'post') as mock_post:
            mock_post.return_value = AsyncMock(json=Mock(return_value={
                "code": 0,
                "data": {"document": {"document_id": "doc-token-123"}}
            }))

            result = await service.create_document(
                title="Test Doc",
                content="# Content"
            )

            assert result["token"] == "doc-token-123"

    @pytest.mark.asyncio
    async def test_get_document_permission(self):
        """测试检查文档权限"""
        service = LarkService(app_id, app_secret)

        with patch.object(service.client, 'get') as mock_get:
            mock_get.return_value = AsyncMock(json=Mock(return_value={
                "code": 0,
                "data": {
                    "permissions": [
                        {"type": "edit"},
                        {"type": "view"}
                    ]
                }
            }))

            has_permission = await service.get_document_permission(
                doc_token="doc-123",
                user_id="user-1"
            )

            assert has_permission is True
```

### 前端单元测试

```typescript
// tests/unit/components/RequirementCard.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import RequirementCard from '@/components/kanban/RequirementCard';

describe('RequirementCard', () => {
  const mockRequirement = {
    id: 'req-1',
    reqNumber: 1,
    title: 'Test Requirement',
    priority: 'high',
    status: 'new',
    returnCount: 0
  };

  it('renders requirement title', () => {
    render(<RequirementCard requirement={mockRequirement} />);
    expect(screen.getByText('Test Requirement')).toBeInTheDocument();
  });

  it('shows RETURNED badge when return count > 0', () => {
    const reqWithReturn = { ...mockRequirement, returnCount: 2 };
    render(<RequirementCard requirement={reqWithReturn} />);

    expect(screen.getByText('RETURNED (2)')).toBeInTheDocument();
  });

  it('opens detail dialog on click', () => {
    render(<RequirementCard requirement={mockRequirement} />);
    const card = screen.getByText('Test Requirement');
    fireEvent.click(card);

    expect(screen.getByRole('dialog')).toBeInTheDocument();
  });
});
```

```typescript
// tests/unit/components/AddAgentDialog.test.tsx
describe('AddAgentDialog', () => {
  it('disables add button when role is not selected', () => {
    render(<AddAgentDialog isOpen onAdd={jest.fn()} />);
    const addButton = screen.getByText('Add AI Agent');

    expect(addButton).toBeDisabled();
  });

  it('shows role availability warning when all roles taken', () => {
    render(
      <AddAgentDialog
        isOpen
        onAdd={jest.fn()}
        existingRoles={['analysis_agent', 'design_agent', 'development_agent', 'testing_agent']}
      />
    );

    expect(screen.getByText('All agent roles are already assigned')).toBeInTheDocument();
  });
});
```

## 4. 集成测试策略

### API 集成测试

```python
# tests/integration/api/test_requirements_api.py
import pytest
from fastapi.testclient import TestClient

class TestRequirementsAPI:
    @pytest.fixture
    def client(self):
        return TestClient(app)

    @pytest.fixture
    def auth_headers(self):
        return {"Authorization": "Bearer test-token"}

    def test_create_requirement(self, client, auth_headers):
        """测试创建需求 API"""
        response = client.post(
            "/api/v1/projects/proj-1/requirements",
            json={
                "title": "Test Requirement",
                "description": "Test description",
                "priority": "high"
            },
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Requirement"
        assert "id" in data

    def test_transition_requirement_with_ai_approval(self, client, auth_headers):
        """测试需求转换（带 AI 批准）"""
        # 先创建需求
        create_resp = client.post(
            "/api/v1/projects/proj-1/requirements",
            json={"title": "Test", "priority": "medium"},
            headers=auth_headers
        )
        req_id = create_resp.json()["id"]

        # 转换到下一个状态
        transition_resp = client.post(
            f"/api/v1/requirements/{req_id}/transition",
            json={
                "to_status": "analysis",
                "ai_approved": True,
                "approved_ai_suggestions": [{"type": "triage"}]
            },
            headers=auth_headers
        )

        assert transition_resp.status_code == 200
        assert transition_resp.json()["status"] == "analysis"

    def test_transition_requirement_reject(self, client, auth_headers):
        """测试需求拒绝（拖回）"""
        create_resp = client.post(...)
        req_id = create_resp.json()["id"]

        # 移动到上一状态（拒绝）
        reject_resp = client.post(
            f"/api/v1/requirements/{req_id}/transition",
            json={
                "to_status": "new",
                "reason": "需要更多信息",
                "ai_approved": False
            },
            headers=auth_headers
        )

        assert reject_resp.status_code == 200
        data = reject_resp.json()
        assert data["return_count"] == 1
        assert data["last_returned_at"] is not None
```

### DeepAgent 集成测试

```python
# tests/integration/deepagent/test_agent_execution.py
class TestAgentExecution:
    @pytest.mark.asyncio
    async def test_full_analysis_workflow(self):
        """测试完整的分析工作流"""
        # 1. 创建需求
        req = await create_test_requirement()

        # 2. 获取分析 Agent
        agent = await get_agent_by_role("analysis_agent")

        # 3. 执行 Agent
        result = await execute_agent(
            agent_type="analysis_agent",
            input_data={
                "requirement_id": req.id,
                "title": req.title,
                "description": req.description
            }
        )

        assert result["success"] is True
        assert "analysis" in result
        assert "suggestions" in result

        # 4. 验证需求已更新
        updated_req = await get_requirement(req.id)
        assert updated_req.ai_suggestions == result

    @pytest.mark.asyncio
    async def test_agent_memory_persistence(self):
        """测试 Agent 记忆持久化"""
        agent_id = "agent-1"

        # 写入记忆
        await update_agent_memory(agent_id, {"context": "test data"})

        # 读取记忆
        memory = await get_agent_memory(agent_id)

        assert memory is not None
        assert memory["context"] == "test data"
```

### 飞书集成测试

```python
# tests/integration/lark/test_workflow.py
class TestLarkWorkflow:
    @pytest.mark.asyncio
    async def test_create_requirement_from_lark_message(self):
        """测试从飞书消息创建需求"""
        # 模拟飞收消息
        lark_message = {
            "sender": {"sender_id": {"open_id": "user-1"}},
            "message": {
                "content": "## 需求\n\n实现用户登录功能"
            }
        }

        # 创建需求
        requirement = await create_from_lark(
            project_id="proj-1",
            lark_message=lark_message,
            user_id="user-1"
        )

        assert requirement.source == "lark"
        assert requirement.lark_doc_url is not None

    @pytest.mark.asyncio
    async def test_larkai_doc_permission_check(self):
        """测试飞书文档权限检查"""
        # 用户有编辑权限
        has_permission = await check_document_permission(
            doc_token="doc-123",
            user_id="user-1"
        )

        assert has_permission is True

        # 用户无编辑权限
        no_permission = await check_document_permission(
            doc_token="doc-123",
            user_id="user-2"
        )

        assert no_permission is False
```

## 5. E2E 测试场景

### 完整需求生命周期

```python
# tests/e2e/test_requirement_lifecycle.py
from playwright.async_api import async_playwright

class TestRequirementLifecycle:
    @pytest.mark.asyncio
    async def test_new_to_completed_workflow(self, async_playwright):
        """测试从新建到完成的完整流程"""
        browser = await async_playwright.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            # 1. 登录
            await page.goto("http://localhost:3000/login")
            await page.fill('input[name="email"]', "test@example.com")
            await page.fill('input[name="password"]', "password123")
            await page.click('button[type="submit"]')

            # 2. 进入项目看板
            await page.goto("http://localhost:3000/projects/proj-1/kanban")
            await page.wait_for_selector('.swimlane')

            # 3. 创建新需求
            await page.click('button:has-text("Add Requirement")')
            await page.fill('input[name="title"]', "测试需求")
            await page.fill('textarea[name="description"]', "测试描述")
            await page.click('button:has-text("Create")')

            # 4. AI 分析
            await page.wait_for_selector('[data-testid="ai-badge"]')
            ai_badge = await page.query_selector('[data-testid="ai-badge"]')
            assert await ai_badge.inner_text() == "AI FIRST"

            # 5. 点击 AI 批准
            await page.click('[data-testid="ai-approve-button"]')

            # 6. 验证需求移动到下一泳道
            await page.wait_for_timeout(2000)
            card = await page.query_selector('[data-req-id]')

            # 验证在 Analysis 泳道
            analysis_swimlane = await page.query_selector('#swimlane-analysis')
            assert await analysis_swimlane.evaluate_handle('el => el.contains(card)')

            # 7. 继续流转（重复）
            for status in ["design", "development", "testing", "completed"]:
                await self._transition_to_next_status(page, status)

            # 8. 验证最终状态
            final_card = await page.query_selector('[data-req-id]')
            final_status = await final_card.get_attribute('data-status')
            assert final_status == "completed"

        finally:
            await browser.close()

    async def _transition_to_next_status(self, page, target_status):
        """转换到下一个状态的辅助方法"""
        # 找到卡片
        card = await page.query_selector('[data-req-id]')

        # 拖拽到目标泳道
        target_swimlane = await page.query_selector(f'#swimlane-{target_status}')
        await card.drag_to(target_swimlane)

        # AI 批准
        await page.wait_for_selector('[data-testid="ai-approve-dialog"]')
        await page.click('[data-testid="approve-transition"]')
```

### 团队管理 E2E

```python
# tests/e2e/test_team_management.py
class TestTeamManagement:
    @pytest.mark.asyncio
    async def test_add_ai_agent(self, async_playwright):
        """测试添加 AI Agent"""
        browser = await async_playwright.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            await page.goto("http://localhost:3000/projects/proj-1/team")

            # 点击添加 AI Agent 按钮
            await page.click('button:has-text("Add AI Agent")')

            # 填写表单
            await page.fill('input[name="name"]', "Analysis Agent")
            await page.fill('input[name="nickname"]', "Alex")
            await page.select_option('select[name="role"]', "analysis_agent")
            await page.fill('input[name="skills"]', "需求分析,重复检测")
            await page.check('input[name="="memory-enabled"]')

            # 提交
            await page.click('button:has-text("Add AI Agent")')

            # 验证 Agent 出现在列表中
            await page.wait_for_selector('[data-testid="agent-card"]')
            agent_card = await page.query_selector('[data-testid="agent-card"]')

            assert await agent_card.inner_text() == "Alex"

            # 验证角色标签
            role_badge = await agent_card.query_selector('[data-testid="role-badge"]')
            assert await role_badge.inner_text() == "ANALYSIS"

        finally:
            await browser.close()

    @pytest.mark.asyncio
    async def test_role_uniqueness(self, async_playwright):
        """测试角色唯一性"""
        browser = await async_playwright.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            await page.goto("http://localhost:3000/projects/proj-1/team")

            # 点击添加 AI Agent
            await page.click('button:has-text("Add AI Agent")')

            # 尝试选择已占用的角色
            role_select = await page.query_selector('select[name="role"]')
            await role_select.select_option("analysis_agent")

            # 验证已占用的角色不可选
            assert await role_select.is_disabled()

            # 选择可用角色
            available_role = "design_agent"
            await role_select.select_option(available_role)

            # 提交
            await page.fill('input[name="name"]', "Design Agent")
            await page.fill('input[name="nickname"]', "Bob")
            await page.click('button:has-text("Add AI Agent")')

            # 验证成功添加
            await page.wait_for_selector('[data-testid="agent-card"]:has-text("Bob")')

        finally:
            await browser.close()
```

### 飞书集成 E2E

```python
# tests/e2e/test_lark_integration.py
class TestLarkIntegration:
    @pytest.mark.asyncio
    async def test_lark_to_requirement_flow(self, async_playwright):
        """测试从飞书消息到需求创建的完整流程"""
        # 这个测试需要实际的飞收集成或模拟
        pass

    @pytest.mark.asyncio
    async def test_lark_document_edit_flow(self, async_playwright):
        """测试飞书文档编辑流程"""
        # 1. 创建有飞书文档的需求
        req = await create_requirement_with_lark_doc()

        # 2. 在前端查看需求
        page = await browser.new_page()
        await page.goto(f"http://localhost:3000/requirements/{req.id}")

        # 3. 验证显示飞书文档链接
        lark_link = await page.query_selector('[data-testid="lark-doc-link"]')
        assert lark_link is not None

        # 4. 点击链接（新标签页打开）
        with page.expect_popup():
            await lark_link.click()

        # 5. 验证跳转到飞书
        # 注意：这需要实际飞书环境或 mock
```

## 6. 性能测试

### API 性能测试

```python
# tests/performance/test_api_performance.py
from locust import HttpUser, task, between

class APIUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def get_projects(self):
        self.client.get("/api/v1/projects")

    @task
    def get_requirements(self):
        self.client.get("/api/v1/projects/proj-1/requirements")

    @task
    def create_requirement(self):
        self.client.post(
            "/api/v1/projects/proj-1/requirements",
            json={"title": "Test", "priority": "medium"}
        )

    @task
    def transition_requirement(self):
        self.client.post(
            "/api/v1/requirements/req-1/transition",
            json={"to_status": "analysis", "ai_approved": True}
        )

# 运行：locust -f tests/performance/test_api_performance.py --host=http://localhost:8000
```

### 前端性能测试

```javascript
// tests/performance/frontend-performance.spec.ts
describe('Frontend Performance', () => {
  it('Kanban board should render under 100ms', () => {
    const start = performance.now();

    render(<KanbanBoard />);

    const end = performance.now();
    expect(end - start).toBeLessThan(100);
  });

  it('Requirement card should render under 50ms', () => {
    const start = performance.now();

    render(<RequirementCard requirement={mockRequirement} />);

    const end = performance.now();
    expect(end - start).toBeLessThan(50);
  });

  it('List with 1000 requirements should handle efficiently', () => {
    const requirements = Array.from({ length: 1000 }, (_, i) => ({
      id: `req-${i}`,
      title: `Requirement ${i}`
    }));

    const start = performance.now();
    render(<RequirementList requirements={requirements} />);
    const end = performance.now();

    // 应该在 500ms 内完成
    expect(end - start).toBeLessThan(500);
  });
});
```

## 7. 安全测试

### 认证和授权测试

```python
# tests/security/test_auth.py
class TestAuthentication:
    def test_unauthenticated_access(self, client):
        """测试未认证访问"""
        response = client.get("/api/v1/projects/proj-1/requirements")

        assert response.status_code == 401

    def test_invalid_token(self, client):
        """测试无效 Token"""
        response = client.get(
            "/api/v1/projects/proj-1/requirements",
            headers={"Authorization": "Bearer invalid-token"}
        )

        assert response.status_code == 401

    def test_cross_project_access(self, client):
        """测试跨项目访问"""
        # 用户 A 的 Token
        user_a_token = get_token_for_user("user-a")

        response = client.get(
            "/api/v1/projects/project-b/requirements",  # 用户 A 访问项目 B
            headers={"Authorization": f"Bearer {user_a_token}"}
        )

        assert response.status_code == 403
```

### 输入验证测试

```python
# tests/security/test_input_validation.py
class TestInputValidation:
    def test_sql_injection_prevention(self, client):
        """测试 SQL 注入防护"""
        malicious_input = "'; DROP TABLE requirements; --"

        response = client.post(
            "/api/v1/projects/proj-1/requirements",
            json={"title": malicious_input},
            headers=auth_headers
        )

        # 应该被验证拒绝或安全处理
        assert response.status_code in [400, 422]

    def test_xss_prevention(self, client):
        """测试 XSS 防护"""
        xss_payload = "<script>alert('xss')</script>"

        response = client.post(
            "/api/v1/projects/proj-1/requirements",
            json={"title": xss_payload},
            headers=auth_headers
        )

        # 验证返回数据中不包含脚本标签
        data = response.json()
        assert "<script>" not in data.get("title", "")
```

## 8. 测试用例优先级

| 优先级 | 测试用例类别 | 原因 |
|--------|--------------|------|
| P0 | 完整需求生命周期 E2E | 核心功能 |
| P0 | 团队成员管理 | 核心功能 |
| P0 | AI Agent 执行 | 核心功能 |
| P0 | 数据持久化 | 数据完整性 |
| P0 | 认证授权 | 安全性 |
| P1 | API 端点覆盖 | API 完整性 |
| P1 | DeepAgent 集成 | 外部集成 |
| P1 | 飞书集成 | 外部集成 |
| P2 | 性能测试 | 用户体验 |
| P2 | 可访问性 | 合规性 |

## 9. 自动化测试流水线

```yaml
# .github/workflows/test.yml
name: Test Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  # 后端测试
  backend-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      redis:
        image: redis:7
        ports:
          - 6379:6379

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov

      - name: Run unit tests
        run: |
          pytest tests/unit/ --cov=app --cov-report=xml
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
          REDIS_URL: redis://localhost:6379

      - name: Run integration tests
        run: |
          pytest tests/integration/

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml

  # 前端测试
  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm ci

      - name: Run unit tests
        run: npm test

      - name: Run E2E tests
        run: npx playwright test

      - name: Upload E2E artifacts
        uses: actions/upload-artifact@v3
        if: failure()
        with:
          name: playwright-report
          path: playwright-report/

  # E2E 测试
  e2e-tests:
    runs-on: ubuntu-latest
    needs: [backend-tests, frontend-tests]
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run E2E tests
        run: pytest tests/e2e/

      - name: Upload E2E screenshots
        uses: actions/upload-artifact@v3
        if: failure()
        with:
          name: e2e-screenshots
          path: tests/e2e/screenshots/
```

## 10. 持续集成/持续部署 (CI/CD) 流程

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        开发者推送代码                                │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     单元测试 + 集成测试                             │
│                      ✓ 通过                                            │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       代码审查 (PR)                                 │
│                      ✓ 批准                                             │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      合并到 develop 分支                             │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                  部署到 Staging 环境                                │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       运行 E2E 测试                                      │
│                      ✓ 通过                                            │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      性能测试 + 安全测试                                   │
│                      ✓ 通过                                             │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      合并到 main 分支                                   │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      部署到 Production 环境                                │
└─────────────────────────────────────────────────────────────────────────┘
```

## 11. QA 流程和标准

### 冒烟测试检查清单

- [ ] 用户可以登录系统
- [ ] 用户可以创建新项目
- [ ] 用户可以添加团队成员
- [ ] 用户可以添加 AI Agent
- [ ] 用户可以创建新需求
- [ ] AI Agent 可以自动分析需求
- [ ] 用户可以批准 AI 建议
- [ ] 用户可以在泳道间拖拽需求
- [ ] 拖回功能正确标记返回状态
- [ ] 飞书集成正常工作
- [ ] 用户可以查看 Agent 记忆
- [ ] 用户可以管理项目设置

### 回归测试标准

**版本 v1.0 回归测试：**
- [ ] 所有 P0 测试用例通过
- [ ] 所有 P1 测试用例通过
- [ ] 80% P2 测试用例通过
- [ ] 无新的严重 Bug
- [ ] 性能指标达标：
  - [ ] API 响应时间 < 200ms (P95)
  - [ ] 页面加载时间 < 2s (P95)
  - [ ] 数据库查询时间 < 100ms (P95)
- [ ] 安全扫描通过

### 发布标准

**可以发布到 Production 的条件：**
1. ✓ 所有测试通过（单元、集成、E2E）
2. ✓ 代码覆盖率达标（单元 >80%，集成 >70%）
3. ✓ 性能测试通过
4. ✓ 安全测试通过
5. ✓ 冒烟测试通过
6. ✓ 回归测试通过
7. ✓ 产品验收通过
8. ✓ 更新日志和发布说明

### Bug 报告流程

```
发现 Bug
   │
   ├─ 记录到问题追踪系统（Jira/Linear）
   ├─ 分配优先级（P0/P1/P2）
   ├─ 分配给开发人员
   │
   ▼
开发修复
   │
   ├─ 创建分支
   ├─ 修复 Bug
   ├─ 添加测试用例
   │
   ▼
代码审查
   │
   ├─ 提交 PR
   ├─ 代码审查通过
   │
   ▼
测试验证
   │
   ├─ 运行相关测试
   ├─ 确认修复有效
   └─ 无回归问题
   │
   ▼
关闭 Bug
   │
   └─ 更新问题状态为已解决
```

## 12. 测试数据管理

### 测试数据库设置

```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine("postgresql://test:test@localhost:5432/test_db")
    yield engine
    engine.dispose()

@pytest.fixture(scope="function")
def db_session(db_engine):
    Session = sessionmaker(bind=db_engine)
    session = Session()

    # 创建所有表
    Base.metadata.create_all(bind=db_engine)

    yield session

    # 清理
    session.rollback()
    session.close()
    Base.metadata.drop_all(bind=db_engine)

@pytest.fixture
def test_project(db_session):
    project = Project(name="Test Project", slug="test-project")
    db_session.add(project)
    db_session.commit()
    return project

@pytest.fixture
def test_user(db_session):
    user = User(
        email="test@example.com",
        name="Test User"
    )
    db_session.add(user)
    db_session.commit()
    return user
```

### Mock 数据生成器

```python
# tests/factories.py
from app.models import Requirement, User, Project

class RequirementFactory:
    @staticmethod
    def create(**kwargs):
        defaults = {
            "title": "Test Requirement",
            "description": "Test description",
            "priority": "medium",
            "status": "new"
        }
        defaults.update(kwargs)
        return Requirement(**defaults)

    @staticmethod
    def create_batch(count: int, **kwargs):
        return [
            RequirementFactory.create(
                title=f"Requirement {i}",
                **kwargs
            )
            for i in range(count)
        ]
```

## 13. 测试报告

### Pytest 配置

```python
# pytest.ini
[pytest]
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --strict-markers
    --cov=app
    --cov-report=html
    --cov-report=term
    --cov-fail-under=80
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    performance: Performance tests
    security: Security tests
    slow: Slow running tests
```

### 测试报告示例

```
=================== Test Summary ====================
Total Tests: 347
Passed: 341
Failed: 4
Skipped: 2
Duration: 12m 34s

Coverage Report:
- Overall: 82.3%
- app/services: 85.1%
- app.api: 78.9%
- app.models: 91.2%

Failed Tests:
1. test_requirement_transition_invalid_state
2. test_ai_service_timeout_handling
3. test_lark_webhook_invalid_signature
4. test_e2e_requirement_creation_slow_load

Performance Metrics:
- API Response Time (P95): 156ms
- Page Load Time (P95): 1.8s
- DB Query Time (P95): 87ms

Security Scanning:
- XSS Vulnerabilities: 0
- SQL Injection: 0
- CSRF Protection: ✓
- Rate Limiting: ✓
```

## 14. 持续改进

### 测试指标监控

- 每日测试运行状态
- 测试覆盖率趋势
- Bug 发现趋势
- 性能基线和回归

### 测试策略优化

- 定期审查测试用例
- 删除冗余测试
- 添加新功能测试
- 提高测试数据多样性

### 自动化增强

- 自动生成测试数据
- 智能测试用例生成（AI 辅助）
- 自动回归测试选择
- 持续优化测试执行时间
