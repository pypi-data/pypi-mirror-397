"""
内存缓存模块
"""
from typing import Any
from collections import OrderedDict
import time
from .base import Cache


class MemoryCache(Cache):
    """
    内存缓存实现类。

    :param capacity: 缓存容量，默认值为 1000。
    """
    def __init__(self, capacity: int = 1000):
        self.capacity = max(1, int(capacity))
        self.store: OrderedDict[str, tuple[Any, float | None]] = OrderedDict()

    def _evict(self) -> None:
        """
        当缓存容量超过设置值时，移除最早插入的缓存项。
        """
        while len(self.store) > self.capacity:
            self.store.popitem(last=False)

    def get(self, key: str) -> Any:
        """
        获取缓存项。

        :param key: 缓存键。
        :return: 缓存值，如果键不存在或已过期则返回 None。
        """
        v = self.store.get(key)
        if not v:
            return None
        val, exp = v
        if exp is not None and time.time() > exp:
            self.delete(key)
            return None
        self.store.move_to_end(key)
        return val

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """
        设置缓存项。

        :param key: 缓存键。
        :param value: 缓存值。
        :param ttl: 缓存过期时间（秒），如果为 None 则永不过期。
        """
        exp = None
        if ttl and ttl > 0:
            exp = time.time() + ttl
        self.store[key] = (value, exp)
        self.store.move_to_end(key)
        self._evict()

    def delete(self, key: str) -> None:
        """
        删除缓存项。

        :param key: 缓存键。
        """
        if key in self.store:
            del self.store[key]

    def clear(self) -> None:
        """
        清空所有缓存项。
        """
        self.store.clear()