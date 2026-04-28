#!/bin/bash
# EconoNews 一键启动脚本 (macOS / Linux)
# 用法: ./start.sh [--backend-only | --frontend-only | --setup-only]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

# 打印带颜色的消息
print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 打印 Banner
print_banner() {
    echo -e "${GREEN}"
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║       EconoNews Intelligence Hub - 一键启动脚本         ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# 检测操作系统
detect_os() {
    case "$(uname -s)" in
        Darwin*)    OS="macos";;
        Linux*)     OS="linux";;
        *)          print_error "不支持的操作系统: $(uname -s)"; exit 1;;
    esac
    print_info "检测到操作系统: $OS"
}

# 检查依赖
check_dependencies() {
    print_info "检查系统依赖..."

    # 检查 Python
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        print_error "未找到 Python，请先安装 Python 3.8+"
        exit 1
    fi

    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
    print_success "Python 版本: $PYTHON_VERSION"

    # 检查 pip
    if ! $PYTHON_CMD -m pip --version &> /dev/null; then
        print_error "未找到 pip，请先安装 pip"
        exit 1
    fi
    print_success "pip 已就绪"

    # 检查 Node.js (仅前端需要)
    if [[ "$1" != "--backend-only" && "$1" != "--setup-only" ]]; then
        if command -v node &> /dev/null; then
            NODE_VERSION=$(node --version)
            print_success "Node.js 版本: $NODE_VERSION"
        else
            print_error "未找到 Node.js，请先安装 Node.js 16+"
            exit 1
        fi

        if command -v npm &> /dev/null; then
            NPM_VERSION=$(npm --version)
            print_success "npm 版本: $NPM_VERSION"
        else
            print_error "未找到 npm，请先安装 npm"
            exit 1
        fi
    fi
}

# 设置后端环境
setup_backend() {
    print_info "配置后端环境..."
    cd "$BACKEND_DIR"

    # 创建虚拟环境
    if [[ ! -d ".venv" ]]; then
        print_info "创建 Python 虚拟环境..."
        $PYTHON_CMD -m venv .venv
        print_success "虚拟环境创建完成"
    else
        print_info "虚拟环境已存在，跳过创建"
    fi

    # 激活虚拟环境
    print_info "激活虚拟环境..."
    source .venv/bin/activate

    # 升级 pip
    print_info "升级 pip..."
    pip install --upgrade pip -q

    # 安装依赖
    print_info "安装 Python 依赖..."
    pip install -r requirements.txt -q
    print_success "Python 依赖安装完成"

    # 配置 .env 文件
    if [[ ! -f ".env" ]]; then
        if [[ -f ".env.example" ]]; then
            print_info "创建 .env 配置文件..."
            cp .env.example .env
            print_success ".env 文件已创建"
            print_warning "请编辑 backend/.env 文件配置必要的参数 (如 TUSHARE_TOKEN)"
        else
            print_warning "未找到 .env.example 文件"
        fi
    else
        print_info ".env 文件已存在，跳过创建"
    fi

    deactivate 2>/dev/null || true
    cd "$SCRIPT_DIR"
}

# 设置前端环境
setup_frontend() {
    print_info "配置前端环境..."
    cd "$FRONTEND_DIR"

    # 安装依赖
    if [[ ! -d "node_modules" ]]; then
        print_info "安装前端依赖..."
        npm install
        print_success "前端依赖安装完成"
    else
        print_info "node_modules 已存在，检查是否需要更新..."
        npm install
    fi

    # 配置 .env 文件
    if [[ ! -f ".env" ]]; then
        if [[ -f ".env.example" ]]; then
            print_info "创建前端 .env 配置文件..."
            cp .env.example .env
            print_success "前端 .env 文件已创建"
        else
            print_warning "未找到前端 .env.example 文件"
        fi
    else
        print_info "前端 .env 文件已存在，跳过创建"
    fi

    cd "$SCRIPT_DIR"
}

# 启动后端服务
start_backend() {
    print_info "启动后端服务..."
    cd "$BACKEND_DIR"

    # 激活虚拟环境
    source .venv/bin/activate

    # 检查 .env 文件
    if [[ ! -f ".env" ]]; then
        print_warning ".env 文件不存在，使用默认配置"
    fi

    print_info "后端服务运行在 http://127.0.0.1:8000"
    print_info "API 文档地址 http://127.0.0.1:8000/docs"

    # 后台启动
    nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > ../backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../backend.pid
    print_success "后端服务已启动 (PID: $BACKEND_PID)"

    deactivate
    cd "$SCRIPT_DIR"
}

# 启动前端服务
start_frontend() {
    print_info "启动前端服务..."
    cd "$FRONTEND_DIR"

    print_info "前端服务运行在 http://localhost:5173"

    # 后台启动
    nohup npm run dev > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../frontend.pid
    print_success "前端服务已启动 (PID: $FRONTEND_PID)"

    cd "$SCRIPT_DIR"
}

# 停止服务
stop_services() {
    print_info "停止服务..."

    if [[ -f "backend.pid" ]]; then
        BACKEND_PID=$(cat backend.pid)
        if kill -0 $BACKEND_PID 2>/dev/null; then
            kill $BACKEND_PID 2>/dev/null || true
            print_success "后端服务已停止 (PID: $BACKEND_PID)"
        fi
        rm -f backend.pid
    fi

    if [[ -f "frontend.pid" ]]; then
        FRONTEND_PID=$(cat frontend.pid)
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            kill $FRONTEND_PID 2>/dev/null || true
            print_success "前端服务已停止 (PID: $FRONTEND_PID)"
        fi
        rm -f frontend.pid
    fi

    # 额外清理可能残留的进程
    pkill -f "uvicorn app.main:app" 2>/dev/null || true
    pkill -f "vite" 2>/dev/null || true
}

# 显示状态
show_status() {
    echo ""
    print_info "服务状态:"
    echo ""

    # 检查后端
    if curl -s http://127.0.0.1:8000/api/v1/system/heartbeats > /dev/null 2>&1; then
        print_success "后端服务: 运行中 (http://127.0.0.1:8000)"
    else
        print_warning "后端服务: 未运行"
    fi

    # 检查前端
    if curl -s http://localhost:5173 > /dev/null 2>&1; then
        print_success "前端服务: 运行中 (http://localhost:5173)"
    else
        print_warning "前端服务: 未运行"
    fi

    echo ""
    print_info "日志文件:"
    echo "  - 后端日志: $SCRIPT_DIR/backend.log"
    echo "  - 前端日志: $SCRIPT_DIR/frontend.log"
    echo ""
    print_info "停止服务: ./start.sh --stop"
    print_info "查看后端日志: tail -f backend.log"
    print_info "查看前端日志: tail -f frontend.log"
}

# 显示帮助
show_help() {
    echo "用法: ./start.sh [选项]"
    echo ""
    echo "选项:"
    echo "  无参数          完整安装并启动所有服务"
    echo "  --setup-only    仅安装依赖，不启动服务"
    echo "  --backend-only  仅启动后端服务"
    echo "  --frontend-only 仅启动前端服务"
    echo "  --stop          停止所有服务"
    echo "  --status        查看服务状态"
    echo "  --help          显示此帮助信息"
    echo ""
    echo "首次运行建议:"
    echo "  1. 编辑 backend/.env 配置 TUSHARE_TOKEN 等参数"
    echo "  2. 运行 ./start.sh 启动服务"
    echo "  3. 访问 http://localhost:5173 使用应用"
}

# 等待服务就绪
wait_for_backend() {
    print_info "等待后端服务就绪..."
    for i in {1..30}; do
        if curl -s http://127.0.0.1:8000/api/v1/system/heartbeats > /dev/null 2>&1; then
            print_success "后端服务就绪"
            return 0
        fi
        sleep 1
    done
    print_warning "后端服务启动超时，请检查 backend.log"
    return 1
}

# 主函数
main() {
    print_banner
    detect_os

    case "$1" in
        --help|-h)
            show_help
            exit 0
            ;;
        --stop)
            stop_services
            print_success "所有服务已停止"
            exit 0
            ;;
        --status)
            show_status
            exit 0
            ;;
        --setup-only)
            check_dependencies "--setup-only"
            setup_backend
            setup_frontend
            print_success "环境配置完成！"
            echo ""
            print_info "下一步:"
            echo "  1. 编辑 backend/.env 配置必要参数"
            echo "  2. 运行 ./start.sh 启动服务"
            exit 0
            ;;
        --backend-only)
            check_dependencies "--backend-only"
            setup_backend
            start_backend
            show_status
            exit 0
            ;;
        --frontend-only)
            check_dependencies
            setup_frontend
            start_frontend
            show_status
            exit 0
            ;;
    esac

    # 默认：完整安装并启动
    check_dependencies
    setup_backend
    setup_frontend
    start_backend
    sleep 2
    start_frontend

    echo ""
    print_success "所有服务启动完成！"
    sleep 3
    show_status
}

# 执行主函数
main "$@"