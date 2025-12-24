"""
缓存模块 - 配置
"""
import os
from typing import Any
from .base import Cache
from .redis_cache import RedisCache
from .file import FileCache
from .memory import MemoryCache

_config: dict = {
    "backend": "auto",
    "default_ttl": 300,
    "memory_capacity": 1000,
    "file_dir": None,
    "file_max_items": 10000,
    "redis_url": None,
}

_instance: Cache | None = None

def configure(options: dict | None = None):
    """
    配置缓存模块。

    :param options: 配置选项字典。如果为 None，则使用默认配置。
    """
    if not options:
        return
    _config.update(options)


def _try_redis() -> Cache | None:
    """
    尝试创建 Redis 缓存实例。

    :return: RedisCache 实例或 None 如果配置无效或创建失败。
    """
    url = _config.get("redis_url")
    if not url:
        return None
    try:
        return RedisCache(url)
    except Exception:
        return None


def get_cache() -> Cache:
    """
    获取缓存实例。

    :return: 缓存实例。
    """
    global _instance
    if _instance is not None:
        return _instance
    backend = (_config.get("backend") or "auto").lower()
    if backend == "redis" or backend == "auto":
        c = _try_redis()
        if c is not None:
            _instance = c
            return _instance
    if backend == "file" or (backend == "auto" and _config.get("file_dir")):
        _instance = FileCache(_config.get("file_dir"), _config.get("file_max_items") or 10000)
        return _instance
    _instance = MemoryCache(_config.get("memory_capacity") or 1000)
    return _instance


def cache_fn(fn):
    """
    缓存函数装饰器。

    :param fn: 要缓存的函数。
    :return: 缓存包装后的函数。
    """
    def wrapper(*args, **kwargs):
        c = get_cache()
        k = f"fn:{fn.__name__}:{args}:{tuple(sorted(kwargs.items()))}"
        v = c.get(k)
        if v is not None:
            return v
        r = fn(*args, **kwargs)
        ttl = _config.get("default_ttl") or 300
        c.set(k, r, ttl)
        return r
    return wrapper


def configure_from_env(env: dict[str, Any] | None = None):
    """
    从环境变量配置缓存模块。

    :param env: 环境变量字典。如果为 None，则使用 os.environ。
    """
    e = env or os.environ
    opts = {
        "backend": e.get("CACHE_BACKEND") or "auto",
        "default_ttl": int(e.get("CACHE_TTL") or 300),
        "memory_capacity": int(e.get("CACHE_MEMORY_CAPACITY") or 1000),
        "file_dir": e.get("CACHE_DIR"),
        "file_max_items": int(e.get("CACHE_FILE_MAX_ITEMS") or 10000),
        "redis_url": e.get("REDIS_URL"),
    }
    configure(opts)
