# API 鉴权使用指南

## 📋 概述

文件下载 API 使用 **API Key 鉴权**，这是 FastAPI 中最适合内部服务的鉴权方式。

## 🔑 API Key 配置

### 方式 1: 环境变量配置（推荐）

```bash
# 设置主 API Key
export API_KEY="your-secure-api-key-here"

# 可选：设置额外的 API Keys（逗号分隔）
export EXTRA_API_KEYS="key1,key2,key3"
```

### 方式 2: Docker 环境变量

```dockerfile
# Dockerfile
ENV API_KEY=your-secure-api-key-here

# 或在 docker-compose.yml
environment:
  - API_KEY=your-secure-api-key-here
  - EXTRA_API_KEYS=key1,key2,key3
```

### 方式 3: 生成安全的 API Key

```python
# 使用 Python 生成安全的 API Key
import secrets
api_key = secrets.token_urlsafe(32)
print(api_key)
# 输出示例: vT2xZHqM9kN8fR5wP3jL7aB1dC6eG4hI0oY8uX2qS9t
```

### ⚠️ 未配置警告

如果未设置 `API_KEY` 环境变量，系统会：
- 自动生成一个临时 API Key
- 在控制台打印警告信息和临时 Key
- **仅用于开发测试，生产环境必须配置！**

## 🚀 使用方式

### 1. curl 请求

```bash
# 下载文件
curl -H "X-API-Key: your-api-key-here" \
     "http://localhost:8000/api/file/download?path=/app/data/videos/file.zip" \
     -O

# 列出文件
curl -H "X-API-Key: your-api-key-here" \
     "http://localhost:8000/api/file/list?path=/app/data/videos"
```

### 2. Python requests

```python
import requests

# 配置 API Key
headers = {"X-API-Key": "your-api-key-here"}

# 下载文件
response = requests.get(
    "http://localhost:8000/api/file/download",
    params={"path": "/app/data/videos/file.zip"},
    headers=headers
)

# 列出文件
response = requests.get(
    "http://localhost:8000/api/file/list",
    params={"path": "/app/data/videos"},
    headers=headers
)
data = response.json()
```

### 3. JavaScript/TypeScript

```javascript
// 使用 fetch
const headers = {
  'X-API-Key': 'your-api-key-here'
};

// 下载文件
fetch('http://localhost:8000/api/file/download?path=/app/data/videos/file.zip', {
  headers: headers
})
.then(response => response.blob())
.then(blob => {
  // 处理下载的文件
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'file.zip';
  a.click();
});

// 列出文件
fetch('http://localhost:8000/api/file/list?path=/app/data/videos', {
  headers: headers
})
.then(response => response.json())
.then(data => console.log(data));
```

### 4. Postman

1. 打开 Postman
2. 新建请求
3. 在 **Headers** 标签页添加：
   - Key: `X-API-Key`
   - Value: `your-api-key-here`
4. 发送请求

### 5. Swagger UI

访问 `http://localhost:8000/docs`，在页面右上角：
1. 点击 **Authorize** 按钮
2. 输入你的 API Key
3. 点击 **Authorize**
4. 现在可以直接在页面测试 API

## 🔒 安全特性

### 多层防护

| 防护层 | 说明 |
|--------|------|
| **API Key 鉴权** | 请求头必须包含有效的 X-API-Key |
| **路径限制** | 只能访问 /app/data 和 /app/logs 目录 |
| **路径遍历防护** | 自动防止 ../ 等攻击 |
| **文件验证** | 验证文件存在性和类型 |
| **详细日志** | 记录所有访问和失败尝试 |

### 鉴权错误响应

**401 未授权 - 缺少 API Key**
```json
{
  "detail": "缺少 API Key，请在请求头中添加 X-API-Key"
}
```

**401 未授权 - 无效的 API Key**
```json
{
  "detail": "无效的 API Key"
}
```

## 🎯 最佳实践

### 1. 生产环境
✅ **必须设置 API_KEY 环境变量**
```bash
export API_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
```

✅ **不要在代码中硬编码 API Key**

✅ **定期轮换 API Key**

✅ **使用 HTTPS 加密传输**

### 2. 开发环境
✅ **使用 .env 文件管理 API Key**
```bash
# .env
API_KEY=dev-api-key-for-testing
```

✅ **不要提交 API Key 到 Git**

### 3. 多客户端场景
如果需要为不同客户端分配不同的 API Key：

```bash
# 设置主 Key
export API_KEY=main-key

# 设置额外的 Keys（逗号分隔）
export EXTRA_API_KEYS=client1-key,client2-key,client3-key
```

然后在代码中使用 `verify_api_key_multi` 函数：

```python
from routes.auth import verify_api_key_multi

@router.get("/download")
async def download_file(
    path: str = Query(...),
    api_key: str = Depends(verify_api_key_multi)  # 使用多 Key 验证
):
    # ...
```

## 📊 监控和日志

### 成功的请求
```
[鉴权][成功] API Key 验证通过
[文件下载][请求] /app/data/videos/file.zip
[文件下载][安全检查] 通过: /app/data/videos/file.zip
[文件下载][开始] file.zip (/app/data/videos/file.zip)
```

### 失败的请求
```
[鉴权][失败] 缺少 API Key
[鉴权][失败] API Key 无效: abcdefghij...
[文件下载][拒绝] 路径不安全或文件不存在: /etc/passwd
```

## 🔧 故障排查

### 问题 1: 401 未授权
**原因**: 未提供或 API Key 无效

**解决**:
1. 检查是否设置了 `API_KEY` 环境变量
2. 检查请求头是否包含 `X-API-Key`
3. 检查 API Key 是否正确

### 问题 2: 403 禁止访问
**原因**: 尝试访问不允许的路径

**解决**:
1. 确保路径以 `/app/data` 或 `/app/logs` 开头
2. 检查文件是否存在

### 问题 3: 如何查看当前 API Key
启动服务时查看日志：
```
⚠️  使用临时 API Key: vT2xZHqM9kN8fR5wP3jL7aB1dC6eG4hI0oY8uX2qS9t
```

或者在代码中：
```python
from routes.auth import DEFAULT_API_KEY
print(DEFAULT_API_KEY)
```

## 📝 API 完整示例

```bash
# 1. 设置 API Key
export API_KEY="my-secure-api-key-12345"

# 2. 启动服务
python main.py

# 3. 下载文件
curl -H "X-API-Key: my-secure-api-key-12345" \
     "http://localhost:8000/api/file/download?path=/app/data/videos/recording.mp4" \
     -o recording.mp4

# 4. 列出目录
curl -H "X-API-Key: my-secure-api-key-12345" \
     "http://localhost:8000/api/file/list?path=/app/data/videos" \
     | jq

# 5. 无效的请求（缺少 API Key）
curl "http://localhost:8000/api/file/download?path=/app/data/videos/file.zip"
# 响应: {"detail": "缺少 API Key，请在请求头中添加 X-API-Key"}

# 6. 无效的请求（错误的 API Key）
curl -H "X-API-Key: wrong-key" \
     "http://localhost:8000/api/file/download?path=/app/data/videos/file.zip"
# 响应: {"detail": "无效的 API Key"}
```

## 🌟 进阶功能

### 自定义鉴权逻辑

如需更复杂的鉴权（如 JWT、OAuth2），可以修改 `routes/auth.py`：

```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

security = HTTPBearer()

async def verify_jwt_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="无效的 Token")
```

### IP 白名单

```python
from fastapi import Request

ALLOWED_IPS = {"127.0.0.1", "10.0.0.1"}

async def verify_ip(request: Request):
    client_ip = request.client.host
    if client_ip not in ALLOWED_IPS:
        raise HTTPException(status_code=403, detail="IP 未授权")
    return client_ip
```

### 速率限制

使用 `slowapi` 库限制请求频率：

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.get("/download")
@limiter.limit("10/minute")
async def download_file(...):
    # ...
```
