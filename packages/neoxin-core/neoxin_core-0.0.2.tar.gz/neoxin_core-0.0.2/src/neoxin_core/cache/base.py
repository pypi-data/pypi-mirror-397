"""
缓存模块 - 缓存基类

提供缓存功能的基类，定义了缓存的基本操作接口。
具体的缓存实现需要继承并实现这些方法。
"""
from typing import Any


class Cache:
    """
    缓存基类。
    定义了缓存的基本操作接口，具体的缓存实现需要继承并实现这些方法。
    """
    def get(self, key: str) -> Any:
        """
        获取缓存值。

        :param key: 缓存键
        :return: 缓存值，如果键不存在则返回 None
        """
        raise NotImplementedError

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """
        设置缓存值。

        :param key: 缓存键
        :param value: 缓存值
        :param ttl: 缓存过期时间，单位为秒。如果为 None，则使用默认过期时间。
        """
        raise NotImplementedError

    def delete(self, key: str) -> None:
        """
        删除缓存值。

        :param key: 缓存键
        """ 
        raise NotImplementedError

    def clear(self) -> None:
        """
        清空所有缓存值。
        """
        raise NotImplementedError