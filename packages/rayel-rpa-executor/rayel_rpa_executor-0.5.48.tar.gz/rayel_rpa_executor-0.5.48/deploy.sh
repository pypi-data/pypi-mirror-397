#!/bin/bash

# Playwright Executor 部署脚本
# 使用方法: ./deploy.sh [local|docker] [选项]
# 
# 部署模式:
#   local        : 本地直接运行（开发调试用）
#   docker       : Docker Compose 部署（生产环境用）
#               Docker 模式会询问是否忽略缓存重新构建
# 
# 其他选项:
#   --push       : Docker部署后推送镜像到仓库
#   --clean      : 部署前清理旧镜像和容器  
#   --help       : 显示帮助信息

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

function print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

function print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

function print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

function check_env() {
    if [ ! -f .env ]; then
        print_error ".env 文件不存在"
        print_info "正在从 env.example 创建 .env..."
        
        if [ -f env.example ]; then
            cp env.example .env
            print_warn "请编辑 .env 文件，填入正确的配置"
            exit 1
        else
            print_error "env.example 文件也不存在，无法创建配置"
            exit 1
        fi
    fi
    
    print_info "环境变量检查通过"
}

function deploy_local() {
    print_info "========== 本地部署 =========="
    
    check_env
    
    # 检查是否有正在运行的进程
    print_info "检查是否有正在运行的 Playwright 执行器进程..."
    pid=$(ps aux | grep "main.py" | grep -v grep | awk '{print $2}')
    
    if [ ! -z "$pid" ]; then
        print_warn "发现正在运行的进程 (PID: $pid)，正在停止..."
        kill $pid 2>/dev/null || true
        sleep 2
        
        # 如果进程还在运行，强制杀掉
        if ps -p $pid > /dev/null 2>&1; then
            print_warn "进程未停止，强制终止..."
            kill -9 $pid 2>/dev/null || true
        fi
        
        print_info "旧进程已停止"
    else
        print_info "没有发现正在运行的进程"
    fi
    
    # 检查 Python 版本
    python_version=$(python3 --version 2>&1 | awk '{print $2}')
    print_info "Python 版本: $python_version"
    
    # 检查 uv 是否安装
    if ! command -v uv &> /dev/null; then
        print_warn "uv 未安装，正在安装..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.cargo/bin:$PATH"
    fi
    
    print_info "uv 版本: $(uv --version)"
    
    # 安装依赖（使用 uv，极速安装）
    print_info "安装依赖（使用 uv）..."
    uv pip install -e .
    
    # 创建工作目录
    print_info "创建工作目录..."
    mkdir -p workspace/venvs/.md5_cache
    
    # 启动执行器
    print_info "启动 Playwright 执行器..."
    print_warn "按 Ctrl+C 停止执行器"
    python main.py
}

function deploy_docker() {
    print_info "========== Docker Compose 部署 =========="
    
    check_env
    
    # 检查 Docker Compose
    if ! docker compose version &> /dev/null; then
        print_error "Docker Compose 未安装，请先安装 Docker Compose"
        print_info "安装方法: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    # 先构建镜像（减少停机时间）
    print_info "构建 Docker 镜像..."
    
    # 询问是否忽略缓存重新构建
    echo ""
    print_warn "是否要忽略缓存重新构建镜像？"
    echo "  - 选择 [y] 会完全重新构建（较慢，但确保最新）"
    echo "  - 选择 [n] 会使用缓存构建（较快，适合日常开发）"
    echo "  - 10秒内无响应将默认使用缓存构建"
    echo ""
    
    # 使用超时读取，避免在CI/CD环境中卡住
    if read -t 10 -p "忽略缓存重新构建？ [y/N]: " rebuild_choice; then
        echo ""  # 换行
    else
        echo ""
        print_info "超时未响应，默认使用缓存构建"
        rebuild_choice="n"
    fi
    
    if [[ "$rebuild_choice" =~ ^[Yy]$ ]]; then
        print_warn "强制重新构建镜像（忽略缓存）..."
        docker compose --progress plain build --no-cache
    else
        print_info "使用缓存构建镜像..."
        docker compose --progress plain build
    fi
    
    print_info "镜像构建完成"
    
    # 检查服务是否在运行
    print_info "检查服务运行状态..."
    running_services=$(docker compose ps -q 2>/dev/null || true)
    
    if [ ! -z "$running_services" ]; then
        print_warn "发现正在运行的服务，正在停止..."
        docker compose down
        print_info "服务已停止"
    else
        print_info "没有发现正在运行的服务"
    fi
    
    # 启动服务
    print_info "启动服务..."
    docker compose up -d
    
    print_info "服务已启动"
    print_info "停止服务: docker compose down"
    echo ""
    
    # 询问是否查看日志
    read -p "是否查看实时日志？(y/n): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "正在打开日志，按 Ctrl+C 退出..."
        sleep 1
        docker compose logs -f snail-job-executor
    else
        print_info "查看日志命令: docker compose logs -f snail-job-executor"
    fi
}

function push_docker_image() {
    print_info "========== 推送 Docker 镜像 =========="
    
    # 从 docker-compose.yml 获取镜像名称
    if [ -f docker-compose.yml ] || [ -f docker-compose.yaml ]; then
        image_name=$(docker compose config | grep image: | head -n 1 | awk '{print $2}' || echo "")
        
        if [ -z "$image_name" ]; then
            # 如果没有从 compose 文件获取到，使用默认命名
            image_name="snail-job-executor:latest"
            print_warn "无法从 docker-compose 文件获取镜像名，使用默认名称: $image_name"
        fi
    else
        image_name="snail-job-executor:latest"
        print_warn "没有找到 docker-compose 文件，使用默认镜像名: $image_name"
    fi
    
    # 检查环境变量中的镜像仓库配置
    if [ -n "$DOCKER_REGISTRY" ]; then
        # 如果设置了 DOCKER_REGISTRY 环境变量
        registry_image="$DOCKER_REGISTRY/$image_name"
        
        print_info "标记镜像: $image_name -> $registry_image"
        docker tag "$image_name" "$registry_image"
        
        print_info "推送镜像到仓库: $registry_image"
        if docker push "$registry_image"; then
            print_info "镜像推送成功: $registry_image"
        else
            print_error "镜像推送失败，请检查:"
            print_error "1. 是否已登录到 Docker 仓库 (docker login)"
            print_error "2. 是否有推送权限"
            print_error "3. 网络连接是否正常"
            exit 1
        fi
        
    elif [ -n "$HARBOR_REGISTRY" ]; then
        # 支持 Harbor 仓库
        harbor_image="$HARBOR_REGISTRY/$image_name"
        
        print_info "标记镜像: $image_name -> $harbor_image"
        docker tag "$image_name" "$harbor_image"
        
        print_info "推送镜像到 Harbor: $harbor_image"
        if docker push "$harbor_image"; then
            print_info "镜像推送成功: $harbor_image"
        else
            print_error "镜像推送失败，请检查 Harbor 配置"
            exit 1
        fi
        
    else
        # 没有配置仓库，推送到 Docker Hub
        print_warn "未设置 DOCKER_REGISTRY 或 HARBOR_REGISTRY 环境变量"
        print_warn "将尝试推送到 Docker Hub: $image_name"
        
        read -p "确认推送到 Docker Hub？(y/n): " -n 1 -r
        echo ""
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_info "推送镜像: $image_name"
            if docker push "$image_name"; then
                print_info "镜像推送成功: $image_name"
            else
                print_error "镜像推送失败，请检查 Docker Hub 登录状态"
                print_info "登录命令: docker login"
                exit 1
            fi
        else
            print_warn "用户取消推送操作"
        fi
    fi
    
    print_info "========== 镜像推送完成 =========="
}

function show_usage() {
    echo "使用方法: $0 [local|docker] [选项]"
    echo ""
    echo "部署方式:"
    echo "  local           - 本地部署（开发环境）"
    echo "  docker          - Docker Compose 部署（推荐）"
    echo ""
    echo "选项:"
    echo "  --push          - Docker部署后推送镜像到仓库"
    echo "  --clean         - 部署前清理旧镜像和容器"
    echo "  --help          - 显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 local"
    echo "  $0 docker"
    echo "  $0 docker --clean"
    echo "  $0 docker --push"
    echo "  $0 docker --clean --push"
    echo "  $0 --help"
}

# 解析命令行参数
DEPLOY_MODE=""
PUSH_IMAGE=false
CLEAN_BEFORE_DEPLOY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        local|docker)
            if [[ -z "$DEPLOY_MODE" ]]; then
                DEPLOY_MODE="$1"
            else
                print_error "部署方式已设置为 $DEPLOY_MODE，不能重复设置"
                exit 1
            fi
            shift
            ;;
        --push)
            PUSH_IMAGE=true
            shift
            ;;
        --clean)
            CLEAN_BEFORE_DEPLOY=true
            shift
            ;;
        --help)
            show_usage
            exit 0
            ;;
        --*)
            print_error "未知选项: $1"
            show_usage
            exit 1
            ;;
        *)
            print_error "未知参数: $1"
            show_usage
            exit 1
            ;;
    esac
done

# 如果没有指定部署方式，显示帮助信息
if [[ -z "$DEPLOY_MODE" ]]; then
    show_usage
    exit 1
fi

# 主逻辑
case "$DEPLOY_MODE" in
    local)
        if [[ "$PUSH_IMAGE" == "true" ]]; then
            print_warn "--push 选项仅适用于 docker 部署，本地部署将忽略此选项"
        fi
        if [[ "$CLEAN_BEFORE_DEPLOY" == "true" ]]; then
            print_info "清理本地 Python 缓存..."
            find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
            find . -name "*.pyc" -delete 2>/dev/null || true
            print_info "本地缓存清理完成"
        fi
        deploy_local
        ;;
    docker)
        if [[ "$CLEAN_BEFORE_DEPLOY" == "true" ]]; then
            print_info "清理 Docker 环境..."
            # 停止并删除相关容器
            docker compose down 2>/dev/null || true
            # 删除相关镜像
            docker rmi $(docker images | grep snail-job-executor | awk '{print $3}') 2>/dev/null || true
            # 清理 Docker 系统
            docker system prune -f
            print_info "Docker 环境清理完成"
        fi
        deploy_docker
        if [[ "$PUSH_IMAGE" == "true" ]]; then
            push_docker_image
        fi
        ;;
esac

print_info "========== 部署完成 =========="

