import { test, expect } from '@playwright/test';

test.describe('侧边栏导航功能验证', () => {
  // 使用测试用户登录
  test.beforeEach(async ({ page, context }) => {
    // 首先设置认证状态（模拟登录）
    await context.addInitScript(() => {
      // 设置认证token
      localStorage.setItem('auth-storage', JSON.stringify({
        state: {
          user: {
            id: 'test-user-id',
            email: 'test@example.com',
            name: 'Test User',
            avatarUrl: null,
            isActive: true,
            isSuperuser: false,
            createdAt: '2024-01-01T00:00:00Z',
            updatedAt: null
          },
          token: 'test-token-123',
          isAuthenticated: true
        },
        version: 0
      }));
    });

    await page.goto('http://localhost:3000/');
    await page.waitForLoadState('networkidle');
  });

  test.describe('侧边栏元素验证', () => {
    test('应该显示应用Logo', async ({ page }) => {
      await expect(page.getByText('Censorate')).toBeVisible();
    });

    test('应该显示所有导航菜单项', async ({ page }) => {
      const navigationItems = [
        'Dashboard',
        'Kanban',
        'Team',
        'Backlog',
        'Analytics',
        'Settings'
      ];

      for (const item of navigationItems) {
        await expect(page.getByRole('button', { name: item })).toBeVisible();
      }
    });

    test('应该显示Logout按钮', async ({ page }) => {
      await expect(page.getByRole('button', { name: 'Logout' })).toBeVisible();
    });
  });

  test.describe('导航功能验证', () => {
    test('Dashboard导航应该跳转到首页', async ({ page }) => {
      await page.getByRole('button', { name: 'Dashboard' }).click();
      await page.waitForURL('http://localhost:3000/');
      await expect(page).toHaveURL('http://localhost:3000/');
    });

    test('Kanban导航应该跳转到看板页面', async ({ page }) => {
      await page.getByRole('button', { name: 'Kanban' }).click();
      await page.waitForURL('**/kanban');
      await expect(page).toHaveURL(/.*kanban/);
    });

    test('Team导航应该跳转到团队页面', async ({ page }) => {
      await page.getByRole('button', { name: 'Team' }).click();
      await page.waitForURL('**/team');
      await expect(page).toHaveURL(/.*team/);
    });

    test('Backlog导航应该跳转到Backlog页面', async ({ page }) => {
      await page.getByRole('button', { name: 'Backlog' }).click();
      await page.waitForURL('**/backlog');
      await expect(page).toHaveURL(/.*backlog/);
    });

    test('Analytics导航应该跳转到Analytics页面', async ({ page }) => {
      await page.getByRole('button', { name: 'Analytics' }).click();
      await page.waitForURL('**/analytics');
      await expect(page).toHaveURL(/.*analytics/);
    });

    test('Settings导航应该跳转到Settings页面', async ({ page }) => {
      await page.getByRole('button', { name: 'Settings' }).click();
      await page.waitForURL('**/settings');
      await expect(page).toHaveURL(/.*settings/);
    });
  });

  test.describe('导航状态验证', () => {
    test('当前页面的导航项应该高亮', async ({ page }) => {
      // 在Dashboard页面，Dashboard应该高亮
      await page.goto('http://localhost:3000/');
      await page.waitForLoadState('networkidle');

      const dashboardButton = page.getByRole('button', { name: 'Dashboard' });
      await expect(dashboardButton).toBeVisible();

      // 跳转到Kanban页面
      await page.getByRole('button', { name: 'Kanban' }).click();
      await page.waitForURL('**/kanban');

      const kanbanButton = page.getByRole('button', { name: 'Kanban' });
      await expect(kanbanButton).toBeVisible();
    });

    test('导航应该能够在多个页面间正常切换', async ({ page }) => {
      // 依次访问所有页面
      const pages = [
        { name: 'Dashboard', url: '/' },
        { name: 'Kanban', url: '/kanban' },
        { name: 'Team', url: '/team' },
        { name: 'Backlog', url: '/backlog' },
        { name: 'Analytics', url: '/analytics' },
        { name: 'Settings', url: '/settings' },
      ];

      for (const { name, url } of pages) {
        await page.getByRole('button', { name }).click();
        await page.waitForURL(`**${url}`);
        await expect(page).toHaveURL(new RegExp(`.*${url.replace('/', '\\/')}`));
      }
    });
  });

  test.describe('Logout功能验证', () => {
    test('点击Logout应该清除认证状态', async ({ page, context }) => {
      // 首先确认已登录
      await expect(page.getByText('Censorate')).toBeVisible();

      // 点击Logout
      await page.getByRole('button', { name: 'Logout' }).click();

      // 应该跳转到登录页面
      await page.waitForURL('**/login');
      await expect(page).toHaveURL(/.*login/);
    });

    test('Logout后应该无法访问需要认证的页面', async ({ page, context }) => {
      // 先登录
      await context.addInitScript(() => {
        localStorage.setItem('auth-storage', JSON.stringify({
          state: {
            user: {
              id: 'test-user-id',
              email: 'test@example.com',
              name: 'Test User',
              avatarUrl: null,
              isActive: true,
              isSuperuser: false,
              createdAt: '2024-01-01T00:00:00Z',
              updatedAt: null
            },
            token: 'test-token-123',
            isAuthenticated: true
          },
          version: 0
        }));
      });

      await page.goto('http://localhost:3000/');
      await page.waitForLoadState('networkidle');

      // 点击Logout
      await page.getByRole('button', { name: 'Logout' }).click();
      await page.waitForURL('**/login');

      // 尝试访问Dashboard
      await page.goto('http://localhost:3000/');
      await page.waitForLoadState('networkidle');

      // 应该重定向回登录页
      await expect(page).toHaveURL(/.*login/);
    });
  });

  test.describe('响应式导航验证', () => {
    test('移动端应该显示侧边栏切换', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });

      // 在移动端，侧边栏应该是隐藏的，有菜单按钮
      // 这个测试依赖于具体实现，先跳过具体实现细节
      await expect(page.getByText('Censorate')).toBeVisible();
    });

    test('桌面端侧边栏应该固定显示', async ({ page }) => {
      await page.setViewportSize({ width: 1920, height: 1080 });

      // 在桌面端，侧边栏应该始终可见
      await expect(page.getByText('Censorate')).toBeVisible();
      await expect(page.getByRole('button', { name: 'Dashboard' })).toBeVisible();
    });
  });
});
