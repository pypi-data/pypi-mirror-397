"""
腾讯云COS存储后端
"""

import uuid
from pathlib import Path
from typing import Optional, BinaryIO
from .base import StorageBackend, UploadResult
from ..logging import get_logger


logger = get_logger("attachment.storage.tencent")


class TencentCOSStorageBackend(StorageBackend):
    """腾讯云COS存储实现"""

    @property
    def storage_type(self) -> str:
        return "tencent"

    def __init__(self, config: dict):
        super().__init__(config)
        self.secret_id = config.get("secret_id")
        self.secret_key = config.get("secret_key")
        self.region = config.get("region")
        self.bucket_name = config.get("bucket_name")
        self.domain = config.get("domain")  # 自定义域名（可选）

        if not all([self.secret_id, self.secret_key, self.region, self.bucket_name]):
            raise ValueError(
                "腾讯云COS配置缺少必要参数: secret_id, secret_key, region, bucket_name"
            )

        try:
            from qcloud_cos import CosConfig, CosS3Client

            config_obj = CosConfig(
                Region=self.region,
                SecretId=self.secret_id,
                SecretKey=self.secret_key,
            )
            self.client = CosS3Client(config_obj)
            logger.info(f"腾讯云COS存储初始化成功: bucket={self.bucket_name}")
        except ImportError:
            raise ImportError("请安装腾讯云COS SDK: pip install cos-python-sdk-v5")

    async def upload(
        self,
        file_data: bytes | BinaryIO,
        filename: str,
        content_type: Optional[str] = None,
        path_prefix: Optional[str] = None,
    ) -> UploadResult:
        """上传文件到腾讯云COS"""
        # 生成唯一key
        file_ext = Path(filename).suffix
        unique_name = f"{uuid.uuid4().hex}{file_ext}"

        if path_prefix:
            key = f"{path_prefix.strip('/')}/{unique_name}"
        else:
            key = unique_name

        # 上传数据
        if isinstance(file_data, bytes):
            from io import BytesIO

            body = BytesIO(file_data)
            size = len(file_data)
        else:
            body = file_data
            data = file_data.read()
            size = len(data)
            file_data.seek(0)  # 重置文件指针

        kwargs = {"Bucket": self.bucket_name, "Key": key, "Body": body}
        if content_type:
            kwargs["ContentType"] = content_type

        response = self.client.put_object(**kwargs)

        # 构建访问URL
        url = None
        if self.domain:
            url = f"https://{self.domain.strip('/')}/{key}"
        else:
            url = f"https://{self.bucket_name}.cos.{self.region}.myqcloud.com/{key}"

        logger.info(f"文件上传到腾讯云COS成功: {key} ({size} bytes)")

        return UploadResult(
            path=key,
            url=url,
            size=size,
            storage_type=self.storage_type,
            extra={"etag": response.get("ETag")},
        )

    async def download(self, path: str) -> bytes:
        """从腾讯云COS下载文件"""
        response = self.client.get_object(
            Bucket=self.bucket_name,
            Key=path,
        )
        return response["Body"].read()

    async def delete(self, path: str) -> bool:
        """从腾讯云COS删除文件"""
        try:
            self.client.delete_object(
                Bucket=self.bucket_name,
                Key=path,
            )
            logger.info(f"文件从腾讯云COS删除成功: {path}")
            return True
        except Exception as e:
            logger.error(f"文件从腾讯云COS删除失败: {path}, {e}")
            return False

    async def exists(self, path: str) -> bool:
        """检查文件是否存在"""
        try:
            self.client.head_object(
                Bucket=self.bucket_name,
                Key=path,
            )
            return True
        except Exception:
            return False

    async def get_url(self, path: str, expires: Optional[int] = 3600) -> Optional[str]:
        """获取访问URL（支持私有bucket）"""
        if expires:
            # 生成签名URL
            url = self.client.get_presigned_url(
                Method="GET",
                Bucket=self.bucket_name,
                Key=path,
                Expired=expires,
            )
            return url
        else:
            # 公共访问URL
            if self.domain:
                return f"https://{self.domain.strip('/')}/{path}"
            else:
                return (
                    f"https://{self.bucket_name}.cos.{self.region}.myqcloud.com/{path}"
                )

    async def get_size(self, path: str) -> int:
        """获取文件大小"""
        response = self.client.head_object(
            Bucket=self.bucket_name,
            Key=path,
        )
        return int(response.get("Content-Length", 0))
