# Censorate System E2E Test Plan

## Overview
Comprehensive E2E testing strategy for the AI-native requirement management system using Playwright, focusing on critical user flows, integration points, and the notification system.

---

## 1. Critical User Flows to Test

### Priority 1 (Critical Paths)
#### Authentication Flow
- [ ] User login with valid credentials
- [ ] User login with invalid credentials (error handling)
- [ ] Logout functionality
- [ ] Session persistence on page reload

#### Project Management Flow
- [ ] Create new project (both Technical and Non-Technical types)
- [ ] Edit project settings (name, description, lane configuration)
- [ ] Delete project (with confirmation)
- [ ] Switch between multiple projects

#### Kanban Board Flow
- [ ] View requirements in swimlanes
- [ ] Drag-and-drop requirements between lanes
- [ ] Filter requirements by assignee, priority, tags
- [ ] Search requirements by keyword
- [ ] Create new requirement
- [ ] Edit requirement details
- [ ] Delete requirement (with confirmation)

#### Team & Agent Management Flow
- [ ] Add/remove team members
- [ ] Assign roles and permissions
- [ ] Add AI agents to project
- [ ] View agent status and activity
- [ ] Configure agent skills

#### Requirement Detail Flow
- [ ] View requirement details and history
- [ ] Add comments and mentions
- [ ] Attach files to requirements
- [ ] Update requirement status and properties
- [ ] View requirement activity timeline

#### AI Assistant Flow
- [ ] Open Ask AI window from kanban
- [ ] Ask AI questions about requirements
- [ ] Receive AI responses and suggestions
- [ ] Apply AI suggestions to requirements

---

### Priority 2 (Important Features)
#### Notification Flow
- [ ] Receive real-time notifications
- [ ] View notification dropdown
- [ ] Mark notifications as read/unread
- [ ] Delete notifications
- [ ] Mark all as read
- [ ] Notification badges show correct unread count

#### Analytics Flow
- [ ] View project analytics dashboard
- [ ] View throughput and workload charts
- [ ] Filter analytics by time range
- [ ] Export analytics reports

#### Settings Flow
- [ ] Update user profile
- [ ] Configure notification preferences
- [ ] Manage GitHub repository integrations
- [ ] Configure project swimlanes

---

## 2. E2E Test Architecture Using Playwright

### Directory Structure
```
censorate-system/frontend/
├── tests/
│   └── e2e/
│       ├── auth/
│       │   ├── login.spec.ts
│       │   └── logout.spec.ts
│       ├── projects/
│       │   ├── create.spec.ts
│       │   ├── edit.spec.ts
│       │   └── list.spec.ts
│       ├── kanban/
│       │   ├── board.spec.ts
│       │   ├── drag-drop.spec.ts
│       │   ├── requirements.spec.ts
│       │   └── search-filter.spec.ts
│       ├── team/
│       │   ├── members.spec.ts
│       │   └── agents.spec.ts
│       ├── requirements/
│       │   ├── detail.spec.ts
│       │   ├── comments.spec.ts
│       │   └── state-transitions.spec.ts
│       ├── notifications/
│       │   ├── dropdown.spec.ts
│       │   ├── realtime.spec.ts
│       │   └── preferences.spec.ts
│       ├── ai-assistant/
│       │   └── ask-ai.spec.ts
│       ├── analytics/
│       │   └── dashboard.spec.ts
│       └── settings/
│           ├── profile.spec.ts
│           └── project-settings.spec.ts
├── pages/                 # Page Object Models
│   ├── LoginPage.ts
│   ├── ProjectsPage.ts
│   ├── KanbanPage.ts
│   ├── RequirementDetailPage.ts
│   ├── TeamPage.ts
│   ├── NotificationsPage.ts
│   └── SettingsPage.ts
├── fixtures/              # Test data and setup
│   ├── auth.ts
│   ├── test-data.ts
│   └── api-mocks.ts
└── playwright.config.ts
```

### Page Object Model Implementation Example
```typescript
// pages/KanbanPage.ts
import { Page, Locator } from '@playwright/test'

export class KanbanPage {
  readonly page: Page
  readonly swimlanes: Locator
  readonly requirementCards: Locator
  readonly createRequirementBtn: Locator
  readonly searchInput: Locator
  readonly askAiFab: Locator

  constructor(page: Page) {
    this.page = page
    this.swimlanes = page.locator('[data-testid="swimlane"]')
    this.requirementCards = page.locator('[data-testid="requirement-card"]')
    this.createRequirementBtn = page.locator('[data-testid="create-requirement-btn"]')
    this.searchInput = page.locator('[data-testid="search-input"]')
    this.askAiFab = page.locator('[data-testid="ask-ai-fab"]')
  }

  async goto(projectId: string) {
    await this.page.goto(`/projects/${projectId}/board`)
    await this.page.waitForLoadState('networkidle')
  }

  async createRequirement(title: string, description?: string) {
    await this.createRequirementBtn.click()
    await this.page.locator('[data-testid="requirement-title-input"]').fill(title)
    if (description) {
      await this.page.locator('[data-testid="requirement-description-input"]').fill(description)
    }
    await this.page.locator('[data-testid="submit-requirement-btn"]').click()
    await this.page.waitForResponse(resp => resp.url().includes('/api/v1/requirements') && resp.status() === 201)
  }

  async dragRequirementToLane(requirementTitle: string, targetLane: string) {
    const card = this.requirementCards.filter({ hasText: requirementTitle })
    const lane = this.swimlanes.filter({ hasText: targetLane })
    
    await card.dragTo(lane)
    await this.page.waitForResponse(resp => resp.url().includes('/api/v1/requirements') && resp.method() === 'PATCH')
  }
}
```

### Playwright Configuration
```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['junit', { outputFile: 'playwright-results.xml' }]
  ],
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    actionTimeout: 10000,
    navigationTimeout: 30000,
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
  },
})
```

---

## 3. Test Data Management

### Test User Accounts
- Pre-configured test users with different roles (admin, member, viewer)
- Test user credentials stored in environment variables
- Auto-cleanup of test data after each test run

### Test Project Setup
```typescript
// fixtures/test-data.ts
export const testProjects = {
  technicalProject: {
    name: 'Test Technical Project',
    type: 'technical',
    description: 'Test project for E2E testing',
    lanes: ['Backlog', 'Design', 'Development', 'Testing', 'Deployment', 'Done']
  },
  nonTechnicalProject: {
    name: 'Test Business Project',
    type: 'non-technical',
    description: 'Test business project for E2E testing',
    lanes: ['Idea', 'Analysis', 'Approval', 'Implementation', 'Review', 'Done']
  }
}

export const testRequirements = [
  {
    title: 'REQ-001: Implement user authentication',
    description: 'Add login/logout functionality with JWT tokens',
    priority: 'high',
    assignee: 'test-user@example.com'
  },
  {
    title: 'REQ-002: Create API documentation',
    description: 'Generate OpenAPI documentation for all endpoints',
    priority: 'medium',
    assignee: 'test-user@example.com'
  }
]
```

### API Fixtures for Test Setup
- Use backend API calls to create test data before tests
- Clean up test data after test execution
- Mock external services (GitHub, AI APIs) for isolated testing

---

## 4. Integration Points to Validate

### Frontend ↔ Backend API Integration
- [ ] All REST API endpoints return expected responses
- [ ] Error handling for 4xx/5xx responses
- [ ] Request/response payload validation
- [ ] Authentication tokens are properly sent with requests

### WebSocket Integration
- [ ] Real-time updates for requirement changes
- [ ] Real-time notification delivery
- [ ] Connection reconnection logic

### AI Agent Integration
- [ ] AI agent execution triggers correctly
- [ ] AI responses are displayed properly
- [ ] Agent activity is logged and visible

### Third-Party Integrations
- [ ] GitHub repository integration (webhooks, import/export)
- [ ] Email notification delivery
- [ ] File upload functionality

---

## 5. Notification System Testing

### Test Scenarios
#### Realtime Notifications
- [ ] Receive notification when mentioned in comment
- [ ] Receive notification when requirement is assigned
- [ ] Receive notification when requirement status changes
- [ ] Receive notification when new comment is added to followed requirement
- [ ] Notification badge updates in real-time without page reload

#### Notification Management
- [ ] Clicking notification navigates to relevant page
- [ ] Mark single notification as read
- [ ] Mark single notification as unread
- [ ] Mark all notifications as read
- [ ] Delete single notification
- [ ] Delete all read notifications
- [ ] Notification preferences are respected (email, in-app, push)

#### Notification Types to Test
- [ ] Mention notifications (@user in comments)
- [ ] Assignment notifications (requirement assigned to user)
- [ ] Status change notifications (requirement moved between lanes)
- [ ] Comment notifications (new comment on followed requirement)
- [ ] System notifications (agent completed task, errors, etc.)

### Edge Cases
- [ ] Notifications for offline users are delivered on reconnection
- [ ] Large number of notifications (pagination works)
- [ ] Notification formatting for long content
- [ ] Notification permissions are properly enforced

---

## 6. Test Execution Strategy

### Local Development
```bash
# Run all tests
npx playwright test

# Run specific test file
npx playwright test tests/e2e/kanban/board.spec.ts

# Run test in headed mode
npx playwright test --headed

# Debug test
npx playwright test --debug
```

### CI/CD Integration
- Run E2E tests on every PR and push to main branch
- Use separate test environment with test database
- Generate and store test artifacts (screenshots, videos, traces) for failed tests
- Integrate with Slack/email alerts for test failures

### Flaky Test Management
- Quarantine flaky tests with `test.fixme()` and link to GitHub issue
- Retry failed tests 2 times in CI
- Regularly review and fix flaky tests

---

## 7. Success Metrics
- [ ] 90%+ test coverage for critical user flows
- [ ] 99%+ test pass rate on main branch
- [ ] Test execution time < 15 minutes for full suite
- [ ] 0 critical bugs found in production that could have been caught by E2E tests
