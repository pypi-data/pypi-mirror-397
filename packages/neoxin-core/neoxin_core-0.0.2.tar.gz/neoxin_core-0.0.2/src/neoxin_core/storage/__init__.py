"""
存储后端模块

提供多种存储后端实现及统一接口。
"""

from .base import StorageBackend, UploadResult
from .local import LocalStorageBackend
from .qiniu import QiniuStorageBackend
from .aliyun import AliyunOSSStorageBackend
from .tencent import TencentCOSStorageBackend
from .manager import StorageManager, init_storage_manager, get_storage_manager

__all__ = [
    "StorageBackend",
    "UploadResult",
    "LocalStorageBackend",
    "QiniuStorageBackend",
    "AliyunOSSStorageBackend",
    "TencentCOSStorageBackend",
    "StorageManager",
    "init_storage_manager",
    "get_storage_manager",
]
