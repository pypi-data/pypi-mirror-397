"""
维格表工具函数

兼容原vika.py库的工具函数
"""
import re
import json
from typing import Dict, Any, Optional, Union, Iterator, Coroutine
from urllib.parse import urlparse, parse_qs
from functools import wraps, lru_cache
import time
import asyncio
import os
from collections import OrderedDict
from .exceptions import create_exception_from_response, ParameterException
from .const import DEFAULT_API_BASE

def _get_allowed_hosts() -> set:
    """
    获取允许的主机集合（严格匹配）。
    来源优先级：环境变量 VIKA_API_BASE > 常量 DEFAULT_API_BASE。
    安全：仅当 URL 主机与集合成员严格相等时才认为可信，避免后缀/模糊匹配带来的风险。
    """
    hosts = set()

    def _add(url: str):
        if not url:
            return
        # 标准化：去除尾部斜杠，主机名小写
        parsed = urlparse(url.rstrip('/'))
        host = parsed.netloc or parsed.path  # 兼容无scheme的主机写法
        if host:
            hosts.add(host.lower())

    env_base = os.getenv("VIKA_API_BASE")
    if env_base:
        _add(env_base)

    _add(DEFAULT_API_BASE)

    return hosts


def get_dst_id(dst_id_or_url: str) -> str:
    """
    从数据表ID或URL中提取数据表ID，并校验URL主机与路径片段。
    - 仅接受与 DEFAULT_API_BASE 同主机的URL
    - 路径应包含 /datasheet/ 语义（或通过查询参数 ?dst= 提供）
    """
    if not dst_id_or_url:
        raise ParameterException("dst_id_or_url cannot be empty")

    # URL 分支
    if dst_id_or_url.startswith('http'):
        parsed_url = urlparse(dst_id_or_url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ParameterException(f"Invalid URL format: {dst_id_or_url}")

        allowed_hosts = _get_allowed_hosts()
        host = parsed_url.netloc.lower()
        if host not in allowed_hosts:
            raise ParameterException(f"Untrusted host: {parsed_url.netloc}")

        path_lower = parsed_url.path.lower()
        path_parts = parsed_url.path.split('/')

        # 优先从查询参数中提取
        query_params = parse_qs(parsed_url.query)
        if 'dst' in query_params:
            candidate = query_params['dst'][0]
            if not candidate.startswith('dst'):
                raise ParameterException("Invalid datasheet id in query parameter")
            return candidate

        # 路径需具备 datasheet 语义
        if 'datasheet' not in path_lower and 'datasheets' not in path_lower:
            raise ParameterException("URL path not valid for datasheet")

        # 从路径段提取
        for part in path_parts:
            if part.startswith('dst'):
                return part

        raise ParameterException(f"Cannot extract datasheet ID from URL: {dst_id_or_url}")

    # 纯ID分支：验证格式
    if not dst_id_or_url.startswith('dst'):
        raise ParameterException(f"Invalid datasheet ID format: {dst_id_or_url}")

    return dst_id_or_url


def get_space_id(space_id_or_url: str) -> str:
    """
    从空间ID或URL中提取空间ID，并校验URL主机与路径片段。
    - 仅接受与 DEFAULT_API_BASE 同主机的URL
    - 路径应包含 /space/ 语义
    """
    if not space_id_or_url:
        raise ParameterException("space_id_or_url cannot be empty")

    if space_id_or_url.startswith('http'):
        parsed_url = urlparse(space_id_or_url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ParameterException(f"Invalid URL format: {space_id_or_url}")

        allowed_hosts = _get_allowed_hosts()
        host = parsed_url.netloc.lower()
        if host not in allowed_hosts:
            raise ParameterException(f"Untrusted host: {parsed_url.netloc}")

        path_lower = parsed_url.path.lower()
        path_parts = parsed_url.path.split('/')

        if 'space' not in path_lower and 'spaces' not in path_lower:
            raise ParameterException("URL path not valid for space")

        for part in path_parts:
            if part.startswith('spc'):
                return part

        raise ParameterException(f"Cannot extract space ID from URL: {space_id_or_url}")

    if not space_id_or_url.startswith('spc'):
        raise ParameterException(f"Invalid space ID format: {space_id_or_url}")

    return space_id_or_url


def handle_response(response_data: Dict[str, Any], status_code: int = 200) -> Dict[str, Any]:
    """
    处理API响应
    
    Args:
        response_data: 响应数据
        status_code: HTTP状态码
        
    Returns:
        处理后的响应数据
        
    Raises:
        VikaException: 当响应包含错误时
    """
    # 检查HTTP状态码
    if status_code >= 400:
        raise create_exception_from_response(response_data, status_code)
    
    # 检查API响应中的success字段
    if not response_data.get('success', True):
        error_code = response_data.get('code', status_code)
        raise create_exception_from_response(response_data, error_code)
    
    return response_data


def timed_lru_cache(seconds: int = 300, maxsize: int = 128):
    """
    带时间过期的LRU缓存装饰器，支持同步和异步函数
    
    Args:
        seconds: 缓存过期时间（秒）
        maxsize: 最大缓存条目数
    """
    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            # async 版本：使用 OrderedDict 实现 LRU，缓存 Task 而不是协程对象
            cache = OrderedDict()
            cache_times = {}
            lock = asyncio.Lock()
            
            def _make_key(args, kwargs):
                """创建缓存键"""
                return (args, tuple(sorted(kwargs.items())))
            
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                key = _make_key(args, kwargs)
                now = time.time()
                task = None
                
                async with lock:
                    # 检查缓存是否有效
                    if key in cache and key in cache_times:
                        if now - cache_times[key] < seconds:
                            cached_task = cache[key]
                            if not cached_task.done() or cached_task.exception() is None:
                                task = cached_task
                                # 移动到末尾（LRU）
                                cache.move_to_end(key)
                    
                    if task is None:
                        # 创建新的 Task
                        task = asyncio.create_task(func(*args, **kwargs))
                        cache[key] = task
                        cache_times[key] = now
                        
                        # 容量控制：移除最旧的条目
                        while len(cache) > maxsize:
                            oldest_key = next(iter(cache))
                            del cache[oldest_key]
                            if oldest_key in cache_times:
                                del cache_times[oldest_key]
                
                # 在锁外等待 Task
                try:
                    return await task
                except Exception:
                    # 异常时清除缓存
                    async with lock:
                        if key in cache and cache[key] is task:
                            del cache[key]
                        if key in cache_times:
                            del cache_times[key]
                    raise
            
            async def async_cache_clear():
                """清除所有缓存（异步版本）"""
                async with lock:
                    cache.clear()
                    cache_times.clear()
            
            def cache_clear():
                """清除所有缓存（同步版本）"""
                # 如果在事件循环中调用，需要使用异步版本
                try:
                    loop = asyncio.get_running_loop()
                    # 在事件循环中，创建任务但不等待
                    asyncio.create_task(async_cache_clear())
                except RuntimeError:
                    # 不在事件循环中，直接清空（不需要锁）
                    cache.clear()
                    cache_times.clear()
            
            def cache_info():
                """返回缓存信息"""
                return {
                    'hits': 0,  # 简化实现，不统计命中次数
                    'misses': 0,
                    'maxsize': maxsize,
                    'currsize': len(cache)
                }
            
            async_wrapper.cache_clear = cache_clear  # type: ignore[attr-defined]
            async_wrapper.cache_info = cache_info  # type: ignore[attr-defined]
            return async_wrapper
        else:
            # 同步版本：保持现有逻辑
            func = lru_cache(maxsize=maxsize)(func)
            func.lifetime = seconds  # type: ignore[attr-defined]
            func.expiration = time.time() + seconds  # type: ignore[attr-defined]
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                if time.time() >= func.expiration:  # type: ignore[attr-defined]
                    func.cache_clear()
                    func.expiration = time.time() + func.lifetime  # type: ignore[attr-defined]
                return func(*args, **kwargs)
            
            wrapper.cache_info = func.cache_info  # type: ignore[attr-defined]
            wrapper.cache_clear = func.cache_clear  # type: ignore[attr-defined]
            return wrapper
    
    return decorator


def validate_field_key(field_key: Optional[str]) -> str:
    """
    验证字段键类型
    
    Args:
        field_key: 字段键类型
        
    Returns:
        验证后的字段键类型
    """
    if field_key is None:
        return "name"
    
    if field_key not in ["name", "id"]:
        raise ParameterException(f"field_key must be 'name' or 'id', got: {field_key}")
    
    return field_key


def validate_cell_format(cell_format: Optional[str]) -> str:
    """
    验证单元格格式
    
    Args:
        cell_format: 单元格格式
        
    Returns:
        验证后的单元格格式
    """
    if cell_format is None:
        return "json"
    
    if cell_format not in ["json", "string"]:
        raise ParameterException(f"cell_format must be 'json' or 'string', got: {cell_format}")
    
    return cell_format


def build_api_url(base_url: str, endpoint: str) -> str:
    """
    构建API URL
    
    Args:
        base_url: 基础URL
        endpoint: API端点
        
    Returns:
        完整的API URL
    """
    base_url = base_url.rstrip('/')
    endpoint = endpoint.lstrip('/')
    return f"{base_url}/{endpoint}"


def format_records_for_api(records: list, field_key: str = "name") -> list:
    """
    格式化记录数据以符合API要求
    
    Args:
        records: 记录列表
        field_key: 字段键类型
        
    Returns:
        格式化后的记录列表
    """
    formatted_records = []
    
    for record in records:
        if isinstance(record, dict):
            if 'fields' in record:
                # 已经是正确格式
                formatted_records.append(record)
            else:
                # 需要包装为fields结构
                formatted_records.append({"fields": record})
        else:
            raise ParameterException("Record must be a dictionary")
    
    return formatted_records


def safe_json_loads(data: str, default: Any = None) -> Any:
    """
    安全的JSON解析
    
    Args:
        data: JSON字符串
        default: 解析失败时的默认值
        
    Returns:
        解析结果或默认值
    """
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return default


def chunk_list(lst: list, chunk_size: int) -> Iterator[list]:
    """
    将列表分块
    
    Args:
        lst: 要分块的列表
        chunk_size: 块大小
        
    Yields:
        分块后的子列表
    """
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]


# 异步工具函数
def run_sync(coro: Coroutine[Any, Any, Any]) -> Any:
    """
    在同步代码中运行异步协程
    
    Args:
        coro: 协程对象
        
    Returns:
        协程执行结果
    """
    # 禁止在活跃事件循环中同步运行以避免死锁/不可预期行为
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        # 无事件循环在运行，使用一次性的 asyncio.run
        return asyncio.run(coro)
    else:
        raise RuntimeError("run_sync() cannot be called within a running event loop; use the async API (await the coroutine)")


__all__ = [
    'get_dst_id',
    'get_space_id', 
    'handle_response',
    'timed_lru_cache',
    'validate_field_key',
    'validate_cell_format',
    'build_api_url',
    'format_records_for_api',
    'safe_json_loads',
    'chunk_list',
    'run_sync'
]
