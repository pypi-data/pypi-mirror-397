<p align="center">
    🎭 基于 SnailJob 的通用 Playwright 自动化任务执行器
</p>

<p align="center">
  <a href="#快速开始">快速开始</a> •
  <a href="#需求开发指南">需求开发</a> •
  <a href="#部署指南">部署指南</a> •
  <a href="#常见问题">常见问题</a>
</p>

---

# Playwright Executor

基于 [SnailJob](https://gitee.com/aizuda/snail-job) 的通用 Playwright 自动化任务执行器，专为执行存储在 GitLab 中的 Playwright 项目而设计。

## 核心特性

- ✅ **定期快照更新**: 后台刷新线程定期从 Git 获取最新代码，构建“不可变快照”并原子切换 `current`
- ✅ **执行期版本一致**: 单个任务从开始到结束固定使用同一份代码快照，杜绝“部分新部分旧”
- ✅ **更新失败隔离**: Git 拉取/导出失败只影响本轮刷新，不影响正在执行/新启动任务
- ✅ **分层虚拟环境**: 共享基础依赖，磁盘节省 70-80%，新 service 创建仅需 30秒
- ✅ **智能依赖管理**: 基于 MD5 校验，仅在依赖变化时重新安装
- ✅ **实时日志**: 执行日志实时上报到 SnailJob 服务器
- ✅ **任务控制**: 支持任务中断和超时控制
- ✅ **Docker 部署**: 生产环境就绪，支持 Docker Compose 一键部署

## 工作原理

```
SnailJob 调度任务
    ↓
Playwright Executor 接收任务
    ↓
代码快照(RepoLease): 解析 current → 固定到真实快照目录 → 引用计数+1
    ↓
Env Manager: 分层虚拟环境 (共享基础依赖 + service特定依赖)
    ↓
Script Runner: 动态导入 main.py
    ↓
调用 run(extra_params) 方法
    ↓
监控执行 (超时/中断检测)
    ↓
返回结果到 SnailJob

【后台定期刷新线程】
Git 快照: fetch → git archive 导出新快照目录 → 原子切换 current symlink → 清理无引用旧快照
```

### Git 快照机制（推荐的生产模式）

**核心设计**：不可变快照目录 + `current` symlink 原子切换 + 任务租约（引用计数）

- **快照目录**：每个 commit 一份完整工作树，创建后不再原地修改
- **current 指针**：`{workspace_root}/rpa_projects` 是一个 symlink，指向当前生效快照目录
- **任务租约**：任务开始时解析 current 并固定到真实快照目录，执行完成释放租约（引用计数 -1）
- **刷新线程**：周期性 fetch，并用 `git archive` 导出新快照；成功后原子切换 current；失败仅记录日志

**为什么能保证“执行期间版本一致”**：
- 任务执行使用的是“真实快照目录路径”，刷新线程切换 current 不会修改旧快照目录
- 即使执行过程中发生新的 import/读文件，也只会读到同一快照下的文件

### workspace 目录结构（重要）

以 `EXECUTOR_WORKSPACE_ROOT=/workspace` 为例：

```
/workspace/
├── rpa_projects                     # current symlink（指向某个快照目录）
├── .rpa_projects_mirror/            # Git mirror（仅用于 fetch/archive）
├── .rpa_projects_revs/<commit>/     # 快照目录池（不可变）
├── .rpa_projects_refs/<commit>.json # 引用计数（任务租约）
├── venvs/                           # 分层虚拟环境
└── .tmp/                            # 迁移备份、临时导出目录
```

---

# 快速开始

## 前置条件

- Python 3.12+
- uv 包管理器（执行器内置）
- GitLab 仓库访问权限
- SnailJob 服务器


## 方式一：本地开发部署

```bash
# 1. 克隆项目
git clone https://gitee.com/opensnail/snail-job-executor.git
cd snail-job-executor

# 2. 配置环境变量
cp env.example .env
# 编辑 .env 文件

# 3. 安装 uv 包管理器（如果未安装）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 4. 创建虚拟环境（使用 uv，极速）
uv venv --python 3.12
source .venv/bin/activate

# 5. 安装项目
uv pip install -e .

# 6. 启动执行器
python main.py
```

## 方式二：使用部署脚本

```bash
# 1. 配置环境变量
cp env.example .env

# 2.1 本地部署
./deploy.sh local

# 2.2 Docker 部署
./deploy.sh docker
```

---

# 环境配置

## 环境变量说明

### 必需配置

| 环境变量 | 说明 | 示例 | 备注 |
|---------|------|------|------|
| `GIT_REPO_URL` | Git 仓库地址 | `https://gitlab.com/org/project.git`<br>或 `git@github.com:org/project.git` | 支持 HTTPS 和 SSH 两种格式 |
| `GIT_TOKEN` | Git 访问令牌 | `glpat-xxxxxxxxxxxx` | **仅 HTTPS 方式需要**，SSH 方式不需要 |
| `SNAIL_SERVER_HOST` | SnailJob 服务器地址 | `192.168.1.100` | - |
| `SNAIL_SERVER_PORT` | SnailJob 服务器端口 | `1788` | - |

### 可选配置

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| `SNAIL_NAMESPACE` | 命名空间 | `default` |
| `SNAIL_GROUP_NAME` | 组名 | `playwright_group` |
| `SNAIL_APP_NAME` | 应用名 | `playwright_executor` |
| `SNAIL_HOST_IP` | 客户端 IP | 自动获取 |
| `SNAIL_HOST_PORT` | 客户端端口 | `1633` |
| `LOG_ENV` | 日志环境 | `remote` |
| `EXECUTOR_WORKSPACE_ROOT` | 执行器工作目录（快照/venv 都在这里） | `./workspace` |
| `EXECUTOR_GIT_BRANCH` | 执行器使用的固定分支（单分支模式） | `main` |

## 配置示例

创建 `.env` 文件：

```bash
# Git 配置（必需）
GIT_REPO_URL=https://gitlab.com/your-org/playwright-project.git
GIT_TOKEN=glpat-xxxxxxxxxxxx

# SnailJob 服务端配置（必需）
SNAIL_SERVER_HOST=192.168.1.100
SNAIL_SERVER_PORT=1788

# SnailJob 客户端配置（可选）
SNAIL_NAMESPACE=default
SNAIL_GROUP_NAME=playwright_group
```

## Git 仓库访问方式

执行器支持两种方式访问 Git 仓库：**SSH**（推荐）和 **HTTPS**。

### 方式一：SSH 方式（推荐）⭐

**优势**：
- ✅ 不受 GitHub/GitLab 限流影响
- ✅ 连接更稳定，性能更好
- ✅ 无需在 URL 中嵌入 token，更安全
- ✅ 支持 GitHub 和 GitLab（包括自建 GitLab）

**配置步骤**：

1. **生成 SSH key**（如果还没有）：
   ```bash
   ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
   ```

2. **将公钥添加到 GitHub/GitLab**：
   ```bash
   # 复制公钥内容
   cat ~/.ssh/id_rsa.pub
   ```
   - **GitHub**: Settings → SSH and GPG keys → New SSH key
   - **GitLab**: Settings → SSH Keys → Add SSH Key

3. **修改 `.env` 文件**，使用 SSH URL：
   ```bash
   # GitHub SSH URL
   GIT_REPO_URL=git@github.com:laizezhong/rpa-projects.git
   
   # 或 GitLab SSH URL
   # GIT_REPO_URL=git@gitlab.com:zezhong.lai/rpa-projects.git
   
   # 或自建 GitLab SSH URL
   # GIT_REPO_URL=git@gitlab.yeepay.com:zezhong.lai/rpa-projects.git
   
   # 注意：使用 SSH 时不需要 GIT_TOKEN
   ```

4. **确保 SSH key 文件存在**：
   ```bash
   # 检查文件是否存在
   ls -la ~/.ssh/id_rsa
   
   # 如果不存在，请先生成 SSH key
   ```

5. **重启容器**：
   ```bash
   docker-compose down
   docker-compose up -d
   ```

**注意事项**：
- 确保宿主机 `~/.ssh/id_rsa` 文件存在且已添加到 GitHub/GitLab
- Docker Compose 会自动挂载 `~/.ssh/id_rsa` 到容器中
- 对于自建 GitLab，如果首次连接，可能需要手动添加 known_hosts

### 方式二：HTTPS 方式

**适用场景**：
- 临时使用或测试环境
- 无法配置 SSH key 的环境

**配置步骤**：

1. **获取 Git Token**：
   - **GitHub**: Settings → Developer settings → Personal access tokens → Generate new token
   - **GitLab**: Settings → Access Tokens → Create personal access token

2. **修改 `.env` 文件**：
   ```bash
   # GitHub HTTPS URL
   GIT_REPO_URL=https://github.com/laizezhong/rpa-projects.git
   GIT_TOKEN=github_pat_XXXX
   
   # 或 GitLab HTTPS URL
   # GIT_REPO_URL=https://gitlab.yeepay.com/zezhong.lai/rpa-projects.git
   # GIT_TOKEN=glpat-XXXX
   ```

**注意事项**：
- ⚠️ HTTPS 方式可能遇到限流问题（特别是频繁 clone/pull 时）
- 如果遇到 `GnuTLS recv error (-110)` 等错误，建议切换到 SSH 方式

---

# 业务开发指南

## GitLab 项目结构

RPA项目的 GitLab 仓库需要按照以下结构组织：

```
your-playwright-project/
├── pyproject.toml           # 根目录通用依赖（必需）
└── app/
    └── services/             # RPA业务逻辑父目录（固定路径）
        ├── demo_service/ # 业务子文件夹（配置时只需写 demo_service）
        │   ├── main.py       # 必需：包含 run() 方法
        │   ├── pyproject.toml # 可选：业务特定依赖
        │   └── config.json   # 可选：业务配置
        └── other_service/    # 配置时只需写 other_service
            └── main.py
```

## 编写业务脚本

### 1. 固定的 run() 方法签名（必需）

每个业务的 `main.py` 必须实现以下方法：

```python
import snailjob as sj

def run(extra_params: dict = None) -> int:
    """
    执行器的入口方法（必需）
    
    Args:
        extra_params: 从 SnailJob 任务参数传递的额外参数字典
        
    Returns:
        int: 返回码
            - 0: 执行成功
            - 非0: 执行失败
    """
    try:
        # 1. 从 extra_params 获取参数
        target_url = extra_params.get("target_url", "https://example.com") if extra_params else "https://example.com"
        
        # 2. 使用 sj.SnailLog.AUTO 记录日志（自动适配本地/远程）
        sj.SnailLog.AUTO.info(f"开始执行任务，目标URL: {target_url}")
        
        # 3. 执行业务逻辑
        result = your_business_logic(target_url)
        
        # 4. 记录成功日志
        sj.SnailLog.AUTO.info(f"任务执行成功: {result}")
        
        return 0
        
    except Exception as e:
        # 5. 记录错误日志
        sj.SnailLog.AUTO.error(f"任务执行失败: {str(e)}")
        
        import traceback
        sj.SnailLog.AUTO.error(traceback.format_exc())
        
        return 1
```

### 2. 使用 Playwright

```python
import snailjob as sj
from playwright.sync_api import sync_playwright

def run(extra_params: dict = None) -> int:
    try:
        target_url = extra_params.get("target_url", "https://example.com") if extra_params else "https://example.com"
        sj.SnailLog.AUTO.info(f"开始访问: {target_url}")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            page.goto(target_url)
            title = page.title()
            sj.SnailLog.AUTO.info(f"页面标题: {title}")
            
            browser.close()
        
        sj.SnailLog.AUTO.info("执行完成")
        return 0
        
    except Exception as e:
        sj.SnailLog.AUTO.error(f"执行失败: {str(e)}")
        import traceback
        sj.SnailLog.AUTO.error(traceback.format_exc())
        return 1
```

### 3. 导入通用工具类

```python
# 直接导入即可，执行器会自动添加项目根目录到 sys.path
from common.utils import some_util_function
from common.db_client import DatabaseClient

def run(extra_params: dict = None) -> int:
    result = some_util_function()
    db = DatabaseClient()
    # ...
    return 0
```

### 4. 本地调试

```python
if __name__ == "__main__":
    # 本地测试
    test_params = {
        "target_url": "https://example.com"
    }
    exit_code = run(extra_params=test_params)
    print(f"执行结果: {exit_code}")
```

## 日志使用

### 使用 SnailLog.AUTO（推荐）⭐

**推荐使用 `sj.SnailLog.AUTO`，自动适配本地测试和远程执行！**

```python
import snailjob as sj

def run(extra_params: dict = None) -> int:
    # 使用 AUTO 日志，无需关心运行环境
    sj.SnailLog.AUTO.info("开始执行")
    sj.SnailLog.AUTO.warning("警告信息")
    sj.SnailLog.AUTO.error("错误信息")
    return 0
```

**工作原理**：
- **本地测试**（直接运行 `python main.py`）：自动使用本地日志
- **远程执行**（SnailJob 调度）：自动上报到 SnailJob 服务器

### 手动指定日志类型（可选）

```python
# 仅本地日志（不上报）
sj.SnailLog.LOCAL.info("本地日志")

# 远程日志（会上报到 SnailJob）
sj.SnailLog.REMOTE.info("远程日志")
```

## 依赖管理

### 包管理器：uv

执行器使用 **uv** 包管理器进行依赖管理，提供：

- ⚡ **极速安装**：比 pip 快 10-100 倍
- 🧠 **智能冲突解决**：自动处理版本冲突
- 🔒 **环境一致性**：确保所有环境依赖一致

### 根目录依赖

项目根目录的 `pyproject.toml` 包含通用依赖：

```toml
# 根目录 pyproject.toml
[project]
name = "rpa-projects"
version = "1.0.0"
dependencies = [
    "requests>=2.32.5",
    "playwright>=1.49.1",
    # ... 其他通用依赖
]
```

### 业务特定依赖

如果业务有特定的依赖，创建业务逻辑文件夹下的 `pyproject.toml`：

```toml
# app/services/demo_service/pyproject.toml
[project]
name = "demo-service"
version = "1.0.0"
dependencies = [
    "selenium>=4.0",
    "beautifulsoup4>=4.12.0",
]
```

uv 会自动合并根目录和业务目录的依赖，并智能解决版本冲突。

### 分层虚拟环境机制

执行器使用**分层虚拟环境**架构，实现磁盘节省 70-80%：

```
workspace/venvs/
├── _shared_base/              # 共享基础环境（500MB，所有service共享）
│   └── 根目录 pyproject.toml 的依赖
│
├── demo_service_venv/         # Service overlay 环境（5MB）
│   ├── pyvenv.cfg → 继承 _shared_base
│   └── 仅 demo_service 特定依赖
│
└── other_service_venv/        # Service overlay 环境（5MB）
    └── 仅 other_service 特定依赖
```

**工作流程**：
1. 创建共享基础环境 `_shared_base`，安装根目录依赖
2. 为每个 service 创建 overlay 环境，继承基础环境
3. 只安装 service 特定依赖
4. **MD5 校验**：只有依赖变化时才重新安装

**优势**：
- 磁盘节省 70-80%（10个service：从 8GB → 2-3GB）
- 新 service 创建速度提升 10倍（从 5分钟 → 30秒）
- 依赖更新速度提升 3倍（从 3分钟 → 1分钟）

### 依赖冲突处理

uv 会自动处理依赖冲突：

```toml
# 根目录：midscene-python>=0.9.7 需要 openai>=2.7
# 业务目录：midscene-python>=0.1.1 需要 openai~=1.109

# uv 自动分析并找到兼容版本
# 如果无法解决，会给出清晰的错误提示
```

---

# 在 SnailJob 中创建任务

## 创建步骤

1. 登录 SnailJob 管理后台
2. 创建新的定时任务
3. **执行器类型**选择：`Python`
4. **执行器名称**填入：`PlaywrightExecutor`
5. 配置任务参数

## 任务参数配置

### 基本参数

```json
{
  "service_folder": "demo_service"
}
```

**注意**: `service_folder` 只需要写子文件夹名称（如 `demo_service`），系统会自动拼接父目录 `app/services/`，最终路径为 `app/services/demo_service`。

### 完整参数示例

```json
{
  "service_folder": "demo_service",
  "extra_params": {
    "target_url": "https://example.com",
    "env": "production",
    "config": {
      "headless": true,
      "timeout": 30
    }
  }
}
```

### 参数说明

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `service_folder` | string | ✅ | - | 业务逻辑子文件夹名称（只需写子文件夹名，如：`demo_service`）<br>系统会自动拼接父目录 `app/services/` |
| `workspace_root` | string | ❌ | `./workspace` | 工作目录（建议只通过环境变量 `EXECUTOR_WORKSPACE_ROOT` 配置） |
| `extra_params` | object | ❌ | {} | 传递给 run() 的参数 |

**注意**: 
- `service_folder` 只需要写子文件夹名称（如 `demo_service`），系统会自动拼接为 `app/services/demo_service`
- Git 仓库地址通过环境变量 `GIT_REPO_URL` 配置，不在任务参数中传递
- **单分支模式**：执行器只使用 `EXECUTOR_GIT_BRANCH` 指定的分支（通常是 `main`），任务参数不提供分支切换

---

# 部署指南

## 本地部署

### 安装依赖

```bash
# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 使用 uv 安装依赖
uv pip install -e .
```

### 启动执行器

```bash
python main.py
```

## Docker 部署

### 构建镜像

```bash
docker build -t snail-job-playwright:latest .
```

### 运行容器

```bash
docker run -d \
  --name snail-job-playwright \
  --restart unless-stopped \
  -e GIT_TOKEN="${GIT_TOKEN}" \
  -e SNAIL_SERVER_HOST="${SNAIL_SERVER_HOST}" \
  -e GIT_REPO_URL="${GIT_REPO_URL}" \
  -v rpa-workspace:/workspace \
  snail-job-playwright:latest
```

### 查看日志

```bash
docker logs -f snail-job-playwright
```

## Docker Compose 部署（推荐）

### 启动服务

```bash
docker-compose up -d
```

### 查看日志

```bash
docker-compose logs -f
```

### 停止服务

```bash
docker-compose down
```

### 重启服务

```bash
docker-compose restart
```

---

# 常见问题

## 升级snailjob
**获取snailjob最新代码，覆盖snailjob目录即可，若环境变量有变更，则跟随修改**


## GitLab 相关

### Q: GitLab 代码拉取失败？

**A**: 检查以下几点：
- 检查 `GIT_TOKEN` 是否正确（HTTPS 方式）
- 确认 GitLab 仓库权限（至少需要 `read_repository` 权限）
- 检查 `GIT_REPO_URL` 格式是否正确
- 检查网络连接
- **如果使用 HTTPS 方式遇到限流，建议切换到 SSH 方式**

### Q: 如何获取 GitLab Token？

**A**: 
1. 登录 GitLab
2. 进入 Settings → Access Tokens
3. 创建 Personal Access Token
4. 勾选 `read_repository` 权限
5. 复制生成的 Token

### Q: 遇到 `GnuTLS recv error (-110)` 错误？

**A**: 这是 GitHub/GitLab HTTPS 限流导致的连接中断问题。**强烈建议切换到 SSH 方式**：
1. 生成 SSH key：`ssh-keygen -t rsa -b 4096`
2. 将公钥添加到 GitHub/GitLab
3. 修改 `GIT_REPO_URL` 为 SSH 格式：`git@github.com:user/repo.git`
4. 重启容器

### Q: SSH 方式配置后仍然失败？

**A**: 检查以下几点：
- 确认 `~/.ssh/id_rsa` 文件存在
- 确认 SSH key 已添加到 GitHub/GitLab
- 检查 Docker Compose 中是否正确挂载了 SSH key
- 查看容器日志确认 SSH key 权限是否正确（应为 600）
- 对于自建 GitLab，可能需要手动添加 known_hosts

## 依赖相关

### Q: 依赖安装失败？

**A**: 
- 查看 SnailJob 日志中的详细错误信息
- 检查 `pyproject.toml` 格式是否正确
- 确认 PyPI 镜像源可访问
- 尝试使用其他镜像源

### Q: 如何使用私有 PyPI 源？

**A**: 在业务的 `pyproject.toml` 中指定：

```toml
[tool.uv]
index-url = "https://your-pypi-server.com/simple/"
trusted-host = "your-pypi-server.com"
```

## 执行相关

### Q: 日志出现 “current 不存在 / current 快照不可用”？

**A**：这是快照 current 指针不可用导致的（例如第一次初始化失败、或工作目录挂载错误）。排查顺序：

1. 确认 `EXECUTOR_WORKSPACE_ROOT` 是否正确（Docker 建议挂载到 `/workspace`）
2. 确认 `GIT_REPO_URL` 可访问（SSH key 或 token）
3. 查看日志中是否出现 `[快照Git] 初始化 mirror` / `git fetch` / `git archive` 的报错

### Q: 如何查看当前生效的代码版本（commit）？

**A**：在 `{workspace_root}/rpa_projects` 指向的真实目录下查看 `.snapshot_commit`：

```bash
readlink -f /workspace/rpa_projects
cat /workspace/rpa_projects/.snapshot_commit
```

### Q: 任务执行超时？

**A**: 
- 调整 SnailJob 任务超时时间
- 检查 Playwright 脚本是否有长时间等待
- 考虑拆分为多个小任务

### Q: 虚拟环境创建失败？

**A**: 
- 确认磁盘空间充足
- 检查 Python 版本 (需要 3.12+)
- 查看详细错误日志
- 检查文件系统权限
- Windows 环境需要管理员权限

### Q: 如何清理虚拟环境？

**A**: 
```bash
# 清理所有虚拟环境（会自动重建）
rm -rf workspace/venvs/*

# 仅清理某个 service 的环境
rm -rf workspace/venvs/app_services_xxx_venv

# 清理共享基础环境（会触发重建）
rm -rf workspace/venvs/_shared_base
```

### Q: main.py 中未找到 run() 方法？

**A**: 
- 确保 `main.py` 中定义了 `run(extra_params: dict = None) -> int`
- 检查方法签名是否正确
- 确认文件编码为 UTF-8

## Playwright 相关

### Q: 浏览器启动失败？

**A**: 
- 确认已安装 Playwright 浏览器：`playwright install chromium`
- Docker 环境确认镜像中已包含浏览器依赖
- 检查系统依赖是否完整

### Q: 如何处理文件上传/下载？

**A**: 
```python
# 文件上传
file_path = Path(__file__).parent / "data.csv"
page.set_input_files("input[type='file']", str(file_path))

# 文件下载
with page.expect_download() as download_info:
    page.click("a#download-link")
download = download_info.value
download.save_as("/path/to/save/file")
```

## 日志相关

### Q: 日志没有上报到 SnailJob？

**A**: 
- 确认使用的是 `sj.SnailLog.AUTO` 或 `sj.SnailLog.REMOTE`
- 检查 SnailJob 服务器连接是否正常
- 查看执行器日志中是否有上报错误

### Q: 如何查看完整日志？

**A**: 
- **SnailJob 后台**: 查看任务执行日志
- **Docker**: `docker-compose logs -f`
- **本地**: 日志输出到控制台

---

# 最佳实践

## 代码规范

1. ✅ **错误处理**: 总是捕获异常并记录详细日志
2. ✅ **参数验证**: 在 `run()` 方法开始时验证必需参数
3. ✅ **资源清理**: 确保浏览器等资源正确关闭
4. ✅ **日志详细**: 记录关键步骤，便于问题排查

## 性能优化

1. ✅ **幂等性**: 脚本应该支持重复执行而不产生副作用
2. ✅ **超时控制**: 为长时间操作设置合理的超时时间
3. ✅ **依赖缓存**: 利用 MD5 缓存机制，避免重复安装依赖
4. ✅ **浏览器复用**: 考虑在多次操作中复用浏览器实例


---

# 技术栈

- **Python 3.10+**: 主要开发语言
- **SnailJob**: 分布式任务调度平台
- **Playwright**: 浏览器自动化框架
- **git CLI**: Git 仓库拉取与快照导出（`fetch` + `archive`）
- **Docker**: 容器化部署

---

# 相关链接

- [SnailJob 官网](https://snailjob.opensnail.com)
- [SnailJob 仓库](https://gitee.com/aizuda/snail-job)
- [Playwright 文档](https://playwright.dev/python/)
