"""
阿里云OSS存储后端
"""

import uuid
from pathlib import Path
from typing import Optional, BinaryIO
from .base import StorageBackend, UploadResult
from ..logging import get_logger


logger = get_logger("attachment.storage.aliyun")


class AliyunOSSStorageBackend(StorageBackend):
    """阿里云OSS存储实现"""

    @property
    def storage_type(self) -> str:
        return "aliyun"

    def __init__(self, config: dict):
        super().__init__(config)
        self.access_key_id = config.get("access_key_id")
        self.access_key_secret = config.get("access_key_secret")
        self.endpoint = config.get("endpoint")
        self.bucket_name = config.get("bucket_name")
        self.domain = config.get("domain")  # 自定义域名（可选）

        if not all(
            [
                self.access_key_id,
                self.access_key_secret,
                self.endpoint,
                self.bucket_name,
            ]
        ):
            raise ValueError(
                "阿里云OSS配置缺少必要参数: access_key_id, access_key_secret, endpoint, bucket_name"
            )

        try:
            import oss2

            auth = oss2.Auth(self.access_key_id, self.access_key_secret)
            self.bucket = oss2.Bucket(auth, self.endpoint, self.bucket_name)
            logger.info(f"阿里云OSS存储初始化成功: bucket={self.bucket_name}")
        except ImportError:
            raise ImportError("请安装阿里云OSS SDK: pip install oss2")

    async def upload(
        self,
        file_data: bytes | BinaryIO,
        filename: str,
        content_type: Optional[str] = None,
        path_prefix: Optional[str] = None,
    ) -> UploadResult:
        """上传文件到阿里云OSS"""
        import oss2

        # 生成唯一key
        file_ext = Path(filename).suffix
        unique_name = f"{uuid.uuid4().hex}{file_ext}"

        if path_prefix:
            key = f"{path_prefix.strip('/')}/{unique_name}"
        else:
            key = unique_name

        # 上传数据
        if isinstance(file_data, bytes):
            data = file_data
        else:
            data = file_data.read()

        headers = {}
        if content_type:
            headers["Content-Type"] = content_type

        result = self.bucket.put_object(key, data, headers=headers)

        if result.status != 200:
            raise Exception(f"阿里云OSS上传失败: {result.status}")

        # 构建访问URL
        url = None
        if self.domain:
            url = f"https://{self.domain.strip('/')}/{key}"
        else:
            url = f"https://{self.bucket_name}.{self.endpoint}/{key}"

        logger.info(f"文件上传到阿里云OSS成功: {key} ({len(data)} bytes)")

        return UploadResult(
            path=key,
            url=url,
            size=len(data),
            storage_type=self.storage_type,
            extra={"etag": result.etag},
        )

    async def download(self, path: str) -> bytes:
        """从阿里云OSS下载文件"""
        result = self.bucket.get_object(path)
        return result.read()

    async def delete(self, path: str) -> bool:
        """从阿里云OSS删除文件"""
        try:
            result = self.bucket.delete_object(path)
            if result.status == 204:
                logger.info(f"文件从阿里云OSS删除成功: {path}")
                return True
            else:
                logger.error(f"文件从阿里云OSS删除失败: {path}, status={result.status}")
                return False
        except Exception as e:
            logger.error(f"文件从阿里云OSS删除失败: {path}, {e}")
            return False

    async def exists(self, path: str) -> bool:
        """检查文件是否存在"""
        return self.bucket.object_exists(path)

    async def get_url(self, path: str, expires: Optional[int] = 3600) -> Optional[str]:
        """获取访问URL（支持私有bucket）"""
        if expires:
            # 生成签名URL
            return self.bucket.sign_url("GET", path, expires)
        else:
            # 公共访问URL
            if self.domain:
                return f"https://{self.domain.strip('/')}/{path}"
            else:
                return f"https://{self.bucket_name}.{self.endpoint}/{path}"

    async def get_size(self, path: str) -> int:
        """获取文件大小"""
        meta = self.bucket.head_object(path)
        return meta.content_length
