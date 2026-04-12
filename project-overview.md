# Censorate Management System - 项目总览

## 项目概述

Censorate 是一个 AI 原生的需求管理系统，采用 "AI 第一，人类检查" 的理念，通过项目为组织单位管理需求的全生命周期。

## 技术架构

### 后端架构

**技术栈：**
- Python 3.10+
- FastAPI - Web 框架
- SQLAlchemy - ORM
- PostgreSQL - 数据库
- Pydantic - 数据验证
- Uvicorn - ASGI 服务器

**核心功能模块：**

1. **项目管理** - 项目创建、更新、删除
2. **需求管理** - 需求的创建、状态跟踪、AI 分析
3. **团队管理** - 团队成员和 AI 代理管理
4. **任务管理** - 任务分配、跟踪
5. **测试用例管理** - 测试用例的创建和执行
6. **集成功能** - 飞书文档、GitHub、GitLab 集成

**API 文档：**
- 访问地址：http://localhost:8026/docs
- 使用 Swagger UI 提供完整的 API 文档和测试界面

### 前端架构

**技术栈：**
- Next.js 14 (React 框架)
- TypeScript
- Tailwind CSS (样式框架)
- shadcn/ui (UI 组件库)
- Zustand (状态管理)
- React DnD (拖放功能)

**核心功能：**

1. **看板视图** - 需求的可视化管理，支持拖放操作
2. **团队管理** - 团队成员和 AI 代理的详细信息展示
3. **需求详情** - 完整的需求信息和历史记录
4. **AI 代理** - 智能代理的技能和内存管理

**运行状态：**
- 开发服务器：http://localhost:3000
- 构建状态：已成功构建
- 依赖：已安装完成

## 项目进度

### 已完成

#### 后端功能
- ✅ 核心基础设施（数据库连接、依赖注入、配置管理）
- ✅ 项目管理 API 端点
- ✅ 需求管理 API 端点（创建、更新、删除、查询）
- ✅ 团队管理 API 端点
- ✅ 任务管理 API 端点
- ✅ 测试用例管理 API 端点
- ✅ GitHub 集成服务
- ✅ 飞书文档集成
- ✅ 分析服务（需求状态机）
- ✅ 响应拦截器和异常处理

#### 前端功能
- ✅ 项目初始化（Next.js 14 + TypeScript + Tailwind）
- ✅ 核心布局组件（Header、Sidebar、Layout）
- ✅ 状态管理（Zustand 存储）
- ✅ 看板组件（Drag & Drop、Swimlanes、Cards）
- ✅ 团队管理组件（Member Card、Agent Card、Add Dialogs）
- ✅ 需求详情视图
- ✅ 响应式设计实现
- ✅ API 客户端集成
- ✅ UI 组件库集成（shadcn/ui）

### 待完成

#### 后端功能
- 🔄 自动化服务实现
- 🔄 AI Agent 技能系统
- 🔄 添加日志中间件和压缩
- 🔄 完善测试用例 API 端点

#### 前端功能
- 🔄 待办列表视图
- 🔄 分析仪表板
- 🔄 项目设置页面
- 🔄 自定义钩子和工具函数
- 🔄 Deep Agents 集成
- 🔄 更多优化和测试

## 快速启动指南

### 后端启动

```bash
# 进入后端目录
cd /Users/moya/Workspace/stichdemo/backend

# 安装依赖
pip install -r requirements.txt

# 启动服务器（端口 8026）
python main.py
```

### 前端启动

```bash
# 进入前端目录
cd /Users/moya/Workspace/stichdemo/frontend

# 安装依赖
npm install

# 启动开发服务器（端口 3000）
npm run dev
```

### 访问应用

- 前端界面：http://localhost:3000
- 后端 API 文档：http://localhost:8026/docs

## 项目结构

```
stichdemo/
├── backend/                 # FastAPI 后端服务
│   ├── main.py             # 应用入口点
│   ├── requirements.txt    # Python 依赖
│   └── app/
│       ├── api/            # API 路由
│       ├── core/           # 核心功能
│       ├── models/         # 数据模型
│       ├── schemas/        # 请求/响应模式
│       ├── services/       # 业务逻辑服务
│       └── utils/          # 工具函数
├── frontend/               # Next.js 前端应用
│   ├── package.json        # npm 依赖
│   ├── next.config.js      # Next.js 配置
│   ├── tailwind.config.ts  # Tailwind 配置
│   └── app/
│       ├── components/     # React 组件
│       ├── lib/            # 工具库
│       ├── stores/         # 状态管理
│       └── pages/          # 页面组件
└── docs/                   # 项目文档
```

## 数据库连接

**数据库：** PostgreSQL
**端口：** 5432
**连接字符串：** postgresql://stratos_user:stratos_password@localhost:5432/stratos_db

## 重要更新

**2024-04-11:**
- 后端端口已更新为 8026（之前为 8000）
- 前端 API 基础 URL 已相应更新
- 环境变量文件已创建（.env.local）

## 注意事项

1. 确保后端服务在端口 8026 上运行
2. 确保 PostgreSQL 数据库已正确设置
3. 前端和后端需要同时运行才能正常工作
4. 开发模式下支持实时刷新
