"""
七牛云存储后端
"""

import uuid
from pathlib import Path
from typing import Optional, BinaryIO
from .base import StorageBackend, UploadResult
from ..logging import get_logger


logger = get_logger("attachment.storage.qiniu")


class QiniuStorageBackend(StorageBackend):
    """七牛云存储实现"""

    @property
    def storage_type(self) -> str:
        return "qiniu"

    def __init__(self, config: dict):
        super().__init__(config)
        self.access_key = config.get("access_key")
        self.secret_key = config.get("secret_key")
        self.bucket_name = config.get("bucket_name")
        self.domain = config.get("domain")  # CDN域名

        if not all([self.access_key, self.secret_key, self.bucket_name]):
            raise ValueError(
                "七牛云配置缺少必要参数: access_key, secret_key, bucket_name"
            )

        try:
            from qiniu import Auth, put_data, BucketManager

            self.auth = Auth(self.access_key, self.secret_key)
            self.bucket_manager = BucketManager(self.auth)
            logger.info(f"七牛云存储初始化成功: bucket={self.bucket_name}")
        except ImportError:
            raise ImportError("请安装七牛云SDK: pip install qiniu")

    async def upload(
        self,
        file_data: bytes | BinaryIO,
        filename: str,
        content_type: Optional[str] = None,
        path_prefix: Optional[str] = None,
    ) -> UploadResult:
        """上传文件到七牛云"""
        from qiniu import put_data

        # 生成唯一key
        file_ext = Path(filename).suffix
        unique_name = f"{uuid.uuid4().hex}{file_ext}"

        if path_prefix:
            key = f"{path_prefix.strip('/')}/{unique_name}"
        else:
            key = unique_name

        # 获取上传token
        token = self.auth.upload_token(self.bucket_name, key)

        # 上传数据
        if isinstance(file_data, bytes):
            data = file_data
        else:
            data = file_data.read()

        ret, info = put_data(token, key, data)

        if info.status_code != 200:
            raise Exception(f"七牛云上传失败: {info.text_body}")

        # 构建访问URL
        url = None
        if self.domain:
            url = f"https://{self.domain.strip('/')}/{key}"

        logger.info(f"文件上传到七牛云成功: {key} ({len(data)} bytes)")

        return UploadResult(
            path=key,
            url=url,
            size=len(data),
            storage_type=self.storage_type,
            extra={"hash": ret.get("hash")},
        )

    async def download(self, path: str) -> bytes:
        """从七牛云下载文件"""
        import httpx

        url = await self.get_url(path)
        if not url:
            raise ValueError("无法生成下载URL")

        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.content

    async def delete(self, path: str) -> bool:
        """从七牛云删除文件"""
        try:
            ret, info = self.bucket_manager.delete(self.bucket_name, path)
            if info.status_code == 200:
                logger.info(f"文件从七牛云删除成功: {path}")
                return True
            else:
                logger.error(f"文件从七牛云删除失败: {path}, {info.text_body}")
                return False
        except Exception as e:
            logger.error(f"文件从七牛云删除失败: {path}, {e}")
            return False

    async def exists(self, path: str) -> bool:
        """检查文件是否存在"""
        try:
            ret, info = self.bucket_manager.stat(self.bucket_name, path)
            return info.status_code == 200
        except Exception:
            return False

    async def get_url(self, path: str, expires: Optional[int] = 3600) -> Optional[str]:
        """获取访问URL（支持私有空间）"""
        if not self.domain:
            return None

        base_url = f"https://{self.domain.strip('/')}/{path}"

        # 如果设置了过期时间，生成私有URL
        if expires:
            private_url = self.auth.private_download_url(base_url, expires=expires)
            return private_url

        return base_url

    async def get_size(self, path: str) -> int:
        """获取文件大小"""
        ret, info = self.bucket_manager.stat(self.bucket_name, path)
        if info.status_code != 200:
            raise FileNotFoundError(f"文件不存在: {path}")
        return ret.get("fsize", 0)
