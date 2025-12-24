"""
缓存模块

提供缓存功能，支持内存、文件、Redis 等后端。

#### 功能模块
- 内存缓存：基于 Python 字典实现，适用于单进程应用。
- 文件缓存：将缓存数据序列化到文件系统，适用于多进程应用。
- Redis 缓存：利用 Redis 实现分布式缓存，适用于多实例应用。

"""
from .config import configure, configure_from_env, get_cache, Cache
from .stores import CacheCodeStore



__all__ = [
    "configure", 
    "configure_from_env",
    "get_cache", 
    "Cache",
    "CacheCodeStore"]
