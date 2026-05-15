# Skill Manager Daemon

Skill Manager 是一个用于同步 Censorate Hub 技能到 Hermes 本地存储的 sidecar 服务。

## 功能特性

- **Webhook 模式**: 实时响应 agent 技能变更
- **轮询模式**: 作为兜底机制定期同步
- **混合模式**: 同时启用 webhook 和轮询（推荐）
- **单次同步**: 手动触发一次同步

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `CENSORATE_URL` | Censorate API 地址 | `http://localhost:8216/api/v1` |
| `HERMES_API_SERVER_KEY` | Agent API Key（必填） | - |
| `HERMES_HOME` | hermes_data 目录路径 | `./hermes_data` |
| `SKILL_MANAGER_PORT` | HTTP 服务端口 | `8765` |
| `SKILL_MANAGER_HOST` | HTTP 服务监听地址 | `0.0.0.0` |
| `SKILL_MANAGER_INTERVAL` | 轮询间隔（秒） | `300` |

## 使用方法

### 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 单次同步
python skill_manager.py --api-key <your-api-key>

# 轮询模式（每5分钟同步）
python skill_manager.py --daemon --api-key <your-api-key>

# HTTP 服务模式（支持 webhook）
python skill_manager.py --server --api-key <your-api-key>

# 混合模式（推荐）
python skill_manager.py --server --daemon --api-key <your-api-key>
```

### Docker 运行

```bash
# 构建镜像
docker build -t censorate-skill-manager .

# 运行容器
docker run -d \
  -e HERMES_API_SERVER_KEY=<your-api-key> \
  -e CENSORATE_URL=http://host.docker.internal:8216/api/v1 \
  -v ./hermes_data:/opt/data \
  -p 8765:8765 \
  censorate-skill-manager
```

## HTTP API

### 健康检查

```bash
GET /health
```

### 查看状态

```bash
GET /status
```

### 手动触发同步

```bash
POST /sync
```

### Agent 更新 Webhook

```bash
POST /webhook/agent-updated
Content-Type: application/json

{
  "agent_id": "xxx",
  "event_type": "capabilities_updated"
}
```

## 目录结构

```
hermes_data/
├── skills/              # 技能安装目录
│   ├── .hub/
│   │   └── lock.json   # Hermes 锁文件
│   └── <category>/
│       └── <skill>/
└── .skill_manager_state.json  # Skill Manager 状态文件
```
