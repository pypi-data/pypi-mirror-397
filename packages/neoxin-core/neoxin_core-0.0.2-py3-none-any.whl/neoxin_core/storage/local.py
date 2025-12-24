"""
本地文件存储后端
"""

import os
import uuid
from pathlib import Path
from typing import Optional, BinaryIO
from .base import StorageBackend, UploadResult
from ..logging import get_logger


logger = get_logger("attachment.storage.local")


class LocalStorageBackend(StorageBackend):
    """本地文件存储实现"""

    @property
    def storage_type(self) -> str:
        return "local"

    def __init__(self, config: dict):
        super().__init__(config)
        self.base_dir = Path(config.get("base_dir", "./data/attachments")).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.base_url = config.get("base_url")  # 可选的访问URL前缀
        logger.info(f"本地存储初始化: {self.base_dir}")

    def _get_full_path(self, path: str) -> Path:
        """获取完整路径"""
        return self.base_dir / path

    async def upload(
        self,
        file_data: bytes | BinaryIO,
        filename: str,
        content_type: Optional[str] = None,
        path_prefix: Optional[str] = None,
    ) -> UploadResult:
        """上传文件到本地存储"""
        # 生成唯一文件名
        file_ext = Path(filename).suffix
        unique_name = f"{uuid.uuid4().hex}{file_ext}"

        # 构建存储路径
        if path_prefix:
            rel_path = Path(path_prefix) / unique_name
        else:
            rel_path = Path(unique_name)

        full_path = self._get_full_path(str(rel_path))
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # 写入文件
        if isinstance(file_data, bytes):
            full_path.write_bytes(file_data)
            size = len(file_data)
        else:
            with open(full_path, "wb") as f:
                data = file_data.read()
                f.write(data)
                size = len(data)

        # 构建访问URL
        url = None
        if self.base_url:
            url = f"{self.base_url.rstrip('/')}/{str(rel_path).replace(os.sep, '/')}"

        logger.info(f"文件上传成功: {rel_path} ({size} bytes)")

        return UploadResult(
            path=str(rel_path).replace(os.sep, "/"),
            url=url,
            size=size,
            storage_type=self.storage_type,
        )

    async def download(self, path: str) -> bytes:
        """从本地存储下载文件"""
        full_path = self._get_full_path(path)
        if not full_path.exists():
            raise FileNotFoundError(f"文件不存在: {path}")
        return full_path.read_bytes()

    async def delete(self, path: str) -> bool:
        """从本地存储删除文件"""
        full_path = self._get_full_path(path)
        if not full_path.exists():
            return False
        try:
            full_path.unlink()
            logger.info(f"文件删除成功: {path}")
            return True
        except Exception as e:
            logger.error(f"文件删除失败: {path}, {e}")
            return False

    async def exists(self, path: str) -> bool:
        """检查文件是否存在"""
        return self._get_full_path(path).exists()

    async def get_url(self, path: str, expires: Optional[int] = None) -> Optional[str]:
        """获取访问URL"""
        if not self.base_url:
            return None
        return f"{self.base_url.rstrip('/')}/{path}"

    async def get_size(self, path: str) -> int:
        """获取文件大小"""
        full_path = self._get_full_path(path)
        if not full_path.exists():
            raise FileNotFoundError(f"文件不存在: {path}")
        return full_path.stat().st_size
