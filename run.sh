#!/bin/bash

# Censorate Management System - 项目启动脚本
# 作者: Claude Code
# 日期: 2024-04-11

echo "============================================="
echo "Censorate Management System - 项目启动脚本"
echo "============================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 项目根目录 - 获取脚本所在目录的绝对路径
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="${SCRIPT_DIR}/censorate-system"

# 验证项目目录是否存在
if [ ! -d "${PROJECT_ROOT}" ]; then
    echo -e "${RED}错误: 项目目录不存在: ${PROJECT_ROOT}${NC}"
    echo -e "${YELLOW}当前脚本目录: ${SCRIPT_DIR}${NC}"
    exit 1
fi

if [ ! -d "${PROJECT_ROOT}/backend" ]; then
    echo -e "${RED}错误: 后端目录不存在: ${PROJECT_ROOT}/backend${NC}"
    exit 1
fi

if [ ! -d "${PROJECT_ROOT}/frontend" ]; then
    echo -e "${RED}错误: 前端目录不存在: ${PROJECT_ROOT}/frontend${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 项目目录验证通过${NC}"
echo "  - 项目根目录: ${PROJECT_ROOT}"
echo ""

# 检查命令是否可用
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}错误: ${1} 命令未找到${NC}"
        exit 1
    fi
}

# 检查端口是否被占用
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${YELLOW}警告: 端口 ${1} 正在被占用${NC}"
        echo -e "${YELLOW}正在尝试终止占用端口的进程...${NC}"
        pkill -f "python.*main.py" 2>/dev/null
        pkill -f "npm.*dev" 2>/dev/null
        sleep 2
    fi
}

# 检查 Node.js 版本
check_node_version() {
    NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -lt 18 ]; then
        echo -e "${RED}错误: 需要 Node.js 18 或更高版本，当前版本: ${NODE_VERSION}${NC}"
        exit 1
    fi
}

# 检查 Python 版本
check_python_version() {
    if ! python3 --version &> /dev/null; then
        echo -e "${RED}错误: Python 3 未找到${NC}"
        exit 1
    fi

    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1)
    if [ "$PYTHON_VERSION" -lt 3 ]; then
        echo -e "${RED}错误: 需要 Python 3.10 或更高版本${NC}"
        exit 1
    fi
}

# 检查并创建虚拟环境
setup_python_env() {
    cd "${PROJECT_ROOT}/backend"

    if [ ! -d "venv" ]; then
        echo -e "${GREEN}正在创建 Python 虚拟环境...${NC}"
        python3 -m venv venv
    fi

    echo -e "${GREEN}正在激活虚拟环境...${NC}"
    source venv/bin/activate

    echo -e "${GREEN}正在安装 Python 依赖...${NC}"
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo -e "${RED}错误: 依赖安装失败${NC}"
        exit 1
    fi
}

# 安装前端依赖
setup_frontend() {
    cd "${PROJECT_ROOT}/frontend"

    if [ ! -d "node_modules" ]; then
        echo -e "${GREEN}正在安装前端依赖...${NC}"
        npm install
        if [ $? -ne 0 ]; then
            echo -e "${RED}错误: 前端依赖安装失败${NC}"
            exit 1
        fi
    else
        echo -e "${GREEN}✓ 前端依赖已安装${NC}"
    fi
}

# 启动后端服务
start_backend() {
    cd "${PROJECT_ROOT}/backend"

    echo -e "${GREEN}正在启动后端服务...${NC}"
    echo -e "${YELLOW}后端服务信息:${NC}"
    echo "  - 地址: http://localhost:8216"
    echo "  - API 文档: http://localhost:8216/docs"
    echo "  - 数据模型: PostgreSQL"

    source venv/bin/activate
    python main.py &
    BACKEND_PID=$!
    echo $BACKEND_PID > backend.pid

    echo -e "${GREEN}后端服务已启动 (PID: ${BACKEND_PID})${NC}"
}

# 启动前端服务
start_frontend() {
    cd "${PROJECT_ROOT}/frontend"

    echo -e "\n${GREEN}正在启动前端服务...${NC}"
    echo -e "${YELLOW}前端服务信息:${NC}"
    echo "  - 地址: http://localhost:3000"
    echo "  - 框架: Next.js 16"
    echo "  - 状态: 已成功构建"

    npm run dev &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > frontend.pid

    echo -e "${GREEN}前端服务已启动 (PID: ${FRONTEND_PID})${NC}"
}

# 启动 skill-manager daemon（如果配置了）
start_daemon_if_configured() {
    # 总是启动 skill-manager（现在不需要 API key 了）
    echo -e "${GREEN}正在启动 Skill-Manager Daemon...${NC}"
    start_daemon
}

# 检查服务是否成功启动
check_services() {
    echo -e "\n${GREEN}正在检查服务启动状态...${NC}"

    # 等待服务启动
    sleep 5

    # 检查后端服务
    if curl -f http://localhost:8216/docs >/dev/null 2>&1; then
        echo -e "${GREEN}✅ 后端服务已成功启动${NC}"
    else
        echo -e "${RED}❌ 后端服务启动失败${NC}"
        return 1
    fi

    # 检查前端服务
    if curl -f http://localhost:3000 >/dev/null 2>&1; then
        echo -e "${GREEN}✅ 前端服务已成功启动${NC}"
    else
        echo -e "${RED}❌ 前端服务启动失败${NC}"
        return 1
    fi

    # 检查 skill-manager
    if curl -f http://localhost:${SKILL_MANAGER_PORT:-8765}/health >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Skill-Manager Daemon 已成功启动${NC}"
    else
        echo -e "${YELLOW}⚠️  Skill-Manager Daemon 可能未完全启动，请稍后检查${NC}"
    fi

    return 0
}

# 显示启动信息
display_info() {
    echo -e "\n${GREEN}=============================================${NC}"
    echo -e "${GREEN}    Censorate 项目启动成功！${NC}"
    echo -e "${GREEN}=============================================${NC}"
    echo ""
    echo -e "${YELLOW}🌐 访问地址:${NC}"
    echo "   - 前端应用: http://localhost:3000"
    echo "   - 后端 API: http://localhost:8216"
    echo "   - API 文档: http://localhost:8216/docs"

    # 显示 skill-manager 信息
    echo "   - Skill-Manager: http://localhost:${SKILL_MANAGER_PORT:-8765}"
    echo ""
    echo -e "${YELLOW}🚀 核心功能:${NC}"
    echo "   - 看板视图: 需求的可视化管理"
    echo "   - 团队管理: 成员和 AI 代理管理"
    echo "   - 需求详情: 完整的需求信息"
    echo "   - AI 集成: 智能代理和分析功能"
    echo ""
    echo -e "${YELLOW}⚙️  管理命令:${NC}"
    echo "   - 停止服务: ./run.sh stop"
    echo "   - 重启服务: ./run.sh restart"
    echo "   - 查看状态: ./run.sh status"
    echo "   - 单独启动 Skill-Manager: ./run.sh start-daemon"
    echo "   - 单独停止 Skill-Manager: ./run.sh stop-daemon"
}

# 停止服务
stop_services() {
    echo -e "${GREEN}正在停止服务...${NC}"

    cd "${PROJECT_ROOT}"

    # 停止后端服务
    if [ -f "backend/backend.pid" ]; then
        BACKEND_PID=$(cat backend/backend.pid)
        if kill -0 $BACKEND_PID 2>/dev/null; then
            kill $BACKEND_PID
            echo -e "${GREEN}✅ 后端服务已停止${NC}"
        fi
        rm -f backend/backend.pid
    fi

    # 停止前端服务
    if [ -f "frontend/frontend.pid" ]; then
        FRONTEND_PID=$(cat frontend/frontend.pid)
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            kill $FRONTEND_PID
            echo -e "${GREEN}✅ 前端服务已停止${NC}"
        fi
        rm -f frontend/frontend.pid
    fi

    # 停止 skill-manager daemon
    stop_daemon

    # 停止所有相关的 Python 和 Node 进程
    pkill -f "python.*main.py" 2>/dev/null
    pkill -f "npm.*dev" 2>/dev/null
}

# 检查服务状态
check_status() {
    echo -e "${GREEN}检查服务状态:${NC}"

    # 检查后端服务
    if curl -f http://localhost:8216/docs >/dev/null 2>&1; then
        echo -e "${GREEN}✅ 后端服务运行正常${NC}"
    else
        echo -e "${RED}❌ 后端服务未运行${NC}"
    fi

    # 检查前端服务
    if curl -f http://localhost:3000 >/dev/null 2>&1; then
        echo -e "${GREEN}✅ 前端服务运行正常${NC}"
    else
        echo -e "${RED}❌ 前端服务未运行${NC}"
    fi
}

# 初始化 mock 数据
init_mock_data() {
    echo -e "${GREEN}=============================================${NC}"
    echo -e "${GREEN}    初始化 Mock 数据${NC}"
    echo -e "${GREEN}=============================================${NC}"
    echo ""

    cd "${PROJECT_ROOT}/backend"

    # 激活虚拟环境
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi

    # 运行初始化脚本
    echo -e "${YELLOW}正在创建 mock 数据...${NC}"
    python scripts/init_mock_data.py

    if [ $? -eq 0 ]; then
        echo -e "\n${GREEN}✅ Mock 数据初始化成功！${NC}"
    else
        echo -e "\n${RED}❌ Mock 数据初始化失败${NC}"
        exit 1
    fi
}

# 启动 skill-manager daemon
start_daemon() {
    echo -e "${GREEN}=============================================${NC}"
    echo -e "${GREEN}    启动 Skill Manager Daemon${NC}"
    echo -e "${GREEN}=============================================${NC}"
    echo ""

    cd "${PROJECT_ROOT}/daemon"

    # 创建虚拟环境（如果不存在）
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}正在创建 daemon 虚拟环境...${NC}"
        python3 -m venv venv
    fi

    # 激活虚拟环境
    source venv/bin/activate

    # 安装依赖
    echo -e "${YELLOW}正在安装 daemon 依赖...${NC}"
    pip install -r requirements.txt

    # 加载 env 文件（用于配置端口等）
    if [ -f "${SCRIPT_DIR}/.env" ]; then
        export $(grep -v '^#' "${SCRIPT_DIR}/.env" | xargs)
    fi

    # 确保 ~/.hermes 目录存在
    mkdir -p ~/.hermes

    # 启动 daemon（仅 server 模式 - webhook 驱动）
    echo -e "${GREEN}正在启动 skill-manager daemon...${NC}"
    echo -e "${YELLOW}  - Mode: server (webhook-driven)${NC}"
    echo -e "${YELLOW}  - Port: ${SKILL_MANAGER_PORT:-8765}${NC}"
    echo -e "${YELLOW}  - Hermes data dir: ~/.hermes${NC}"
    echo ""

    python skill_manager.py --server --hermes-data "$HOME/.hermes" &
    DAEMON_PID=$!
    echo $DAEMON_PID > "${PROJECT_ROOT}/daemon.pid"

    echo -e "${GREEN}✅ Skill Manager Daemon 已启动 (PID: ${DAEMON_PID})${NC}"
    echo -e "${YELLOW}查看日志: ${PROJECT_ROOT}/daemon/daemon.log${NC}"
}

# 停止 skill-manager daemon
stop_daemon() {
    echo -e "${GREEN}正在停止 Skill Manager Daemon...${NC}"

    cd "${PROJECT_ROOT}"

    if [ -f "daemon.pid" ]; then
        DAEMON_PID=$(cat daemon.pid)
        if kill -0 $DAEMON_PID 2>/dev/null; then
            kill $DAEMON_PID
            echo -e "${GREEN}✅ Skill Manager Daemon 已停止${NC}"
        fi
        rm -f daemon.pid
    else
        # Try to find and kill any running skill_manager processes
        pkill -f "python.*skill_manager.py" 2>/dev/null
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Skill Manager Daemon 已停止${NC}"
        fi
    fi
}

# 检查 daemon 状态
check_daemon_status() {
    echo -e "${GREEN}检查 Skill Manager Daemon 状态:${NC}"

    if [ -f "${PROJECT_ROOT}/daemon.pid" ]; then
        DAEMON_PID=$(cat "${PROJECT_ROOT}/daemon.pid")
        if kill -0 $DAEMON_PID 2>/dev/null; then
            echo -e "${GREEN}✅ Skill Manager Daemon 正在运行 (PID: ${DAEMON_PID})${NC}"
            # Check health endpoint
            if curl -f "http://localhost:${SKILL_MANAGER_PORT:-8765}/health" >/dev/null 2>&1; then
                echo -e "${GREEN}✅ HTTP 服务响应正常${NC}"
            fi
        else
            echo -e "${RED}❌ Skill Manager Daemon PID 文件存在但进程未运行${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️ Skill Manager Daemon 未运行${NC}"
    fi
}

# 主函数
main() {
    case "$1" in
        "start")
            # 检查系统需求
            check_command "node"
            check_command "python3"
            check_command "pip3"

            check_node_version
            check_python_version

            # 检查端口
            check_port 3000
            check_port 8216

            # 设置环境
            setup_python_env
            setup_frontend

            # 启动服务
            start_backend
            start_frontend
            start_daemon_if_configured

            # 检查服务状态
            if check_services; then
                display_info
            fi
            ;;

        "stop")
            stop_services
            ;;

        "restart")
            stop_services
            sleep 3
            main start
            ;;

        "status")
            check_status
            check_daemon_status
            ;;

        "setup")
            check_node_version
            check_python_version

            check_port 3000
            check_port 8216

            setup_python_env
            setup_frontend

            echo -e "${GREEN}✅ 项目环境配置完成${NC}"
            ;;

        "init")
            check_node_version
            check_python_version

            # 先确保环境配置好
            setup_python_env
            setup_frontend

            # 初始化 mock 数据
            init_mock_data
            ;;

        "start-daemon")
            start_daemon
            ;;

        "stop-daemon")
            stop_daemon
            ;;

        "daemon-status")
            check_daemon_status
            ;;

        *)
            echo "Usage: $0 {start|stop|restart|status|setup|init|start-daemon|stop-daemon|daemon-status}"
            echo ""
            echo "Commands:"
            echo "  start         - 启动所有服务"
            echo "  stop          - 停止所有服务"
            echo "  restart       - 重启所有服务"
            echo "  status        - 检查服务状态"
            echo "  setup         - 配置项目环境"
            echo "  init          - 初始化 mock 数据（项目、skills、成员等）"
            echo "  start-daemon  - 启动 skill-manager daemon"
            echo "  stop-daemon   - 停止 skill-manager daemon"
            echo "  daemon-status - 检查 skill-manager 状态"
            ;;
    esac
}

# 执行主函数
main "$1"
