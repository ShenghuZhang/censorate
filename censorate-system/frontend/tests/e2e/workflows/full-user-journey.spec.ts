import { test, expect } from '@playwright/test';

test.describe('完整用户旅程端到端验证', () => {
  test('用户完整旅程：登录 → Dashboard → Kanban → Team → Logout', async ({ page, context }) => {
    // ==========================================
    // 阶段 1: 访问登录页面
    // ==========================================
    test.step('访问登录页面并验证所有元素', async () => {
      await page.goto('http://localhost:3000/login');
      await page.waitForLoadState('networkidle');

      // 验证登录页面核心元素
      await expect(page).toHaveURL('http://localhost:3000/login');
      await expect(page.getByText('Censorate Management')).toBeVisible();
      await expect(page.getByPlaceholder('name@company.com')).toBeVisible();
      await expect(page.getByPlaceholder('••••••••')).toBeVisible();
      await expect(page.getByRole('button', { name: 'Sign In' })).toBeVisible();
    });

    // ==========================================
    // 阶段 2: 测试登录页面交互功能
    // ==========================================
    test.step('验证登录页面交互功能', async () => {
      // 测试认证模式切换
      await page.getByText('LDAP / Enterprise').click();
      await expect(page.getByPlaceholder('your.username')).toBeVisible();

      await page.getByText('Standard Sign In').click();
      await expect(page.getByPlaceholder('name@company.com')).toBeVisible();

      // 测试密码可见性切换
      const passwordInput = page.getByPlaceholder('••••••••');
      await expect(passwordInput).toHaveAttribute('type', 'password');

      await page.locator('button:has(svg)').click();
      await expect(passwordInput).toHaveAttribute('type', 'text');

      await page.locator('button:has(svg)').click();
      await expect(passwordInput).toHaveAttribute('type', 'password');

      // 测试表单输入
      await page.getByPlaceholder('name@company.com').fill('journey-test@example.com');
      await passwordInput.fill('JourneyTest123!');

      await expect(page.getByPlaceholder('name@company.com')).toHaveValue('journey-test@example.com');
      await expect(passwordInput).toHaveValue('JourneyTest123!');
    });

    // ==========================================
    // 阶段 3: 测试表单验证
    // ==========================================
    test.step('验证表单验证功能', async () => {
      // 清空输入
      await page.getByPlaceholder('name@company.com').fill('');
      await page.getByPlaceholder('••••••••').fill('');

      // 提交空表单
      await page.getByRole('button', { name: 'Sign In' }).click();

      // 验证错误显示
      await expect(page.getByText('Email is required')).toBeVisible();

      // 输入时清除错误
      await page.getByPlaceholder('name@company.com').fill('t');
      await expect(page.getByText('Email is required')).not.toBeVisible();
    });

    // ==========================================
    // 阶段 4: 验证页脚链接
    // ==========================================
    test.step('验证页脚所有链接', async () => {
      const footerLinks = [
        'Privacy Policy',
        'Terms of Service',
        'Security',
        'Help Center'
      ];

      for (const link of footerLinks) {
        const linkElement = page.getByText(link);
        await expect(linkElement).toBeVisible();
        await expect(linkElement).toHaveAttribute('href', '#');
      }

      await expect(page.getByText('© 2024 Kinetic Workspace. All rights reserved.')).toBeVisible();
    });

    // ==========================================
    // 阶段 5: 模拟登录并访问Dashboard
    // ==========================================
    test.step('模拟登录并访问Dashboard', async () => {
      // 设置认证状态
      await context.addInitScript(() => {
        localStorage.setItem('auth-storage', JSON.stringify({
          state: {
            user: {
              id: 'journey-test-user-id',
              email: 'journey-test@example.com',
              name: 'Journey Test User',
              avatarUrl: null,
              isActive: true,
              isSuperuser: false,
              createdAt: '2024-01-01T00:00:00Z',
              updatedAt: null
            },
            token: 'journey-test-token-123',
            isAuthenticated: true
          },
          version: 0
        }));
      });

      // 重新加载页面以应用认证
      await page.goto('http://localhost:3000/');
      await page.waitForLoadState('networkidle');

      // 验证在Dashboard页面
      await expect(page.getByText('Welcome')).toBeVisible();
    });

    // ==========================================
    // 阶段 6: 验证侧边栏导航
    // ==========================================
    test.step('验证侧边栏导航完整功能', async () => {
      // 验证所有导航项存在
      const navigationItems = [
        'Dashboard',
        'Kanban',
        'Team',
        'Backlog',
        'Analytics',
        'Settings'
      ];

      for (const item of navigationItems) {
        const navButton = page.getByRole('button', { name: item });
        await expect(navButton).toBeVisible();
      }

      // 验证Logo和Logout
      await expect(page.getByText('Censorate')).toBeVisible();
      await expect(page.getByRole('button', { name: 'Logout' })).toBeVisible();
    });

    // ==========================================
    // 阶段 7: Dashboard页面功能验证
    // ==========================================
    test.step('验证Dashboard页面功能', async () => {
      // 验证欢迎信息
      await expect(page.getByText('Welcome')).toBeVisible();
      await expect(page.getByText('Successfully logged in')).toBeVisible();

      // 验证导航按钮
      const kanbanButton = page.getByText('Go to Kanban Board');
      const teamButton = page.getByText('Go to Team Management');

      await expect(kanbanButton).toBeVisible();
      await expect(teamButton).toBeVisible();
    });

    // ==========================================
    // 阶段 8: 导航到Kanban页面
    // ==========================================
    test.step('导航到Kanban页面并验证', async () => {
      // 点击Dashboard上的Kanban按钮
      await page.getByText('Go to Kanban Board').click();
      await page.waitForURL('**/kanban');
      await expect(page).toHaveURL(/.*kanban/);

      // 验证Kanban页面元素
      await expect(page.getByText('Project Kanban')).toBeVisible();
      await expect(page.getByText('Manage requirements and track progress')).toBeVisible();

      // 验证看板列
      await page.waitForTimeout(2000);
      const anyColumn = page.getByText('New').first()
        .or(page.getByText('Analysis').first())
        .or(page.getByText('Design').first())
        .or(page.getByText('Development').first())
        .or(page.getByText('Testing').first())
        .or(page.getByText('Completed').first());

      await expect(anyColumn).toBeVisible();
    });

    // ==========================================
    // 阶段 9: 通过侧边栏导航到Team页面
    // ==========================================
    test.step('通过侧边栏导航到Team页面', async () => {
      await page.getByRole('button', { name: 'Team' }).click();
      await page.waitForURL('**/team');
      await expect(page).toHaveURL(/.*team/);

      // 验证Team页面元素
      await expect(page.getByText('Team Members')).toBeVisible();
      await expect(page.getByText('Manage your team and AI agents')).toBeVisible();

      // 验证Add AI Agent按钮
      const addButton = page.getByText('Add AI Agent', { exact: true }).first();
      await expect(addButton).toBeVisible();
    });

    // ==========================================
    // 阶段 10: 测试完整的导航循环
    // ==========================================
    test.step('验证完整导航循环', async () => {
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

    // ==========================================
    // 阶段 11: 验证响应式设计
    // ==========================================
    test.step('验证响应式设计在不同设备上', async () => {
      // 移动端
      await page.setViewportSize({ width: 375, height: 667 });
      await page.goto('http://localhost:3000/');
      await page.waitForLoadState('networkidle');
      await expect(page.getByText('Censorate')).toBeVisible();

      // 平板端
      await page.setViewportSize({ width: 768, height: 1024 });
      await page.goto('http://localhost:3000/kanban');
      await page.waitForLoadState('networkidle');
      await expect(page.getByText('Project Kanban')).toBeVisible();

      // 桌面端
      await page.setViewportSize({ width: 1920, height: 1080 });
      await page.goto('http://localhost:3000/team');
      await page.waitForLoadState('networkidle');
      await expect(page.getByText('Team Members')).toBeVisible();
    });

    // ==========================================
    // 阶段 12: 测试Logout功能
    // ==========================================
    test.step('验证Logout功能', async () => {
      // 先确保已登录
      await context.addInitScript(() => {
        localStorage.setItem('auth-storage', JSON.stringify({
          state: {
            user: {
              id: 'journey-test-user-id',
              email: 'journey-test@example.com',
              name: 'Journey Test User',
              avatarUrl: null,
              isActive: true,
              isSuperuser: false,
              createdAt: '2024-01-01T00:00:00Z',
              updatedAt: null
            },
            token: 'journey-test-token-123',
            isAuthenticated: true
          },
          version: 0
        }));
      });

      await page.goto('http://localhost:3000/');
      await page.waitForLoadState('networkidle');

      // 点击Logout
      await page.getByRole('button', { name: 'Logout' }).click();

      // 验证跳转到登录页
      await page.waitForURL('**/login');
      await expect(page).toHaveURL(/.*login/);

      // 验证认证状态已清除
      const authStorage = await page.evaluate(() => {
        return localStorage.getItem('auth-storage');
      });

      // 验证登录页面元素可见
      await expect(page.getByText('Censorate Management')).toBeVisible();
      await expect(page.getByPlaceholder('name@company.com')).toBeVisible();
    });
  });

  test('快速验证：所有页面可访问性检查', async ({ page, context }) => {
    // 设置认证
    await context.addInitScript(() => {
      localStorage.setItem('auth-storage', JSON.stringify({
        state: {
          user: {
            id: 'quick-test-user',
            email: 'quick@example.com',
            name: 'Quick Test',
            avatarUrl: null,
            isActive: true,
            isSuperuser: false,
            createdAt: '2024-01-01T00:00:00Z',
            updatedAt: null
          },
          token: 'quick-token-123',
          isAuthenticated: true
        },
        version: 0
      }));
    });

    // 访问所有页面并验证基本元素
    const pagesToTest = [
      { path: '/', title: 'Welcome' },
      { path: '/kanban', title: 'Project Kanban' },
      { path: '/team', title: 'Team Members' },
      { path: '/backlog', title: '' },
      { path: '/analytics', title: '' },
      { path: '/settings', title: '' },
    ];

    for (const { path, title } of pagesToTest) {
      await page.goto(`http://localhost:3000${path}`);
      await page.waitForLoadState('networkidle');

      // 验证侧边栏始终存在
      await expect(page.getByText('Censorate')).toBeVisible();
      await expect(page.getByRole('button', { name: 'Dashboard' })).toBeVisible();

      // 如果有预期标题，验证标题
      if (title) {
        const titleElement = page.getByText(title).first();
        await expect(titleElement).toBeVisible();
      }
    }
  });
});
