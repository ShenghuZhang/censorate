import { test, expect } from '@playwright/test';

test('should navigate to login page', async ({ page, context }) => {
  await context.clearCookies();
  await page.goto('http://localhost:3000');
  // Wait a bit for redirect
  await page.waitForURL('**/login', { timeout: 10000 });
});

test('should display login page elements', async ({ page }) => {
  await page.goto('http://localhost:3000/login');

  await expect(page.locator('h1:has-text("Censorate Management")')).toBeVisible();
  await expect(page.getByPlaceholder('name@company.com')).toBeVisible();
  await expect(page.getByPlaceholder('••••••••')).toBeVisible();
  await expect(page.locator('button[type="submit"]')).toBeVisible();
});

test('should toggle password visibility', async ({ page }) => {
  await page.goto('http://localhost:3000/login');

  const passwordInput = page.getByPlaceholder('••••••••');
  await expect(passwordInput).toHaveAttribute('type', 'password');

  await page.click('button:has(svg)');
  await expect(passwordInput).toHaveAttribute('type', 'text');

  await page.click('button:has(svg)');
  await expect(passwordInput).toHaveAttribute('type', 'password');
});

test('should switch between auth modes', async ({ page }) => {
  await page.goto('http://localhost:3000/login');

  await expect(page.getByText('Standard Sign In')).toBeVisible();
  await expect(page.getByPlaceholder('name@company.com')).toBeVisible();

  await page.click('button:has-text("LDAP / Enterprise")');
  await expect(page.getByPlaceholder('your.username')).toBeVisible();

  await page.click('button:has-text("Standard Sign In")');
  await expect(page.getByPlaceholder('name@company.com')).toBeVisible();
});

test('should show forgot password link', async ({ page }) => {
  await page.goto('http://localhost:3000/login');

  await expect(page.getByText('Forgot Password?')).toBeVisible();
});

test('should show request account button', async ({ page }) => {
  await page.goto('http://localhost:3000/login');

  await expect(page.getByRole('button', { name: 'Request an Account' })).toBeVisible();
});

test('should display footer links', async ({ page }) => {
  await page.goto('http://localhost:3000/login');

  await expect(page.getByText('Privacy Policy')).toBeVisible();
  await expect(page.getByText('Terms of Service')).toBeVisible();
  await expect(page.getByText('Security')).toBeVisible();
  await expect(page.getByText('Help Center')).toBeVisible();
});
