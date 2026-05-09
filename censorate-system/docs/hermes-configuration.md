# Hermes 配置整理建议

## 目标

- 只保留一个 Hermes 运行目录：`./hermes_data`
- `config.yaml` 只存非敏感配置
- 所有密钥只放在 `hermes_data/.env` 或宿主机环境变量
- 不把 `auth.json`、`.env`、`state.db`、日志和缓存提交进仓库

## 推荐目录职责

- `docker-compose.yml`
  - 负责声明 Hermes 容器、端口和环境变量映射
- `.env`
  - 负责 Docker Compose 的变量注入
- `hermes_data/config.yaml`
  - 负责模型、工具、审批、显示和安全策略等非敏感配置
- `hermes_data/.env`
  - 负责 `API_SERVER_KEY`、`DEEPSEEK_API_KEY` 这类敏感信息

## 不建议继续保留的做法

- 在 `docker-compose.yml` 里写死 `API_SERVER_KEY`
- 在启动命令里 `echo` 追加 secret 到 `/opt/data/.env`
- 同时维护 `./hermes_data` 和 `./backend/hermes_data` 两套状态目录
- 把 `auth.json`、`state.db`、`logs/` 当作项目源码的一部分

## 初始化步骤

1. 复制 `backend/hermes.config.example.yaml` 到 `hermes_data/config.yaml`
2. 创建 `hermes_data/.env`
3. 在 `hermes_data/.env` 中填写最少配置：

```env
API_SERVER_KEY=replace-with-a-long-random-secret
DEEPSEEK_API_KEY=replace-with-your-provider-key
```

4. 在项目根目录 `.env` 中填写 Compose 变量
5. 启动 `docker compose up -d hermes`

## 安全基线

- `HERMES_GATEWAY_ALLOW_ALL_USERS=false`
- `API_SERVER_KEY` 使用至少 32 位随机字符串
- `security.redact_secrets=true`
- `security.tirith_fail_open=false`
- 生产环境不要暴露 `8642` 到公网；如需访问，优先走内网或反向代理鉴权
