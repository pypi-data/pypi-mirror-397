"""
文件下载 API

提供安全的文件下载接口，限制只能下载 /app/data 和 /app/logs 和 /data/snail-job-executor 目录下的文件
"""
from pathlib import Path
from typing import Optional
from urllib.parse import unquote

from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import FileResponse

from executor.logger import logger
from routes.auth import verify_api_key

router = APIRouter(prefix="/api/file", tags=["文件下载"])

# 允许下载的根目录（安全限制）
ALLOWED_BASE_DIR_DATA = Path("/app/data").resolve()
ALLOWED_BASE_DIR_LOGS = Path("/app/logs").resolve()
ALLOWED_BASE_DIR_DATA_2 = Path("/data/snail-job-executor/data").resolve()
ALLOWED_BASE_DIR_LOGS_2 = Path("/data/snail-job-executor/logs").resolve()


def is_safe_path(file_path: str) -> tuple[bool, Optional[Path]]:
    """
    检查文件路径是否安全
    
    Args:
        file_path: 要检查的文件路径
        
    Returns:
        (是否安全, 解析后的路径)
    """
    try:
        # URL 解码（处理双重编码问题）
        decoded_path = unquote(file_path)
        logger.LOCAL.debug(f"[文件下载][URL解码] {file_path} -> {decoded_path}")
        
        # 解析为绝对路径
        target_path = Path(decoded_path).resolve()
        
        # 检查是否在允许的目录下
        if not str(target_path).startswith(str(ALLOWED_BASE_DIR_DATA)) \
            and not str(target_path).startswith(str(ALLOWED_BASE_DIR_LOGS)) \
                and not str(target_path).startswith(str(ALLOWED_BASE_DIR_DATA_2)) \
                    and not str(target_path).startswith(str(ALLOWED_BASE_DIR_LOGS_2)):
            logger.LOCAL.warning(f"[文件下载][安全检查] 拒绝访问: {file_path} (不在允许目录内)")
            return False, None
        
        # 检查文件是否存在
        if not target_path.exists():
            logger.LOCAL.warning(f"[文件下载][安全检查] 文件不存在: {file_path}")
            return False, None
        
        # 检查是否为文件（不是目录）
        if not target_path.is_file():
            logger.LOCAL.warning(f"[文件下载][安全检查] 不是文件: {file_path}")
            return False, None
        
        logger.LOCAL.info(f"[文件下载][安全检查] 通过: {target_path}")
        return True, target_path
        
    except Exception as e:
        logger.LOCAL.error(f"[文件下载][安全检查] 异常: {e}")
        return False, None


@router.get("/download")
async def download_file(
    path: str = Query(..., description="文件完整路径，例如: /app/data/videos/file.zip"),
    api_key: str = Depends(verify_api_key)
):
    """
    下载文件
    
    **鉴权**：
    - 需要在请求头中添加 X-API-KEY
    
    **安全限制**：
    - 只能下载 /app/data 或 /app/logs 目录下的文件
    - 自动防止路径遍历攻击（如 ../ 等）
    - 验证文件存在性
    
    **示例**：
    - GET /api/file/download?path=/app/data/videos/job-3_task-5436_20251126002523290.zip
    - Header: X-API-KEY: your_api_key_here
    
    Args:
        path: 要下载的文件完整路径
        
    Returns:
        文件响应流
        
    Raises:
        HTTPException: 
            - 400: 路径不安全或文件不存在
            - 403: 无权限访问该路径
            - 500: 服务器内部错误
    """
    logger.LOCAL.info(f"[文件下载][请求] {path}")
    
    # 安全检查
    is_safe, target_path = is_safe_path(path)
    
    if not is_safe:
        logger.LOCAL.error(f"[文件下载][拒绝] 路径不安全或文件不存在: {path}")
        raise HTTPException(
            status_code=403,
            detail=f"无权限访问该路径或文件不存在。"
        )
    
    try:
        # 获取文件名
        filename = target_path.name
        
        logger.LOCAL.info(f"[文件下载][开始] {filename} ({target_path})")
        
        # 返回文件
        return FileResponse(
            path=str(target_path),
            filename=filename,
            media_type="application/octet-stream"
        )
        
    except Exception as e:
        logger.LOCAL.error(f"[文件下载][失败] {e}")
        raise HTTPException(
            status_code=500,
            detail=f"文件下载失败: {str(e)}"
        )


@router.get("/list")
async def list_files(
    path: str = Query("", description="路径，例如: /app/data/videos"),
    api_key: str = Depends(verify_api_key)
):
    """
    列出指定目录下的文件
    
    **鉴权**：
    - 需要在请求头中添加 X-API-KEY
    
    **安全限制**：
    - 只能列出 /app/data 或 /app/logs 目录下的内容
    
    **示例**：
    - GET /api/file/list?path=/app/data/videos
    - GET /api/file/list?path=/app/logs
    - Header: X-API-KEY: your_api_key_here
    
    Args:
        path: 路径（相对于 /app/data）
        
    Returns:
        文件列表
    """
    # 构建目标路径
    if not path:
        raise HTTPException(
            status_code=400,
            detail="路径不能为空"
        )
        
    
    # 解析为绝对路径并检查安全性
    try:
        # URL 解码（处理双重编码问题）
        decoded_path = unquote(path)
        target_path = Path(decoded_path).resolve()
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail="解析路径失败"
        )
    
    if not str(target_path).startswith(str(ALLOWED_BASE_DIR_DATA)) \
        and not str(target_path).startswith(str(ALLOWED_BASE_DIR_LOGS)) \
            and not str(target_path).startswith(str(ALLOWED_BASE_DIR_DATA_2)) \
                and not str(target_path).startswith(str(ALLOWED_BASE_DIR_LOGS_2)):
        raise HTTPException(
            status_code=403,
            detail="无权限访问该路径"
        )
    
    if not target_path.exists():
        raise HTTPException(
            status_code=404,
            detail="目录不存在"
        )
    
    if not target_path.is_dir():
        raise HTTPException(
            status_code=400,
            detail="不是目录"
        )
    
    try:
        files = []
        for item in target_path.iterdir():
            files.append({
                "name": item.name,
                "path": str(item),
                "type": "file" if item.is_file() else "directory",
                "size": item.stat().st_size if item.is_file() else 0,
            })
        
        logger.LOCAL.info(f"[文件下载][列表] {target_path} (共 {len(files)} 项)")
        
        return {
            "directory": str(target_path),
            "count": len(files),
            "items": files
        }
        
    except Exception as e:
        logger.LOCAL.error(f"[文件下载][列表失败] {e}")
        raise HTTPException(
            status_code=500,
            detail=f"列出文件失败: {str(e)}"
        )
