"""
存储后端基类

定义存储后端的统一接口。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, BinaryIO


@dataclass
class UploadResult:
    """上传结果"""

    path: str  # 存储路径/key
    url: Optional[str] = None  # 访问URL（如果支持）
    size: int = 0  # 文件大小
    storage_type: str = ""  # 存储类型标识
    extra: Optional[dict] = None  # 额外信息


class StorageBackend(ABC):
    """存储后端抽象基类"""

    def __init__(self, config: dict):
        """
        初始化存储后端

        Args:
            config: 配置字典
        """
        self.config = config

    @property
    @abstractmethod
    def storage_type(self) -> str:
        """返回存储类型标识"""
        pass

    @abstractmethod
    async def upload(
        self,
        file_data: bytes | BinaryIO,
        filename: str,
        content_type: Optional[str] = None,
        path_prefix: Optional[str] = None,
    ) -> UploadResult:
        """
        上传文件

        Args:
            file_data: 文件数据（字节或文件对象）
            filename: 文件名
            content_type: 内容类型
            path_prefix: 路径前缀

        Returns:
            UploadResult: 上传结果
        """
        pass

    @abstractmethod
    async def download(self, path: str) -> bytes:
        """
        下载文件

        Args:
            path: 存储路径

        Returns:
            bytes: 文件数据
        """
        pass

    @abstractmethod
    async def delete(self, path: str) -> bool:
        """
        删除文件

        Args:
            path: 存储路径

        Returns:
            bool: 是否成功
        """
        pass

    @abstractmethod
    async def exists(self, path: str) -> bool:
        """
        检查文件是否存在

        Args:
            path: 存储路径

        Returns:
            bool: 是否存在
        """
        pass

    async def get_url(self, path: str, expires: Optional[int] = None) -> Optional[str]:
        """
        获取文件访问URL

        Args:
            path: 存储路径
            expires: 过期时间（秒），None表示永久

        Returns:
            Optional[str]: 访问URL，如果不支持则返回None
        """
        return None

    async def get_size(self, path: str) -> int:
        """
        获取文件大小

        Args:
            path: 存储路径

        Returns:
            int: 文件大小（字节）
        """
        raise NotImplementedError("Subclass must implement get_size method")
