"""
存储管理器

负责管理多个存储后端并提供统一访问接口。
"""

from typing import Dict, Optional, Type
from .base import StorageBackend
from .local import LocalStorageBackend
from .qiniu import QiniuStorageBackend
from .aliyun import AliyunOSSStorageBackend
from .tencent import TencentCOSStorageBackend
from ..logging import get_logger
from ..decorators import singleton


logger = get_logger("attachment.storage.manager")


@singleton
class StorageManager:
    """存储管理器"""

    # 内置存储后端类型映射
    BUILTIN_BACKENDS: Dict[str, Type[StorageBackend]] = {
        "local": LocalStorageBackend,
        "qiniu": QiniuStorageBackend,
        "aliyun": AliyunOSSStorageBackend,
        "tencent": TencentCOSStorageBackend,
    }

    def __init__(self):
        self._backends: Dict[str, StorageBackend] = {}
        self._default_backend: Optional[str] = None
        self._custom_backends: Dict[str, Type[StorageBackend]] = {}

    def register_backend_type(
        self, storage_type: str, backend_class: Type[StorageBackend]
    ):
        """
        注册自定义存储后端类型

        Args:
            storage_type: 存储类型标识
            backend_class: 存储后端类
        """
        self._custom_backends[storage_type] = backend_class
        logger.info(f"注册自定义存储后端: {storage_type} -> {backend_class.__name__}")

    def add_backend(
        self, name: str, storage_type: str, config: dict, set_default: bool = False
    ):
        """
        添加存储后端实例

        Args:
            name: 后端实例名称
            storage_type: 存储类型（local, qiniu, aliyun, tencent 或自定义类型）
            config: 配置字典
            set_default: 是否设置为默认后端
        """
        # 查找后端类
        backend_class = self._custom_backends.get(
            storage_type
        ) or self.BUILTIN_BACKENDS.get(storage_type)

        if not backend_class:
            raise ValueError(f"未知的存储类型: {storage_type}")

        # 创建后端实例
        backend = backend_class(config)
        self._backends[name] = backend

        if set_default or not self._default_backend:
            self._default_backend = name

        logger.info(
            f"添加存储后端: {name} (type={storage_type}, default={set_default})"
        )

    def get_backend(self, name: Optional[str] = None) -> StorageBackend:
        """
        获取存储后端实例

        Args:
            name: 后端名称，None表示使用默认后端

        Returns:
            StorageBackend: 存储后端实例
        """
        if name is None:
            name = self._default_backend

        if not name:
            raise ValueError("未配置存储后端")

        backend = self._backends.get(name)
        if not backend:
            raise ValueError(f"存储后端不存在: {name}")

        return backend

    def set_default_backend(self, name: str):
        """
        设置默认存储后端

        Args:
            name: 后端名称
        """
        if name not in self._backends:
            raise ValueError(f"存储后端不存在: {name}")

        self._default_backend = name
        logger.info(f"设置默认存储后端: {name}")

    def list_backends(self) -> Dict[str, str]:
        """
        列出所有已注册的存储后端

        Returns:
            Dict[str, str]: {后端名称: 存储类型}
        """
        return {name: backend.storage_type for name, backend in self._backends.items()}

    def remove_backend(self, name: str):
        """
        移除存储后端

        Args:
            name: 后端名称
        """
        if name in self._backends:
            del self._backends[name]
            logger.info(f"移除存储后端: {name}")

            if self._default_backend == name:
                self._default_backend = next(iter(self._backends.keys()), None)
                logger.info(f"默认存储后端已更新: {self._default_backend}")


# 全局存储管理器实例
_storage_manager: StorageManager | None = None


def get_storage_manager() -> StorageManager:
    """
    获取存储管理器实例

    Returns:
        StorageManager: 存储管理器
    """
    global _storage_manager
    if _storage_manager is None:
        raise RuntimeError("存储管理器未初始化，请先调用 init_storage_manager()")
    return _storage_manager


def init_storage_manager(manager: StorageManager):
    """
    初始化存储管理器

    Args:
        manager: 存储管理器实例
    """
    global _storage_manager
    _storage_manager = manager
