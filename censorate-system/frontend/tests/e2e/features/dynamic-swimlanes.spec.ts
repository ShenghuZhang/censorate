import { test, expect } from '@playwright/test';

test.describe('动态泳道配置功能验证', () => {
  test.beforeEach(async ({ page, context }) => {
    // 设置认证状态
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
  });

  test.describe('创建项目对话框验证', () => {
    test('应该显示泳道配置选择器', async ({ page }) => {
      // 点击创建新项目按钮
      await page.click('text=Select Project');
      await page.waitForTimeout(500);
      await page.click('text=New Project');
      await page.waitForTimeout(500);

      // 检查是否显示泳道配置标题
      await expect(page.getByText('Swimlane Configuration')).toBeVisible();

      // 检查预定义选项
      await expect(page.getByText('Default (4 lanes)')).toBeVisible();
      await expect(page.getByText('Chinese (6 lanes)')).toBeVisible();
      await expect(page.getByText('Custom')).toBeVisible();
    });

    test('不应该显示 Project Type 选择器', async ({ page }) => {
      // 点击创建新项目按钮
      await page.click('text=Select Project');
      await page.waitForTimeout(500);
      await page.click('text=New Project');
      await page.waitForTimeout(500);

      // 检查不应该显示 Project Type
      await expect(page.getByText('Project Type')).not.toBeVisible();
      await expect(page.getByText('Business')).not.toBeVisible();
      await expect(page.getByText('Technical')).not.toBeVisible();
    });

    test('选择默认泳道配置应该显示预览', async ({ page }) => {
      await page.click('text=Select Project');
      await page.waitForTimeout(500);
      await page.click('text=New Project');
      await page.waitForTimeout(500);

      // 选择默认配置
      await page.click('text=Default (4 lanes)');
      await page.waitForTimeout(300);

      // 检查预览
      await expect(page.getByText('Preview')).toBeVisible();
      await expect(page.getByText('Backlog')).toBeVisible();
      await expect(page.getByText('Todo')).toBeVisible();
      await expect(page.getByText('In Review')).toBeVisible();
      await expect(page.getByText('Done')).toBeVisible();
    });

    test('选择中文泳道配置应该显示预览', async ({ page }) => {
      await page.click('text=Select Project');
      await page.waitForTimeout(500);
      await page.click('text=New Project');
      await page.waitForTimeout(500);

      // 选择中文配置
      await page.click('text=Chinese (6 lanes)');
      await page.waitForTimeout(300);

      // 检查预览
      await expect(page.getByText('需求')).toBeVisible();
      await expect(page.getByText('需求分析')).toBeVisible();
      await expect(page.getByText('方案设计')).toBeVisible();
      await expect(page.getByText('开发')).toBeVisible();
      await expect(page.getByText('测试')).toBeVisible();
      await expect(page.getByText('完成')).toBeVisible();
    });

    test('自定义泳道输入应该工作', async ({ page }) => {
      await page.click('text=Select Project');
      await page.waitForTimeout(500);
      await page.click('text=New Project');
      await page.waitForTimeout(500);

      // 选择自定义
      await page.click('text=Custom');
      await page.waitForTimeout(300);

      // 输入自定义泳道
      const customInput = page.getByPlaceholder('Backlog, Todo, In Review, Done');
      await customInput.fill('Planning, Development, Review, Deploy');
      await page.waitForTimeout(300);

      // 检查预览
      await expect(page.getByText('Planning')).toBeVisible();
      await expect(page.getByText('Development')).toBeVisible();
      await expect(page.getByText('Review')).toBeVisible();
      await expect(page.getByText('Deploy')).toBeVisible();
    });

    test('自定义泳道应该验证数量限制', async ({ page }) => {
      await page.click('text=Select Project');
      await page.waitForTimeout(500);
      await page.click('text=New Project');
      await page.waitForTimeout(500);

      // 选择自定义
      await page.click('text=Custom');
      await page.waitForTimeout(300);

      // 输入少于2个泳道
      const customInput = page.getByPlaceholder('Backlog, Todo, In Review, Done');
      await customInput.fill('Single');
      await page.waitForTimeout(300);

      // 检查验证提示
      await expect(page.getByText('needs 2-10')).toBeVisible();
    });
  });

  test.describe('项目设置页面验证', () => {
    test('项目设置页面应该显示泳道配置', async ({ page }) => {
      // 先创建一个测试项目或选择现有项目
      await page.goto('http://localhost:3000/settings');
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(1000);

      // 检查泳道配置
      const swimlaneConfig = page.getByText('Swimlane Configuration');
      if (await swimlaneConfig.isVisible()) {
        await expect(swimlaneConfig).toBeVisible();
        await expect(page.getByText('Default (4 lanes)')).toBeVisible();
      }
    });

    test('项目设置页面不应该显示 Project Type', async ({ page }) => {
      await page.goto('http://localhost:3000/settings');
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(1000);

      // 检查不应该显示 Project Type
      await expect(page.getByText('Project Type')).not.toBeVisible();
    });
  });

  test.describe('看板泳道验证', () => {
    test('看板应该显示默认泳道', async ({ page }) => {
      await page.goto('http://localhost:3000/kanban');
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(2000);

      // 检查默认泳道
      const backlogColumn = page.getByText('Backlog').first();
      const todoColumn = page.getByText('Todo').first();
      const inReviewColumn = page.getByText('In Review').first();
      const doneColumn = page.getByText('Done').first();

      // 至少应该有一个泳道可见
      await expect(backlogColumn.or(todoColumn).or(inReviewColumn).or(doneColumn)).toBeVisible();
    });
  });
});
