"""
缓存模块 - 文件缓存实现

提供将缓存数据序列化到文件系统的缓存实现，适用于多进程应用。
"""
from typing import Any
import os
import json
import hashlib
import time
from .base import Cache


class FileCache(Cache):
    """
    文件缓存实现。
    将缓存数据序列化到文件系统，适用于多进程应用。
    """
    def __init__(self, directory: str | None, max_items: int = 10000):
        """
        初始化文件缓存。

        :param directory: 缓存文件存储目录。如果为 None，则使用默认目录 ".cache"。
        :param max_items: 最大缓存项数。如果缓存项数超过此值，会触发缓存驱逐策略。
        """
        self.dir = directory or ".cache"
        self.max_items = max(1, int(max_items))
        os.makedirs(self.dir, exist_ok=True)

    def _path(self, key: str) -> str:
        """
        计算缓存键对应的文件路径。

        :param key: 缓存键
        :return: 缓存文件路径
        """
        h = hashlib.sha256(key.encode()).hexdigest()
        return os.path.join(self.dir, h + ".json")

    def _list_files(self) -> list[str]:
        """
        列出所有缓存文件路径。

        :return: 缓存文件路径列表
        """
        return [os.path.join(self.dir, f) for f in os.listdir(self.dir) if f.endswith(".json")]

    def _evict(self) -> None:
        """
        触发缓存驱逐策略，删除过期或超出最大缓存项数的缓存文件。
        """
        files = self._list_files()
        if len(files) <= self.max_items:
            return
        files.sort(key=lambda p: os.path.getmtime(p))
        for p in files[: len(files) - self.max_items]:
            try:
                os.remove(p)
            except Exception:
                pass

    def get(self, key: str) -> Any:
        """
        获取缓存值。

        :param key: 缓存键
        :return: 缓存值，如果键不存在或已过期则返回 None
        """
        p = self._path(key)
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            exp = data.get("exp")
            if exp is not None and time.time() > float(exp):
                self.delete(key)
                return None
            return data.get("val")
        except Exception:
            return None

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """
        设置缓存值。

        :param key: 缓存键
        :param value: 缓存值
        :param ttl: 缓存过期时间，单位为秒。如果为 None，则使用默认过期时间。
        """
        exp = None
        if ttl and ttl > 0:
            exp = time.time() + ttl
        data = {"val": value, "exp": exp}
        p = self._path(key)
        try:
            with open(p, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
        except Exception:
            return
        self._evict()

    def delete(self, key: str) -> None:
        """
        删除缓存值。

        :param key: 缓存键
        """
        p = self._path(key)
        try:
            if os.path.exists(p):
                os.remove(p)
        except Exception:
            pass

    def clear(self) -> None:
        """
        清空所有缓存值。
        """
        for p in self._list_files():
            try:
                os.remove(p)
            except Exception:
                pass