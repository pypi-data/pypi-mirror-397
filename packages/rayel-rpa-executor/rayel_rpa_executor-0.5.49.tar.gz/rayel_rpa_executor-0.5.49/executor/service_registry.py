"""
服务注册表：扫描 rpa_projects/app/services/**/main.py 里带 @service(id="...", name="...") 的 Service 类，
并生成可用于动态注册的执行器描述信息。

注意：
- 必须使用 AST 静态解析，禁止 import 业务代码（避免依赖冲突、避免执行副作用）。
- 支持中文 name。
"""

from __future__ import annotations

import ast
import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import snailjob as sj


@dataclass(frozen=True)
class ServiceDescriptor:
    service_folder: str
    service_id: str
    service_name: str
    executor_name: str
    main_file: Path


def _parse_service_decorator(dec: ast.AST) -> Optional[Tuple[str, str]]:
    """
    判断装饰器是否形如：service(id="HR-000001", name="打开百度任务")
    返回 (service_id, service_name)，否则返回 None
    """
    if not isinstance(dec, ast.Call):
        return None

    func = dec.func
    func_name = None
    if isinstance(func, ast.Name):
        func_name = func.id
    elif isinstance(func, ast.Attribute):
        # 兼容：xxx.service(...)
        func_name = func.attr

    if func_name != "service":
        return None

    service_id: Optional[str] = None
    service_name: Optional[str] = None
    for kw in dec.keywords or []:
        if kw.arg in ("id", "name") and isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
            if kw.arg == "id":
                service_id = kw.value.value.strip()
            elif kw.arg == "name":
                service_name = kw.value.value.strip()

    # 两个字段都必填且非空
    if not service_id or not service_name:
        return None
    return service_id, service_name


def _extract_service_meta_from_main(main_py: Path) -> Optional[Tuple[str, str]]:
    """
    从 main.py 里提取 Service 的 @service(id="...", name="...")。
    找不到则返回 None。
    """
    try:
        source = main_py.read_text(encoding="utf-8")
    except Exception:
        # 兜底：某些文件可能不是 utf-8
        source = main_py.read_text(encoding="utf-8", errors="ignore")

    try:
        tree = ast.parse(source, filename=str(main_py))
    except SyntaxError:
        return None

    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "Service":
            for dec in node.decorator_list:
                meta = _parse_service_decorator(dec)
                if meta is not None:
                    return meta
            return None
    return None


def _iter_service_main_files(repo_root: Path) -> Iterable[Path]:
    services_dir = repo_root / "app" / "services"
    if not services_dir.exists():
        return []
    # 只扫描 services 下的 main.py，避免扫到 __pycache__ 等
    return [
        p
        for p in services_dir.rglob("main.py")
        if p.is_file() and "__pycache__" not in p.parts
    ]


def build_executor_name(service_id: str, service_name: str) -> str:
    """
    executorName 生成规则（按用户需求）：
    - 两字段必填：service_id + service_name
    - executorName 永远使用：{id}-{name}
    """
    return f"{service_id}-{service_name}"


def resolve_executor_name_conflicts(
    descriptors: List[ServiceDescriptor],
) -> List[ServiceDescriptor]:
    """
    解决 executorName 冲突：
    - 正常情况下 service_id 保证唯一，因此冲突应当极少出现。
    - 如果仍发生冲突（同名 executorName 或重复 id），保留第一个，跳过其余重复项避免覆盖。
    """
    by_name: Dict[str, List[ServiceDescriptor]] = {}
    by_id: Dict[str, List[ServiceDescriptor]] = {}
    for d in descriptors:
        by_name.setdefault(d.executor_name, []).append(d)
        by_id.setdefault(d.service_id, []).append(d)

    # 先按 id 去重（更符合“唯一且不变”）
    id_dedup: List[ServiceDescriptor] = []
    for sid, group in by_id.items():
        keep = sorted(group, key=lambda x: x.service_folder)[0]
        id_dedup.append(keep)

    # 再按 executorName 去重
    by_name2: Dict[str, List[ServiceDescriptor]] = {}
    for d in id_dedup:
        by_name2.setdefault(d.executor_name, []).append(d)

    resolved: List[ServiceDescriptor] = []
    for name, group in by_name2.items():
        keep = sorted(group, key=lambda x: x.service_folder)[0]
        resolved.append(keep)

    return resolved


class ServiceScanner:
    """
    带缓存的扫描器：每次扫描只解析变更过的 main.py，降低 1000+ 服务的开销。
    """

    def __init__(self):
        # main_file -> (mtime_ns, descriptor or None)
        self._cache: Dict[str, Tuple[int, Optional[ServiceDescriptor]]] = {}

    def scan(self, repo_root: Path) -> List[ServiceDescriptor]:
        main_files = list(_iter_service_main_files(repo_root))
        seen: set[str] = set()
        results: List[ServiceDescriptor] = []

        for main_py in main_files:
            key = str(main_py)
            seen.add(key)
            try:
                mtime_ns = main_py.stat().st_mtime_ns
            except FileNotFoundError:
                continue

            cached = self._cache.get(key)
            if cached and cached[0] == mtime_ns:
                desc = cached[1]
                if desc is not None:
                    results.append(desc)
                continue

            meta = _extract_service_meta_from_main(main_py)
            if not meta:
                self._cache[key] = (mtime_ns, None)
                continue

            service_folder = main_py.parent.name
            service_id, service_name = meta
            executor_name = build_executor_name(service_id, service_name)
            desc = ServiceDescriptor(
                service_folder=service_folder,
                service_id=service_id,
                service_name=service_name,
                executor_name=executor_name,
                main_file=main_py,
            )
            self._cache[key] = (mtime_ns, desc)
            results.append(desc)

        # 清理被删除的文件缓存
        removed = [k for k in self._cache.keys() if k not in seen]
        for k in removed:
            self._cache.pop(k, None)

        return results


def compute_fingerprint(descriptors: List[ServiceDescriptor]) -> str:
    """
    计算稳定指纹：用于判断是否需要重新上报 executors。
    """
    md5 = hashlib.md5()
    for d in sorted(descriptors, key=lambda x: x.executor_name):
        line = f"{d.executor_name}|{d.service_id}|{d.service_folder}|{d.service_name}"
        md5.update(line.encode("utf-8"))
        md5.update(b"\n")
    return md5.hexdigest()


def build_thin_wrapper_job_method(
    *,
    executor_name: str,
    service_folder: str,
    default_branch: str,
    default_workspace_root: str,
):
    """
    构建“薄包装”执行器：把后端传来的 jobParams（A 语义：仅业务参数）
    注入为 extra_params，并转调现有通用执行器 executor.playwright_executor。
    """

    def _coerce_extra_params(raw):
        if raw is None:
            return None
        if isinstance(raw, dict):
            return raw
        if isinstance(raw, str):
            try:
                return json.loads(raw)
            except Exception:
                return {"_raw": raw}
        # 兜底：任意类型
        return {"value": raw}

    @sj.job(executor_name)
    def _wrapper(args: sj.JobArgs) -> sj.ExecuteResult:
        # 延迟导入，避免循环依赖
        from dataclasses import replace

        from executor import executor as generic_executor

        extra_params = _coerce_extra_params(args.job_params)

        injected = {
            "service_folder": service_folder,
            "branch": default_branch,
            "workspace_root": default_workspace_root,
            "extra_params": extra_params,
        }

        new_args = replace(args, job_params=injected)
        return generic_executor.playwright_executor(new_args)

    # 保险：即使未来不走 @sj.job 也能识别到名称
    _wrapper.executor_name = executor_name
    return _wrapper


def get_defaults_from_env() -> Tuple[str, str]:
    """
    wrapper 注入默认 branch/workspace_root 的来源。
    - EXECUTOR_GIT_BRANCH: 默认 main
    - EXECUTOR_WORKSPACE_ROOT: 默认 ./workspace
    """
    branch = os.getenv("EXECUTOR_GIT_BRANCH", "main")
    workspace_root = os.getenv("EXECUTOR_WORKSPACE_ROOT", "./workspace")
    return branch, workspace_root


