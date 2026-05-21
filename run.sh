#!/bin/bash

# Censorate Code Generator - 项目启动脚本

echo "============================================="
echo "Censorate Code Generator - 项目启动脚本"
echo "============================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 项目根目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="${SCRIPT_DIR}/censorate-system"

if [ ! -d "${PROJECT_ROOT}" ]; then
    echo -e "${RED}错误: 项目目录不存在: ${PROJECT_ROOT}${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 项目目录验证通过${NC}"
echo ""

check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}错误: ${1} 命令未找到${NC}"
        exit 1
    fi
}

check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${YELLOW}警告: 端口 ${1} 正在被占用${NC}"
        pkill -f "python.*main.py" 2>/dev/null
        pkill -f "npm.*dev" 2>/dev/null
        sleep 2
    fi
}

setup_python_env() {
    cd "${PROJECT_ROOT}/backend"
    if [ ! -d "venv" ]; then
        echo -e "${GREEN}正在创建 Python 虚拟环境...${NC}"
        python3 -m venv venv
    fi
    echo -e "${GREEN}正在激活虚拟环境...${NC}"
    source venv/bin/activate
    echo -e "${GREEN}正在安装 Python 依赖...${NC}"
    pip install -r requirements.txt || { echo -e "${RED}依赖安装失败${NC}"; exit 1; }
}

setup_frontend() {
    cd "${PROJECT_ROOT}/frontend"
    if [ ! -d "node_modules" ]; then
        echo -e "${GREEN}正在安装前端依赖...${NC}"
        npm install || { echo -e "${RED}前端依赖安装失败${NC}"; exit 1; }
    fi
}

start_backend() {
    cd "${PROJECT_ROOT}/backend"
    echo -e "${GREEN}正在启动后端服务 (端口 8216)...${NC}"
    source venv/bin/activate
    python main.py &
    BACKEND_PID=$!
    echo $BACKEND_PID > backend.pid
    echo -e "${GREEN}后端服务已启动 (PID: ${BACKEND_PID})${NC}"
}

start_frontend() {
    cd "${PROJECT_ROOT}/frontend"
    echo -e "${GREEN}正在启动前端服务 (端口 3000)...${NC}"
    npm run dev &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > frontend.pid
    echo -e "${GREEN}前端服务已启动 (PID: ${FRONTEND_PID})${NC}"
}

check_services() {
    echo -e "\n${GREEN}正在检查服务启动状态...${NC}"
    sleep 5

    if curl -f http://localhost:8216/docs >/dev/null 2>&1; then
        echo -e "${GREEN}✅ 后端服务已成功启动${NC}"
    else
        echo -e "${RED}❌ 后端服务启动失败${NC}"
        return 1
    fi

    if curl -f http://localhost:3000 >/dev/null 2>&1; then
        echo -e "${GREEN}✅ 前端服务已成功启动${NC}"
    else
        echo -e "${RED}❌ 前端服务启动失败${NC}"
        return 1
    fi
}

display_info() {
    echo -e "\n${GREEN}=============================================${NC}"
    echo -e "${GREEN}    Censorate Code Generator 启动成功！${NC}"
    echo -e "${GREEN}=============================================${NC}"
    echo ""
    echo -e "${YELLOW}🌐 访问地址:${NC}"
    echo "   - 前端应用: http://localhost:3000"
    echo "   - API 文档: http://localhost:8216/docs"
    echo ""
    echo -e "${YELLOW}🚀 功能:${NC}"
    echo "   - AI 代码生成: 描述需求 → 生成完整仓库"
    echo "   - GitHub 推送: 一键推送到你的仓库"
    echo ""
    echo -e "${YELLOW}⚙️  管理命令:${NC}"
    echo "   - 停止: ./run.sh stop"
    echo "   - 重启: ./run.sh restart"
    echo "   - 状态: ./run.sh status"
}

stop_services() {
    echo -e "${GREEN}正在停止服务...${NC}"
    cd "${PROJECT_ROOT}"
    for pid_file in backend/backend.pid frontend/frontend.pid; do
        if [ -f "$pid_file" ]; then
            PID=$(cat "$pid_file")
            kill $PID 2>/dev/null && echo -e "${GREEN}✅ 已停止 $(basename $(dirname $pid_file)) 服务${NC}"
            rm -f "$pid_file"
        fi
    done
    pkill -f "python.*main.py" 2>/dev/null
    pkill -f "npm.*dev" 2>/dev/null
}

check_status() {
    echo -e "${GREEN}检查服务状态:${NC}"
    curl -f http://localhost:8216/docs >/dev/null 2>&1 && echo -e "${GREEN}✅ 后端服务运行正常${NC}" || echo -e "${RED}❌ 后端服务未运行${NC}"
    curl -f http://localhost:3000 >/dev/null 2>&1 && echo -e "${GREEN}✅ 前端服务运行正常${NC}" || echo -e "${RED}❌ 前端服务未运行${NC}"
}

main() {
    case "$1" in
        "start")
            check_command "node"
            check_command "python3"
            check_command "pip3"
            check_port 3000
            check_port 8216
            setup_python_env
            setup_frontend
            start_backend
            start_frontend
            check_services && display_info
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
            ;;
        "setup")
            setup_python_env
            setup_frontend
            echo -e "${GREEN}✅ 项目环境配置完成${NC}"
            ;;
        *)
            echo "Usage: $0 {start|stop|restart|status|setup}"
            ;;
    esac
}

main "$1"
