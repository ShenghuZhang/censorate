import { test, expect } from '@playwright/test';

test('should allow user to login and access dashboard', async ({ page }) => {
  // Navigate to login page
  await page.goto('/login');

  // Wait for login form to load
  await page.waitForSelector('input[type="email"]');

  // Fill in login form
  await page.fill('input[type="email"]', 'test@example.com');
  await page.fill('input[type="password"]', 'password123');

  // Click login button
  await page.click('button[type="submit"]');

  // Wait for navigation to dashboard
  await page.waitForURL('http://localhost:3000/');

  // Verify dashboard is loaded
  await expect(page).toHaveURL('http://localhost:3000/');
  await expect(page.locator('h1:has-text("Welcome")')).toBeVisible();
});

test('should show error for invalid credentials', async ({ page }) => {
  // Navigate to login page
  await page.goto('/login');

  // Wait for login form to load
  await page.waitForSelector('input[type="email"]');

  // Fill in login form with invalid credentials
  await page.fill('input[type="email"]', 'invalid@example.com');
  await page.fill('input[type="password"]', 'wrongpassword');

  // Click login button
  await page.click('button[type="submit"]');

  // Wait for error to appear
  await page.waitForSelector('.error');

  // Verify error message is displayed
  const errorMessage = page.locator('.error');
  await expect(errorMessage).toBeVisible();
  await expect(errorMessage).toContainText('Invalid credentials');
});

test('should allow user to register and login', async ({ page }) => {
  // Navigate to login page
  await page.goto('/login');

  // Click register link
  await page.click('a:has-text("Register")');

  // Wait for register form to load
  await page.waitForSelector('input[name="name"]');

  // Fill in register form
  await page.fill('input[name="name"]', 'Test User');
  await page.fill('input[type="email"]', 'new@example.com');
  await page.fill('input[type="password"]', 'password123');
  await page.fill('input[name="confirmPassword"]', 'password123');

  // Click register button
  await page.click('button[type="submit"]');

  // Wait for navigation to dashboard
  await page.waitForURL('http://localhost:3000/');

  // Verify user is logged in
  await expect(page).toHaveURL('http://localhost:3000/');
  await expect(page.locator('h1:has-text("Welcome, Test User!")')).toBeVisible();
});

test('should allow user to logout', async ({ page }) => {
  // First login to get into logged in state
  await page.goto('/login');
  await page.waitForSelector('input[type="email"]');
  await page.fill('input[type="email"]', 'test@example.com');
  await page.fill('input[type="password"]', 'password123');
  await page.click('button[type="submit"]');
  await page.waitForURL('http://localhost:3000/');

  // Click logout button
  await page.click('button:has-text("Logout")');

  // Wait for navigation to login page
  await page.waitForURL('http://localhost:3000/login');

  // Verify login page is shown
  await expect(page).toHaveURL('http://localhost:3000/login');
  await expect(page.locator('h1:has-text("Login")')).toBeVisible();
});
