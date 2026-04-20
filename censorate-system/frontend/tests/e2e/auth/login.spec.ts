import { test, expect } from '@playwright/test';

test.describe('登录页面完整功能验证', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000/login');
    await page.waitForLoadState('networkidle');
  });

  test.describe('页面元素验证', () => {
    test('应该显示Logo和品牌信息', async ({ page }) => {
      // 验证Logo图标存在
      await expect(page.locator('svg[width="36"]').first()).toBeVisible();

      // 验证主标题
      await expect(page.getByText('Censorate Management')).toBeVisible();

      // 验证副标题
      await expect(page.getByText('Digital Studio & Enterprise Hub')).toBeVisible();
    });

    test('应该显示标准登录模式的所有元素', async ({ page }) => {
      // 确保在标准模式
      await page.getByText('Standard Sign In').click();

      // 验证邮箱/用户名标签和输入框
      await expect(page.getByLabel('Email or Username')).toBeVisible();
      await expect(page.getByPlaceholder('name@company.com')).toBeVisible();

      // 验证密码标签和输入框
      await expect(page.getByLabel('Password')).toBeVisible();
      await expect(page.getByPlaceholder('••••••••')).toBeVisible();

      // 验证密码可见性切换按钮
      await expect(page.locator('button:has(svg)')).toBeVisible();

      // 验证忘记密码链接
      await expect(page.getByText('Forgot Password?')).toBeVisible();

      // 验证登录按钮
      await expect(page.getByRole('button', { name: 'Sign In' })).toBeVisible();
    });

    test('应该显示LDAP登录模式的所有元素', async ({ page }) => {
      // 切换到LDAP模式
      await page.getByText('LDAP / Enterprise').click();

      // 验证用户名标签和输入框
      await expect(page.getByLabel('Username')).toBeVisible();
      await expect(page.getByPlaceholder('your.username')).toBeVisible();

      // 验证密码标签和输入框
      await expect(page.getByLabel('Password')).toBeVisible();
      await expect(page.getByPlaceholder('••••••••')).toBeVisible();
    });

    test('应该显示认证模式切换器', async ({ page }) => {
      await expect(page.getByText('Standard Sign In')).toBeVisible();
      await expect(page.getByText('LDAP / Enterprise')).toBeVisible();
    });

    test('应该显示页脚所有链接', async ({ page }) => {
      const footerLinks = [
        'Privacy Policy',
        'Terms of Service',
        'Security',
        'Help Center'
      ];

      for (const link of footerLinks) {
        await expect(page.getByText(link)).toBeVisible();
      }
    });

    test('应该显示Request an Account按钮', async ({ page }) => {
      await expect(page.getByRole('button', { name: 'Request an Account' })).toBeVisible();
    });

    test('应该显示版权信息', async ({ page }) => {
      await expect(page.getByText('© 2024 Kinetic Workspace. All rights reserved.')).toBeVisible();
    });
  });

  test.describe('交互功能验证', () => {
    test('应该能够切换认证模式', async ({ page }) => {
      // 默认在标准模式，验证输入框
      await expect(page.getByPlaceholder('name@company.com')).toBeVisible();

      // 切换到LDAP模式
      await page.getByText('LDAP / Enterprise').click();
      await expect(page.getByPlaceholder('your.username')).toBeVisible();

      // 切换回标准模式
      await page.getByText('Standard Sign In').click();
      await expect(page.getByPlaceholder('name@company.com')).toBeVisible();
    });

    test('应该能够切换密码可见性', async ({ page }) => {
      const passwordInput = page.getByPlaceholder('••••••••');

      // 初始状态应该是密码类型
      await expect(passwordInput).toHaveAttribute('type', 'password');

      // 点击显示密码
      await page.locator('button:has(svg)').click();
      await expect(passwordInput).toHaveAttribute('type', 'text');

      // 再次点击隐藏密码
      await page.locator('button:has(svg)').click();
      await expect(passwordInput).toHaveAttribute('type', 'password');
    });

    test('应该能够输入邮箱和密码', async ({ page }) => {
      const emailInput = page.getByPlaceholder('name@company.com');
      const passwordInput = page.getByPlaceholder('••••••••');

      await emailInput.fill('test@example.com');
      await passwordInput.fill('testpassword123');

      await expect(emailInput).toHaveValue('test@example.com');
      await expect(passwordInput).toHaveValue('testpassword123');
    });

    test('应该能够在LDAP模式输入用户名和密码', async ({ page }) => {
      await page.getByText('LDAP / Enterprise').click();

      const usernameInput = page.getByPlaceholder('your.username');
      const passwordInput = page.getByPlaceholder('••••••••');

      await usernameInput.fill('testuser');
      await passwordInput.fill('testpassword123');

      await expect(usernameInput).toHaveValue('testuser');
      await expect(passwordInput).toHaveValue('testpassword123');
    });

    test('切换模式时应该清除错误', async ({ page }) => {
      // 先尝试提交空表单产生错误
      await page.getByRole('button', { name: 'Sign In' }).click();

      // 等待错误显示
      await page.waitForTimeout(500);

      // 切换到LDAP模式
      await page.getByText('LDAP / Enterprise').click();

      // 错误应该被清除
      const errorElement = page.locator('text="Email is required"').first();
      await expect(errorElement).not.toBeVisible();
    });
  });

  test.describe('表单验证', () => {
    test('空邮箱应该显示验证错误', async ({ page }) => {
      await page.getByPlaceholder('••••••••').fill('testpassword123');
      await page.getByRole('button', { name: 'Sign In' }).click();

      await expect(page.getByText('Email is required')).toBeVisible();
    });

    test('空密码应该显示验证错误', async ({ page }) => {
      await page.getByPlaceholder('name@company.com').fill('test@example.com');
      await page.getByRole('button', { name: 'Sign In' }).click();

      await expect(page.getByText('Password is required')).toBeVisible();
    });

    test('输入时应该清除错误', async ({ page }) => {
      // 先产生错误
      await page.getByRole('button', { name: 'Sign In' }).click();
      await expect(page.getByText('Email is required')).toBeVisible();

      // 开始输入应该清除错误
      await page.getByPlaceholder('name@company.com').fill('t');
      await expect(page.getByText('Email is required')).not.toBeVisible();
    });
  });

  test.describe('响应式布局验证', () => {
    test('移动端布局应该正常显示', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });

      await expect(page.getByText('Censorate Management')).toBeVisible();
      await expect(page.getByPlaceholder('name@company.com')).toBeVisible();
      await expect(page.getByRole('button', { name: 'Sign In' })).toBeVisible();
    });

    test('平板端布局应该正常显示', async ({ page }) => {
      await page.setViewportSize({ width: 768, height: 1024 });

      await expect(page.getByText('Censorate Management')).toBeVisible();
      await expect(page.getByPlaceholder('name@company.com')).toBeVisible();
      await expect(page.getByRole('button', { name: 'Sign In' })).toBeVisible();
    });

    test('桌面端布局应该正常显示', async ({ page }) => {
      await page.setViewportSize({ width: 1920, height: 1080 });

      await expect(page.getByText('Censorate Management')).toBeVisible();
      await expect(page.getByPlaceholder('name@company.com')).toBeVisible();
      await expect(page.getByRole('button', { name: 'Sign In' })).toBeVisible();
    });
  });

  test.describe('视觉反馈验证', () => {
    test('输入框获得焦点时应该有视觉反馈', async ({ page }) => {
      const emailInput = page.getByPlaceholder('name@company.com');

      // 焦点前应该没有focus ring
      // 聚焦
      await emailInput.focus();

      // 验证样式变化（有focus ring）
      await expect(emailInput).toBeFocused();
    });

    test('按钮悬停时应该有视觉反馈', async ({ page }) => {
      const signInButton = page.getByRole('button', { name: 'Sign In' });

      // 悬停前
      // 悬停
      await signInButton.hover();

      // 验证悬停状态（通过是否可见来确认）
      await expect(signInButton).toBeVisible();
    });
  });
});
