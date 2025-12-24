"""
Redis 缓存模块
"""
import json
from typing import Any
import redis
from .base import Cache

class RedisCache(Cache):
    """
    Redis 缓存实现类。

    :param url: Redis 连接 URL，例如 "redis://localhost:6379/0"。
    """
    def __init__(self, url: str):
        """
        初始化 Redis 缓存客户端。

        :param url: Redis 连接 URL，例如 "redis://localhost:6379/0"。
        """
       
        self.client = redis.Redis.from_url(url)

    def get(self, key: str) -> Any:
        """
        获取缓存项。

        :param key: 缓存键。
        :return: 缓存值，如果键不存在或已过期则返回 None。
        """
        v = self.client.get(key)
        if v is None:
            return None
        try:
            return json.loads(v)
        except Exception:
            return v

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """
        设置缓存项。

        :param key: 缓存键。
        :param value: 缓存值。
        :param ttl: 缓存过期时间（秒），如果为 None 则永不过期。
        """
        try:
            import json
            payload = json.dumps(value, ensure_ascii=False)
        except Exception:
            payload = value
        if ttl and ttl > 0:
            self.client.set(key, payload, ex=int(ttl))
        else:
            self.client.set(key, payload)

    def delete(self, key: str) -> None:
        """
        删除缓存项。

        :param key: 缓存键。
        """
        self.client.delete(key)

    def clear(self) -> None:
        """
        清空所有缓存项。
        """
        self.client.flushdb()