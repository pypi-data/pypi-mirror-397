"""
API 鉴权模块

使用 API Key 进行身份验证
"""
import os
import secrets
from typing import Optional

from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

from executor.logger import logger

# API Key 配置
API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# 从环境变量获取 API Key，如果未设置则生成默认值
# 生产环境必须设置 API_KEY 环境变量
DEFAULT_API_KEY = os.getenv("API_KEY", "")

# 如果没有配置 API_KEY，生成一个临时的并提示警告
if not DEFAULT_API_KEY:
    DEFAULT_API_KEY = secrets.token_urlsafe(32)
    logger.LOCAL.warning("=" * 60)
    logger.LOCAL.warning("⚠️  未配置 API_KEY 环境变量！")
    logger.LOCAL.warning(f"⚠️  使用临时 API Key: {DEFAULT_API_KEY}")
    logger.LOCAL.warning("⚠️  生产环境请务必设置 API_KEY 环境变量！")
    logger.LOCAL.warning("=" * 60)
else:
    logger.LOCAL.info(f"[鉴权][配置] API Key 已加载 (长度: {len(DEFAULT_API_KEY)})")


async def verify_api_key(api_key: Optional[str] = Security(api_key_header)) -> str:
    """
    验证 API Key
    
    Args:
        api_key: 从请求头获取的 API Key
        
    Returns:
        验证通过的 API Key
        
    Raises:
        HTTPException: 401 未授权
    """
    if not api_key:
        logger.LOCAL.warning("[鉴权][失败] 缺少 API Key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="权限校验失败",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    # 验证 API Key
    if api_key != DEFAULT_API_KEY:
        logger.LOCAL.warning(f"[鉴权][失败] API Key 无效: {api_key[:10]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="权限校验失败",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    logger.LOCAL.debug("[鉴权][成功] API Key 验证通过")
    return api_key


def generate_api_key() -> str:
    """
    生成安全的 API Key
    
    Returns:
        新的 API Key（URL 安全的 Base64 编码）
    """
    return secrets.token_urlsafe(32)


# 可选：支持多个 API Key（用于不同的客户端）
VALID_API_KEYS = set()

# 从环境变量加载额外的 API Keys（逗号分隔）
extra_keys = os.getenv("EXTRA_API_KEYS", "")
if extra_keys:
    VALID_API_KEYS.update(key.strip() for key in extra_keys.split(",") if key.strip())
    logger.LOCAL.info(f"[鉴权][配置] 加载了 {len(VALID_API_KEYS)} 个额外 API Key")


async def verify_api_key_multi(api_key: Optional[str] = Security(api_key_header)) -> str:
    """
    验证 API Key（支持多个有效 Key）
    
    适用于多客户端场景
    
    Args:
        api_key: 从请求头获取的 API Key
        
    Returns:
        验证通过的 API Key
        
    Raises:
        HTTPException: 401 未授权
    """
    if not api_key:
        logger.LOCAL.warning("[鉴权][失败] 缺少 API Key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="权限校验失败",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    # 验证 API Key（支持主 Key 和额外 Keys）
    if api_key != DEFAULT_API_KEY and api_key not in VALID_API_KEYS:
        logger.LOCAL.warning(f"[鉴权][失败] API Key 无效: {api_key[:10]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="权限校验失败",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    logger.LOCAL.debug("[鉴权][成功] API Key 验证通过")
    return api_key
