"""
配置管理模块

提供项目的通用环境配置，聚焦基础能力（数据库、JWT、CORS、日志等），
去除非通用配置（如云存储、短信），由业务模块自行管理。
"""

from functools import lru_cache
import json
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator, model_validator
from cryptography.fernet import Fernet


class CoreSettings(BaseSettings):
    """
    项目配置类。
    包含项目的所有配置项，包括数据库连接、JWT 密钥、CORS 允许的来源等。
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="",
        case_sensitive=False,
        extra="allow",
    )
    project_name: str = Field(default="FastAPI Common Module", description="项目名称")
    app_name: str = Field(default="FastAPI Common Module", description="应用名称")
    app_version: str = Field(default="0.0.0", description="应用版本")
    debug: bool = Field(default=False, description="是否开启调试模式")
    api_str: str = Field(default="/api", description="API 基础路径")

    database_url: str = Field(default="sqlite:///./app.db", description="数据库连接URL")

    mysql_host: str | None = Field(default=None, description="MySQL主机")
    mysql_port: int | None = Field(default=None, description="MySQL端口")
    mysql_user: str | None = Field(default=None, description="MySQL用户名")
    mysql_password: str | None = Field(default=None, description="MySQL密码")
    mysql_database: str | None = Field(default=None, description="MySQL数据库名")

    jwt_secret: str = Field(default="CHANGE_ME", description="JWT密钥")
    jwt_algorithm: str = Field(default="HS256", description="JWT算法")
    jwt_expires_minutes: int = Field(default=60, description="JWT过期时间（分钟）")

    db_encryption_key: Optional[str] = Field(default=None, description="数据库加密密钥")

    @field_validator("db_encryption_key")
    @classmethod
    def validate_encryption_key(cls, v):
        """
        验证数据库加密密钥。
        如果配置为字符串，会尝试使用 Fernet 解密验证其有效性。
        """
        if v is None:
            return v
        try:
            Fernet(v.encode())
        except ValueError as exc:
            raise ValueError("DB_ENCRYPTION_KEY must be a valid Fernet key") from exc
        return v

    backend_cors_origins: List[str] = Field(default=["*"], description="CORS允许的来源")
    allowed_hosts: List[str] = Field(default=["*"], description="允许的主机")

    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        """
        解析CORS允许的来源列表。
        如果配置为字符串，会根据逗号分隔符解析为列表。
        """
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    log_level: str = Field(default="INFO", description="日志级别")
    log_dir: str | None = Field(default="./logs", description="日志目录")
    log_format: str = Field(
        default="%(asctime)s %(levelname)s %(name)s %(message)s", description="日志格式"
    )

    @model_validator(mode="after")
    def _compute_database_url(self):
        """
        计算数据库URL。
        如果配置了MySQL主机、用户、密码和数据库名，会根据这些信息构建数据库URL。
        """
        if (
            self.mysql_host
            and self.mysql_user
            and self.mysql_password
            and self.mysql_database
        ):
            port = self.mysql_port or 3306
            self.database_url = (
                f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
                f"@{self.mysql_host}:{port}/{self.mysql_database}?charset=utf8mb4"
            )
        return self

    module_sources: List[str] = Field(default=[], description="模块源列表")

    @field_validator("module_sources", mode="before")
    @classmethod
    def parse_sources(cls, v):
        """
        解析模块源配置，支持JSON格式或逗号分隔字符串。

        :param v: 配置值，可能是JSON字符串、逗号分隔字符串或列表
        :return: 解析后的源列表
        """
        if v is None:
            return []
        if isinstance(v, str) and v.strip().startswith("["):
            try:
                return json.loads(v)
            except Exception:
                pass
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # 附加存储相关配置
    storage_type: str = Field(
        default="local", description="存储类型, local, qiniu, aliyun, tencent"
    )

    # 七牛云存储配置
    qiniu_access_key: str | None = Field(default=None, description="七牛AccessKey")
    qiniu_secret_key: str | None = Field(default=None, description="七牛SecretKey")
    qiniu_bucket_name: str | None = Field(default=None, description="七牛BucketName")
    qiniu_domain: str | None = Field(default=None, description="七牛Domain")
    qiniu_region: str | None = Field(default=None, description="七牛Region")

    # 阿里云OSS存储配置
    aliyun_access_key_id: str | None = Field(
        default=None, description="阿里云AccessKey ID"
    )
    aliyun_access_key_secret: str | None = Field(
        default=None, description="阿里云AccessKey Secret"
    )
    aliyun_bucket_name: str | None = Field(default=None, description="阿里云BucketName")
    aliyun_endpoint: str | None = Field(default=None, description="阿里云Endpoint")

    # 腾讯云COS存储配置
    tencent_secret_id: str | None = Field(default=None, description="腾讯云Secret ID")
    tencent_secret_key: str | None = Field(default=None, description="腾讯云Secret Key")
    tencent_bucket_name: str | None = Field(
        default=None, description="腾讯云BucketName"
    )
    tencent_domain: str | None = Field(default=None, description="腾讯云Domain")
    tencent_region: str | None = Field(default=None, description="腾讯云Region")


@lru_cache(maxsize=1)
def get_settings() -> CoreSettings:
    """
    获取基础配置实例。
    该函数会返回一个配置实例，包含项目的所有配置项。
    """
    settings = CoreSettings()
    return settings
