import { test, expect } from '@playwright/test';

test('should allow login with any email/password', async ({ page }) => {
  // Navigate to login page
  await page.goto('http://localhost:3000/login');

  // Wait for the email input to be visible
  await page.waitForSelector('input[placeholder="name@company.com"]');

  // Fill in login form
  await page.fill('input[placeholder="name@company.com"]', 'test@example.com');
  await page.fill('input[type="password"]', 'anything');

  // Click login button
  await page.click('button[type="submit"]');

  // Wait for login to complete and for redirect to home page
  await page.waitForURL('http://localhost:3000/');

  // Verify we are on home page
  expect(page.url()).toBe('http://localhost:3000/');
});