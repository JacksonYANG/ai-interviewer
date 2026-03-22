#!/bin/bash

# AI面试官系统部署脚本

set -e

echo "================================"
echo "AI面试官系统 - Docker部署"
echo "================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 函数: 打印信息
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# 检查Docker和Docker Compose
check_docker() {
    print_info "检查Docker环境..."

    if ! command -v docker &> /dev/null; then
        print_error "Docker未安装,请先安装Docker"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose未安装,请先安装Docker Compose"
        exit 1
    fi

    print_info "Docker环境检查通过"
}

# 创建必要的目录
create_directories() {
    print_info "创建数据目录..."

    mkdir -p data
    mkdir -p backups

    print_info "目录创建完成"
}

# 设置环境变量
setup_env() {
    print_info "设置环境变量..."

    if [ ! -f .env ]; then
        cat > .env << EOF
# 数据库配置
DATABASE_URL=sqlite+aiosqlite:///data/database.db

# JWT密钥 (生产环境请修改)
SECRET_KEY=$(openssl rand -hex 32)

# Token过期时间
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# LLM配置 (可选)
LLM_PROVIDER=qwen
LLM_API_KEY=your-api-key-here
LLM_MODEL_NAME=qwen-turbo

# 语音识别配置 (可选)
SPEECH_PROVIDER=aliyun
SPEECH_API_KEY=your-speech-api-key-here
EOF
        print_info ".env文件已创建"
        print_warning "请编辑.env文件,配置你的API密钥"
    else
        print_info ".env文件已存在"
    fi
}

# 构建镜像
build_images() {
    print_info "开始构建Docker镜像..."

    docker-compose build

    print_info "镜像构建完成"
}

# 启动服务
start_services() {
    print_info "启动服务..."

    docker-compose up -d

    print_info "服务启动完成"
}

# 查看服务状态
check_status() {
    print_info "检查服务状态..."

    docker-compose ps

    echo ""
    print_info "服务健康检查:"

    # 检查后端
    if curl -sf http://localhost:8000/health > /dev/null; then
        echo -e "${GREEN}✓${NC} 后端服务正常"
    else
        echo -e "${RED}✗${NC} 后端服务异常"
    fi

    # 检查前端
    if curl -sf http://localhost:3000/health > /dev/null; then
        echo -e "${GREEN}✓${NC} 前端服务正常"
    else
        echo -e "${RED}✗${NC} 前端服务异常"
    fi

    # 检查Nginx
    if curl -sf http://localhost/health > /dev/null; then
        echo -e "${GREEN}✓${NC} Nginx服务正常"
    else
        echo -e "${RED}✗${NC} Nginx服务异常"
    fi
}

# 查看日志
view_logs() {
    print_info "查看服务日志..."
    docker-compose logs -f
}

# 停止服务
stop_services() {
    print_info "停止服务..."
    docker-compose down
    print_info "服务已停止"
}

# 清理资源
cleanup() {
    print_warning "清理Docker资源..."
    docker-compose down -v
    docker system prune -f
    print_info "清理完成"
}

# 主菜单
show_menu() {
    echo ""
    echo "================================"
    echo "请选择操作:"
    echo "================================"
    echo "1) 首次安装"
    echo "2) 启动服务"
    echo "3) 停止服务"
    echo "4) 重启服务"
    echo "5) 查看状态"
    echo "6) 查看日志"
    echo "7) 清理资源"
    echo "8) 退出"
    echo "================================"
    read -p "请输入选项 [1-8]: " choice

    case $choice in
        1)
            check_docker
            create_directories
            setup_env
            build_images
            start_services
            check_status
            ;;
        2)
            start_services
            check_status
            ;;
        3)
            stop_services
            ;;
        4)
            stop_services
            start_services
            check_status
            ;;
        5)
            check_status
            ;;
        6)
            view_logs
            ;;
        7)
            cleanup
            ;;
        8)
            print_info "退出"
            exit 0
            ;;
        *)
            print_error "无效选项"
            ;;
    esac
}

# 主函数
main() {
    # 如果有参数,直接执行对应操作
    if [ $# -gt 0 ]; then
        case $1 in
            install)
                check_docker
                create_directories
                setup_env
                build_images
                start_services
                check_status
                ;;
            start)
                start_services
                check_status
                ;;
            stop)
                stop_services
                ;;
            restart)
                stop_services
                start_services
                check_status
                ;;
            status)
                check_status
                ;;
            logs)
                view_logs
                ;;
            cleanup)
                cleanup
                ;;
            *)
                echo "用法: $0 {install|start|stop|restart|status|logs|cleanup}"
                exit 1
                ;;
        esac
    else
        # 交互式菜单
        while true; do
            show_menu
        done
    fi
}

# 运行主函数
main "$@"
