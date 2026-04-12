import { test, expect } from '@playwright/test';

test.describe('Project Management', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login');
    await page.waitForSelector('input[type="email"]');
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button[type="submit"]');
    await page.waitForURL('http://localhost:3000/');
  });

  test('should display list of projects', async ({ page }) => {
    // Navigate to projects page
    await page.goto('/projects');

    // Wait for projects to load
    await page.waitForSelector('[data-testid="project-list"]');

    // Verify projects are displayed
    const projectList = page.locator('[data-testid="project-list"]');
    await expect(projectList).toBeVisible();

    // Check that at least one project exists
    const projectCards = page.locator('[data-testid="project-card"]');
    const count = await projectCards.count();
    expect(count).toBeGreaterThan(0);
  });

  test('should allow creating a new project', async ({ page }) => {
    // Navigate to projects page
    await page.goto('/projects');

    // Click create project button
    await page.click('[data-testid="create-project-btn"]');

    // Wait for modal to open
    await page.waitForSelector('[data-testid="create-project-modal"]');

    // Fill in project details
    await page.fill('[data-testid="project-name-input"]', 'New Test Project');
    await page.fill('[data-testid="project-description-input"]', 'This is a test project');
    await page.selectOption('[data-testid="project-type-select"]', 'software');

    // Click submit
    await page.click('[data-testid="submit-project-btn"]');

    // Wait for modal to close and project to appear
    await page.waitForSelector('[data-testid="project-card"]:has-text("New Test Project")');

    // Verify the new project is in the list
    const newProject = page.locator('[data-testid="project-card"]:has-text("New Test Project")');
    await expect(newProject).toBeVisible();
  });

  test('should allow viewing project details', async ({ page }) => {
    // Navigate to projects page
    await page.goto('/projects');

    // Wait for projects to load
    await page.waitForSelector('[data-testid="project-card"]');

    // Click on first project
    await page.click('[data-testid="project-card"]:first-child');

    // Wait for project details page
    await page.waitForURL('/projects/*');

    // Verify project details are displayed
    await expect(page.locator('[data-testid="project-title"]')).toBeVisible();
    await expect(page.locator('[data-testid="project-description"]')).toBeVisible();
  });

  test('should allow updating a project', async ({ page }) => {
    // Navigate to projects page
    await page.goto('/projects');

    // Wait for projects to load
    await page.waitForSelector('[data-testid="project-card"]');

    // Click on first project
    await page.click('[data-testid="project-card"]:first-child');

    // Wait for project details page
    await page.waitForURL('/projects/*');

    // Click edit button
    await page.click('[data-testid="edit-project-btn"]');

    // Wait for edit modal
    await page.waitForSelector('[data-testid="edit-project-modal"]');

    // Update project name
    await page.fill('[data-testid="project-name-input"]', 'Updated Project Name');

    // Click save
    await page.click('[data-testid="save-project-btn"]');

    // Verify the name was updated
    await expect(page.locator('[data-testid="project-title"]:has-text("Updated Project Name")')).toBeVisible();
  });

  test('should allow deleting a project', async ({ page }) => {
    // Navigate to projects page
    await page.goto('/projects');

    // Wait for projects to load
    await page.waitForSelector('[data-testid="project-card"]');

    // Get initial project count
    const initialCount = await page.locator('[data-testid="project-card"]').count();

    // Hover over first project and click delete
    const firstProject = page.locator('[data-testid="project-card"]').first();
    await firstProject.hover();
    await firstProject.locator('[data-testid="delete-project-btn"]').click();

    // Confirm deletion
    await page.waitForSelector('[data-testid="confirm-delete-modal"]');
    await page.click('[data-testid="confirm-delete-btn"]');

    // Wait for project to be removed
    await page.waitForTimeout(500);

    // Verify project count decreased
    const finalCount = await page.locator('[data-testid="project-card"]').count();
    expect(finalCount).toBe(initialCount - 1);
  });
});
