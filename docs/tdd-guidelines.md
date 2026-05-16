# TDD 开发规范

## 核心原则

**铁律：没有失败的测试就不能写生产代码**

```
RED → GREEN → REFACTOR
```

- **RED**: 先写失败的测试
- **GREEN**: 写最少代码让测试通过
- **REFACTOR**: 重构，保持测试通过

## 什么时候必须用TDD

✅ **必须使用：**
- 新功能开发
- Bug修复
- 重构
- 行为变更

❌ **例外（需要确认）：**
- 一次性原型
- 生成的代码
- 配置文件

## RED-GREEN-REFACTOR 流程

### 1. RED - 写失败的测试

写一个最小化的测试，展示期望的行为。

**好的测试：**
```python
def test_rejects_empty_email():
    result = submit_form(email='')
    assert result.error == 'Email required'
```

**坏的测试：**
```python
def test_form_works():
    mock = Mock()
    submit_form(mock)
    assert mock.called
```

**要求：**
- 只测试一个行为
- 名称清晰描述行为
- 尽量用真实代码（除非迫不得已不用mock）

### 2. Verify RED - 看它失败

**强制要求，不能跳过。**

```bash
# 后端
cd censorate-system/backend
python -m pytest tests/unit/test_file.py -v

# 前端
cd censorate-system/frontend
npm run test:e2e
```

确认：
- 测试失败（不是错误）
- 失败信息是预期的
- 失败是因为功能缺失（不是拼写错误）

**测试通过了？** 你在测试已有行为，修复测试。

**测试报错？** 修复错误，重跑直到正确失败。

### 3. GREEN - 最少代码

写最简单的代码让测试通过。

**好的代码：**
```python
def submit_form(email):
    if not email.strip():
        return {'error': 'Email required'}
```

**坏的代码：**
```python
def submit_form(email, options=None):
    # YAGNI - 不要过度设计
```

不要添加额外功能，不要重构其他代码，不要"改进"超出测试范围。

### 4. Verify GREEN - 看它通过

**强制要求。**

确认：
- 测试通过
- 其他测试仍然通过
- 输出干净（没有错误、警告）

**测试失败？** 修复代码，不要修改测试。

**其他测试失败？** 立即修复。

### 5. REFACTOR - 清理

只能在 green 之后：
- 消除重复
- 改进命名
- 提取辅助函数

保持测试通过。不要添加新行为。

### 重复

下一个功能的下一个失败测试。

## 项目结构

```
censorate-system/
├── backend/
│   ├── tests/
│   │   ├── unit/          # 单元测试
│   │   ├── integration/   # 集成测试
│   │   └── e2e/          # 端到端测试
│   └── ...
└── frontend/
    ├── tests/
    │   └── e2e/          # Playwright E2E测试
    └── ...
```

## 测试命名规范

### 后端（Python）

**测试文件：** `test_<module>.py`

**测试类：** `Test<Feature>`

**测试方法：** `test_<behavior_under_test>`

**示例：**
```python
# tests/unit/test_auth_service.py
class TestAuthService:
    def test_login_creates_user_when_not_found(self):
        ...
```

### 前端（TypeScript）

**测试文件：** `<feature>.spec.ts`

**测试方法：** `should <behavior>` 或描述性名称

**示例：**
```typescript
// tests/e2e/login.spec.ts
test('should allow user to login and access dashboard', async () => {
    ...
});
```

## 好测试的特征

| 特征 | 好 | 坏 |
|------|-----|-----|
| **最小化** | 一个测试一件事。名称里有"and"？拆分。 | `test('validates email and domain')` |
| **清晰** | 名称描述行为 | `test('test1')` |
| **显示意图** | 展示期望的API | 模糊代码应该做什么 |

## 为什么顺序很重要

**"我之后写测试来验证"**

之后写的测试会立即通过。立即通过什么都证明不了：
- 可能测试了错误的东西
- 可能测试了实现而不是行为
- 可能漏掉了你忘记的边界情况
- 你从来没看到它抓住bug

测试优先迫使你看到测试失败，证明它确实测试了什么。

## 验证清单

标记工作完成前：

- [ ] 每个新函数/方法都有测试
- [ ] 实现前看到每个测试失败
- [ ] 每个测试因预期原因失败（功能缺失，不是拼写错误）
- [ ] 写最少代码让每个测试通过
- [ ] 所有测试通过
- [ ] 输出干净（没有错误、警告）
- [ ] 测试用真实代码（除非迫不得已不用mock）
- [ ] 覆盖边界情况和错误处理

## 常见借口反驳

| 借口 | 现实 |
|------|------|
| "太简单不用测试" | 简单代码也会坏。测试30秒。 |
| "我之后测试" | 立即通过的测试什么都证明不了。 |
| "已经手动测试了" | 手动不系统。没记录，不能重跑。 |
| "删除X小时工作浪费" | 沉没成本。保留不可信代码是技术债务。 |
| "保留作为参考" | 你会参考它。那是测试之后。删除就是删除。 |
| "需要先探索" | 可以。扔掉探索，用TDD开始。 |
| "TDD会让我变慢" | TDD比调试快。务实=测试优先。 |

## 红色标志 - 停止并重来

- 测试前写了代码
- 实现后加测试
- 测试立即通过
- 不能解释为什么测试失败
- "之后"加测试
- 找借口"就这一次"
- "我已经手动测试了"
- "测试之后达到相同目标"
- "是精神不是仪式"
- "保留作为参考"或"适配现有代码"
- "已经花了X小时，删除浪费"
- "TDD太教条，我要务实"
- "这不同因为..."

**所有这些都意味着：删除代码。用TDD重来。**

## Bug修复流程

**Bug:** 空邮箱被接受

**RED**
```python
def test_rejects_empty_email():
    result = submit_form(email='')
    assert result.error == 'Email required'
```

**Verify RED**
```bash
$ python -m pytest tests/unit/test_form.py -v
FAIL: expected 'Email required', got undefined
```

**GREEN**
```python
def submit_form(email):
    if not email.strip():
        return {'error': 'Email required'}
```

**Verify GREEN**
```bash
$ python -m pytest tests/unit/test_form.py -v
PASS
```

**REFACTOR**
如果需要，为多个字段提取验证。

## 项目特定命令

### 运行后端测试

```bash
# 运行所有后端测试
cd censorate-system/backend
python -m pytest tests/ -v

# 运行特定测试
python -m pytest tests/unit/test_auth_service.py -v
```

### 运行前端测试

```bash
# 运行E2E测试
cd censorate-system/frontend
npm run test:e2e

# 运行带UI的测试
npm run test:e2e:ui
```

## 最终规则

```
生产代码 → 测试存在且先失败
否则 → 不是TDD
```

没有例外，除非得到许可。
