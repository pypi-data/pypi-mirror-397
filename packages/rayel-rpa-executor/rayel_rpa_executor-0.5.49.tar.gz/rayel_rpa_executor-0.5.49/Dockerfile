# =============================================================================
# 第一阶段：基础环境构建（包含所有系统依赖和浏览器）
# 这个阶段会被缓存，避免重复安装 Playwright 浏览器
# =============================================================================
FROM python:3.12-slim as base

# 配置 Debian 使用国内镜像源加速（阿里云）
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources && \
    sed -i 's/security.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources

# 安装 Git、SSH 客户端和必要的系统工具
# Slim 版本需要额外安装 wget，其他 Playwright 依赖由 --with-deps 自动安装
# ⚠️ 新增 tini：作为容器 Entrypoint，负责回收所有僵尸进程（包括 Git/SSH 的孤儿进程, 防止PIDS无限增长）
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git \
        openssh-client \
        ca-certificates \
        wget curl procps tini && \
    rm -rf /var/lib/apt/lists/*


# 配置 Git 以增加网络容错性
RUN git config --global http.postBuffer 524288000 && \
    git config --global http.lowSpeedLimit 0 && \
    git config --global http.lowSpeedTime 999999 && \
    git config --global http.version HTTP/1.1 && \
    git config --global core.compression 0

# 配置 SSH：创建 .ssh 目录并添加 GitHub 和 GitLab 的 known_hosts
# 这样在使用 SSH 克隆时不会提示确认主机密钥
RUN mkdir -p /root/.ssh && \
    chmod 700 /root/.ssh && \
    ssh-keyscan -t rsa,ecdsa,ed25519 github.com >> /root/.ssh/known_hosts 2>/dev/null || true && \
    ssh-keyscan -t rsa,ecdsa,ed25519 gitlab.com >> /root/.ssh/known_hosts 2>/dev/null || true && \
    chmod 644 /root/.ssh/known_hosts

# 安装 uv 包管理器（极速依赖安装 + 智能冲突解决）
# 同时安装 playwright（用于执行 `playwright install ...` 下载浏览器）
#
# 说明：
# - 这里不再用 pip 直接安装 `rayel-rpa-executor`（避免与项目源码版本不一致）
# - 运行阶段会通过 uv 按 `pyproject.toml` 安装项目依赖（见下方 final 阶段）
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple uv playwright

# 安装 Playwright 和 Chromium 浏览器，作为执行器基础
# --with-deps 会自动安装所有系统依赖，安装完整版Chromium（包含headless支持）
# 这是最耗时的步骤，通过多阶段构建可以有效缓存这一层
RUN playwright install --with-deps chromium

# =============================================================================
# 第二阶段：应用程序构建（继承基础环境，添加应用代码）
# 当应用代码变化时，只需要重新构建这个阶段
# =============================================================================
FROM base as final

# 接收构建时传入的参数
ARG BUILD_DATE
ARG VERSION=latest
ARG VCS_REF
ARG VCS_URL

# 设置镜像元数据和标签
LABEL maintainer="914660773@qq.com" \
      description="SnailJob Playwright Executor - 通用 Playwright 自动化任务执行器" \
      version="${VERSION}" \
      name="laizezhong/snail-job-executor" \
      vendor="SnailJob" \
      url="https://github.com/snail-job/snail-job-executor" \
      documentation="https://github.com/snail-job/snail-job-executor/blob/main/README.md" \
      source="https://github.com/snail-job/snail-job-executor" \
      licenses="MIT" \
      build-date="${BUILD_DATE}" \
      title="SnailJob Playwright Executor" \
      base.name="python:3.12-slim" \
      runtime="python" \
      runtime.version="3.12" \
      component="executor" \
      part-of="snail-job" \
      managed-by="docker" \
      vcs-ref="${VCS_REF}" \
      vcs-url="${VCS_URL}"

WORKDIR /app

# 复制项目文件
# .dockerignore 会自动过滤虚拟环境、日志、文档等不需要的文件
COPY . .

# 使用 uv 按 pyproject.toml 安装所有 Python 依赖（安装到系统环境）
# - 这样容器内运行时不依赖 pip 单独装包
# - 会同时安装当前项目（snailjob/executor）及其依赖
RUN uv pip install --system .

# 设置时区和编码环境变量
ENV TZ=Asia/Shanghai \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# 配置 uv 性能优化环境变量（容器环境）
# 针对容器内网络环境优化，预期提升安装速度 2-3 倍
ENV UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple \
    UV_EXTRA_INDEX_URL="https://pypi.douban.com/simple https://mirrors.aliyun.com/pypi/simple https://pypi.org/simple" \
    UV_HTTP_TIMEOUT=120 \
    UV_CONCURRENT_BUILDS=1 \
    UV_KEYRING_PROVIDER=disabled \
    UV_COMPILE_BYTECODE=1 \
    UV_NO_PROGRESS=1 \
    UV_CACHE_DIR=/root/.cache/uv

# 健康检查（检查 FastAPI 服务是否正常, 以及snailjob客户端是否正常）
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget --no-verbose --tries=1 -O /dev/null http://localhost:8000/health && \
    python -c "import snailjob; print('OK')" || exit 1

# 启动 Playwright 执行器（FastAPI + APScheduler）
# ⚠️ 使用 tini 作为 Entrypoint，确保所有僵尸进程被正确回收，防止PIDS无限增长
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["python", "main.py"]