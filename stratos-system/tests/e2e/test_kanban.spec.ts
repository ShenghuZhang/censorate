import { test, expect } from '@playwright/test';

test.describe('Kanban Board', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login');
    await page.waitForSelector('input[type="email"]');
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button[type="submit"]');
    await page.waitForURL('http://localhost:3000/');
  });

  test('should display kanban board with lanes', async ({ page }) => {
    // Navigate to a project's kanban board
    await page.goto('/projects');
    await page.waitForSelector('[data-testid="project-card"]');
    await page.click('[data-testid="project-card"]:first-child');
    await page.waitForURL('/projects/*');
    await page.click('[data-testid="kanban-tab"]');

    // Wait for kanban board to load
    await page.waitForSelector('[data-testid="kanban-board"]');

    // Verify all lanes are present
    const lanes = ['New', 'Analysis', 'Design', 'Development', 'Testing', 'Completed'];
    for (const laneName of lanes) {
      await expect(page.locator(`[data-testid="lane-${laneName.toLowerCase()}"]`)).toBeVisible();
    }
  });

  test('should allow dragging requirements between lanes', async ({ page }) => {
    // Navigate to kanban board
    await page.goto('/projects');
    await page.waitForSelector('[data-testid="project-card"]');
    await page.click('[data-testid="project-card"]:first-child');
    await page.waitForURL('/projects/*');
    await page.click('[data-testid="kanban-tab"]');
    await page.waitForSelector('[data-testid="kanban-board"]');

    // Check initial state: find a card in "New" lane
    const newLane = page.locator('[data-testid="lane-new"]');
    const analysisLane = page.locator('[data-testid="lane-analysis"]');

    // Get initial counts
    const initialNewCount = await newLane.locator('[data-testid="kanban-card"]').count();
    const initialAnalysisCount = await analysisLane.locator('[data-testid="kanban-card"]').count();

    if (initialNewCount > 0) {
      // Drag first card from New to Analysis
      const card = newLane.locator('[data-testid="kanban-card"]').first();
      await card.dragTo(analysisLane);

      // Wait for animation
      await page.waitForTimeout(500);

      // Verify counts changed
      const finalNewCount = await newLane.locator('[data-testid="kanban-card"]').count();
      const finalAnalysisCount = await analysisLane.locator('[data-testid="kanban-card"]').count();

      expect(finalNewCount).toBe(initialNewCount - 1);
      expect(finalAnalysisCount).toBe(initialAnalysisCount + 1);
    }
  });

  test('should allow creating a new requirement from kanban', async ({ page }) => {
    // Navigate to kanban board
    await page.goto('/projects');
    await page.waitForSelector('[data-testid="project-card"]');
    await page.click('[data-testid="project-card"]:first-child');
    await page.waitForURL('/projects/*');
    await page.click('[data-testid="kanban-tab"]');
    await page.waitForSelector('[data-testid="kanban-board"]');

    // Click add button in New lane
    await page.click('[data-testid="add-card-new"]');

    // Wait for modal
    await page.waitForSelector('[data-testid="create-requirement-modal"]');

    // Fill in requirement details
    await page.fill('[data-testid="requirement-title-input"]', 'New Requirement');
    await page.fill('[data-testid="requirement-description-input"]', 'Requirement description');
    await page.selectOption('[data-testid="requirement-priority-select"]', 'high');

    // Click create
    await page.click('[data-testid="submit-requirement-btn"]');

    // Wait for card to appear
    await page.waitForSelector('[data-testid="kanban-card"]:has-text("New Requirement")');

    // Verify new card is in New lane
    const newCard = page.locator('[data-testid="lane-new"]').locator('[data-testid="kanban-card"]:has-text("New Requirement")');
    await expect(newCard).toBeVisible();
  });

  test('should allow opening requirement detail from card', async ({ page }) => {
    // Navigate to kanban board
    await page.goto('/projects');
    await page.waitForSelector('[data-testid="project-card"]');
    await page.click('[data-testid="project-card"]:first-child');
    await page.waitForURL('/projects/*');
    await page.click('[data-testid="kanban-tab"]');
    await page.waitForSelector('[data-testid="kanban-board"]');

    // Click on a card
    const card = page.locator('[data-testid="kanban-card"]').first();
    await card.click();

    // Wait for detail modal
    await page.waitForSelector('[data-testid="requirement-detail-modal"]');

    // Verify detail is displayed
    await expect(page.locator('[data-testid="requirement-title"]')).toBeVisible();
    await expect(page.locator('[data-testid="requirement-description"]')).toBeVisible();
  });
});
