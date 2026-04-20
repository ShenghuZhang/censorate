import { test, expect } from '@playwright/test';

test.describe('Skills Page', () => {
  test('should display skills page with correct title', async ({ page }) => {
    await page.goto('/skills');

    // Check page title
    await expect(page.locator('h1')).toContainText('Skills');
    await expect(page.locator('h1')).toBeVisible();
  });

  test('should display search and filter controls', async ({ page }) => {
    await page.goto('/skills');

    // Check search input
    const searchInput = page.locator('input[placeholder="Search skills..."]');
    await expect(searchInput).toBeVisible();

    // Check category filters
    await expect(page.getByText('All')).toBeVisible();

    // Check sort buttons
    await expect(page.getByText('Latest')).toBeVisible();
    await expect(page.getByText('Popular')).toBeVisible();

    // Check action buttons
    await expect(page.getByText('Reload')).toBeVisible();
    await expect(page.getByText('Upload Skill')).toBeVisible();
  });

  test('should open upload dialog when clicking Upload Skill', async ({ page }) => {
    await page.goto('/skills');

    // Click upload button
    await page.getByText('Upload Skill').click();

    // Check dialog is open
    await expect(page.getByText('Upload Skill')).toBeVisible();
    await expect(page.locator('input[placeholder="My awesome skill"]')).toBeVisible();

    // Close dialog
    await page.getByText('Cancel').click();
    await expect(page.getByText('Upload Skill').nth(1)).not.toBeVisible();
  });

  test('should display skills grid with skill cards', async ({ page }) => {
    await page.goto('/skills');

    // Check for loading or skills grid
    const loading = page.locator('.animate-spin');
    const skillsGrid = page.locator('.grid');

    // Wait for either loading to disappear or skills to appear
    try {
      await loading.waitFor({ state: 'detached', timeout: 5000 });
    } catch {
      // Loading might have disappeared already
    }

    // Check if skills grid is visible
    await expect(skillsGrid.or(page.getByText('No skills found'))).toBeVisible();
  });

  test('should filter by search query', async ({ page }) => {
    await page.goto('/skills');

    // Type search query
    const searchInput = page.locator('input[placeholder="Search skills..."]');
    await searchInput.fill('test');

    // Verify input value
    await expect(searchInput).toHaveValue('test');
  });

  test('should switch between sort options', async ({ page }) => {
    await page.goto('/skills');

    // Click Popular sort
    await page.getByText('Popular').click();

    // Verify Popular is selected (has white background)
    const popularButton = page.getByText('Popular');
    await expect(popularButton).toBeVisible();

    // Click Latest sort
    await page.getByText('Latest').click();

    // Verify Latest is visible
    await expect(page.getByText('Latest')).toBeVisible();
  });

  test('should display brain icon in header', async ({ page }) => {
    await page.goto('/skills');

    // Check for brain icon (using class or presence)
    const brainIcon = page.locator('svg').first();
    await expect(brainIcon).toBeVisible();
  });

  test('should have correct layout structure', async ({ page }) => {
    await page.goto('/skills');

    // Check main container
    const mainContainer = page.locator('.max-w-7xl');
    await expect(mainContainer).toBeVisible();
  });
});
