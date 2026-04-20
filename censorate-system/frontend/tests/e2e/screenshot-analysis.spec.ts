import { test, expect } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

// 创建截图目录
const screenshotDir = path.join(__dirname, '../../artifacts/screenshots');
if (!fs.existsSync(screenshotDir)) {
  fs.mkdirSync(screenshotDir, { recursive: true });
}

test.describe('页面截图分析', () => {
  test('1. 登录页面截图分析', async ({ page }) => {
    await page.goto('http://localhost:3000/login');
    await page.waitForLoadState('networkidle');

    // 全屏截图
    await page.screenshot({
      path: path.join(screenshotDir, 'login-page-full.png'),
      fullPage: true
    });

    // 可视区域截图
    await page.screenshot({
      path: path.join(screenshotDir, 'login-page-viewport.png')
    });

    // 分析页面元素
    const pageAnalysis = {
      url: page.url(),
      title: await page.title(),
      hasLogo: await page.locator('h1:has-text("Censorate Management")').count() > 0,
      hasEmailInput: await page.getByPlaceholder('name@company.com').count() > 0,
      hasPasswordInput: await page.getByPlaceholder('••••••••').count() > 0,
      hasSubmitButton: await page.locator('button[type="submit"]').count() > 0,
      hasLDAPButton: await page.getByText('LDAP / Enterprise').count() > 0,
      footerLinks: {
        forgotPassword: await page.getByText('Forgot Password?').count() > 0,
        privacy: await page.getByText('Privacy Policy').count() > 0,
        terms: await page.getByText('Terms of Service').count() > 0,
        security: await page.getByText('Security').count() > 0,
        helpCenter: await page.getByText('Help Center').count() > 0
      }
    };

    // 保存分析结果
    fs.writeFileSync(
      path.join(screenshotDir, 'login-page-analysis.json'),
      JSON.stringify(pageAnalysis, null, 2)
    );

    console.log('✅ 登录页面分析完成');
    console.log('分析结果:', pageAnalysis);

    // 验证关键元素存在
    await expect(page.locator('h1:has-text("Censorate Management")')).toBeVisible();
  });

  test('2. 登录页面 - 标准模式', async ({ page }) => {
    await page.goto('http://localhost:3000/login');
    await page.waitForLoadState('networkidle');

    await page.screenshot({
      path: path.join(screenshotDir, 'login-standard-mode.png')
    });
  });

  test('3. 登录页面 - LDAP模式', async ({ page }) => {
    await page.goto('http://localhost:3000/login');
    await page.waitForLoadState('networkidle');

    await page.click('button:has-text("LDAP / Enterprise")');
    await page.waitForTimeout(500);

    await page.screenshot({
      path: path.join(screenshotDir, 'login-ldap-mode.png')
    });
  });

  test('4. 主页截图分析', async ({ page }) => {
    await page.goto('http://localhost:3000/login');

    // 尝试登录
    await page.getByPlaceholder('name@company.com').fill('test@example.com');
    await page.getByPlaceholder('••••••••').fill('password123');
    await page.locator('button[type="submit"]').click();
    await page.waitForTimeout(2000);

    // 如果重定向到主页
    await page.goto('http://localhost:3000');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    await page.screenshot({
      path: path.join(screenshotDir, 'home-page.png'),
      fullPage: true
    });

    const homeAnalysis = {
      url: page.url(),
      title: await page.title(),
      hasWelcome: await page.getByText('Welcome').count() > 0,
      hasKanbanButton: await page.getByText('Go to Kanban Board').count() > 0,
      hasTeamButton: await page.getByText('Go to Team Management').count() > 0
    };

    fs.writeFileSync(
      path.join(screenshotDir, 'home-page-analysis.json'),
      JSON.stringify(homeAnalysis, null, 2)
    );

    console.log('✅ 主页分析完成');
  });

  test('5. 看板页面截图分析', async ({ page }) => {
    await page.goto('http://localhost:3000/kanban');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    await page.screenshot({
      path: path.join(screenshotDir, 'kanban-page-full.png'),
      fullPage: true
    });

    await page.screenshot({
      path: path.join(screenshotDir, 'kanban-page-viewport.png')
    });

    const kanbanAnalysis = {
      url: page.url(),
      title: await page.title(),
      hasTitle: await page.getByText('Project Kanban').count() > 0,
      hasDescription: await page.getByText('Manage requirements and track progress').count() > 0
    };

    fs.writeFileSync(
      path.join(screenshotDir, 'kanban-page-analysis.json'),
      JSON.stringify(kanbanAnalysis, null, 2)
    );

    console.log('✅ 看板页面分析完成');
  });

  test('6. 团队管理页面截图分析', async ({ page }) => {
    await page.goto('http://localhost:3000/team');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    await page.screenshot({
      path: path.join(screenshotDir, 'team-page-full.png'),
      fullPage: true
    });

    await page.screenshot({
      path: path.join(screenshotDir, 'team-page-viewport.png')
    });

    const teamAnalysis = {
      url: page.url(),
      title: await page.title(),
      hasTitle: await page.getByText('Team Members').count() > 0,
      hasDescription: await page.getByText('Manage your team and AI agents').count() > 0,
      hasAddButton: await page.getByText('Add AI Agent').count() > 0
    };

    fs.writeFileSync(
      path.join(screenshotDir, 'team-page-analysis.json'),
      JSON.stringify(teamAnalysis, null, 2)
    );

    console.log('✅ 团队管理页面分析完成');
  });

  test('7. 添加 Agent 对话框截图分析', async ({ page }) => {
    await page.goto('http://localhost:3000/team');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    // 点击添加按钮
    await page.click('button:has-text("Add AI Agent")');
    await page.waitForTimeout(1000);

    await page.screenshot({
      path: path.join(screenshotDir, 'add-agent-dialog.png')
    });

    console.log('✅ 添加 Agent 对话框分析完成');
  });

  test('8. 响应式设计截图 - 移动端', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('http://localhost:3000/login');
    await page.waitForLoadState('networkidle');

    await page.screenshot({
      path: path.join(screenshotDir, 'mobile-login.png')
    });

    await page.goto('http://localhost:3000/kanban');
    await page.waitForTimeout(1000);
    await page.screenshot({
      path: path.join(screenshotDir, 'mobile-kanban.png')
    });
  });

  test('9. 响应式设计截图 - 平板端', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto('http://localhost:3000/login');
    await page.waitForLoadState('networkidle');

    await page.screenshot({
      path: path.join(screenshotDir, 'tablet-login.png')
    });

    await page.goto('http://localhost:3000/team');
    await page.waitForTimeout(1000);
    await page.screenshot({
      path: path.join(screenshotDir, 'tablet-team.png')
    });
  });

  test('10. 响应式设计截图 - 桌面端', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.goto('http://localhost:3000/login');
    await page.waitForLoadState('networkidle');

    await page.screenshot({
      path: path.join(screenshotDir, 'desktop-login.png')
    });

    await page.goto('http://localhost:3000/kanban');
    await page.waitForTimeout(1000);
    await page.screenshot({
      path: path.join(screenshotDir, 'desktop-kanban.png')
    });
  });

  test('生成分析报告', async () => {
    // 生成完整的分析报告
    const report = `
# 页面截图分析报告

**生成时间**: ${new Date().toISOString()}

## 截图目录

所有截图保存在: \`frontend/artifacts/screenshots/\`

## 截图列表

### 登录页面
- \`login-page-full.png\` - 完整登录页面
- \`login-page-viewport.png\` - 登录页面可视区域
- \`login-standard-mode.png\` - 标准登录模式
- \`login-ldap-mode.png\` - LDAP登录模式

### 主页
- \`home-page.png\` - 主页完整截图

### 看板页面
- \`kanban-page-full.png\` - 看板页面完整截图
- \`kanban-page-viewport.png\` - 看板页面可视区域

### 团队管理页面
- \`team-page-full.png\` - 团队管理页面完整截图
- \`team-page-viewport.png\` - 团队管理页面可视区域
- \`add-agent-dialog.png\` - 添加Agent对话框

### 响应式设计
- \`mobile-login.png\` - 移动端登录页
- \`mobile-kanban.png\` - 移动端看板页
- \`tablet-login.png\` - 平板端登录页
- \`tablet-team.png\` - 平板端团队管理页
- \`desktop-login.png\` - 桌面端登录页
- \`desktop-kanban.png\` - 桌面端看板页

## 分析文件

- \`login-page-analysis.json\` - 登录页分析数据
- \`home-page-analysis.json\` - 主页分析数据
- \`kanban-page-analysis.json\` - 看板页分析数据
- \`team-page-analysis.json\` - 团队管理页分析数据

---

报告生成完成！
`;

    fs.writeFileSync(
      path.join(screenshotDir, 'SCREENSHOT_REPORT.md'),
      report
    );

    console.log('✅ 分析报告生成完成');
  });
});
