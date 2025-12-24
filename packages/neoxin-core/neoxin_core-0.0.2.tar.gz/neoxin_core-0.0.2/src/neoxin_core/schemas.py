from typing import Optional, Any, Dict, List, Generic, TypeVar
from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel


class TokenSubject(BaseModel):
    """
    令牌主题，包含用户ID、用户名和登录类型
    """

    id: int  # 用户ID
    account: str  # 用户名
    login_type: str = "web"  # 登录类型，默认是管理员登录


class ModuleSettings(BaseModel):
    """
    模块配置类。
    包含模块的所有配置项，包括模块源列表等。
    """

    id: Optional[int] = Field(default=None, description="模块ID")
    name: Optional[str] = Field(default="default_module", description="模块名称")
    version: Optional[str] = Field(default="0.0.0", description="模块版本")
    source: Optional[str] = Field(
        default=None, description="模块来源（URL、路径或pip包名）"
    )
    installed: Optional[bool] = Field(default=False, description="是否已安装")
    enabled: Optional[bool] = Field(default=True, description="是否已启用")
    description: Optional[str] = Field(default=None, description="模块描述信息")

    default_config: Optional[dict] = Field(
        default_factory=dict,
        description="模块默认配置（JSON格式）",
    )


# 默认分页大小
__DEFAULT_PAGE_SIZE__ = 15
# 默认分页
__DEFAULT_PAGE__ = 1


class ApiResponse(BaseModel):
    """
    统一API响应模型

    Args:
        code (int): 状态码
        message (str): 消息
        data (Optional[Any]): 数据
        error (Optional[Dict[str, Any]]): 错误信息
    """

    code: int = Field(..., description="状态码")
    message: str = Field(..., description="消息")
    data: Optional[Any] = Field(None, description="数据")
    error: Optional[Dict[str, Any]] = Field(None, description="错误信息")


class PaginationRequest(BaseModel):
    """
    分页请求模型

    Args:
        page (int, optional): 当前页码. Defaults to __DEFAULT_PAGE__.
        pageSize (int, optional): 每页大小. Defaults to __DEFAULT_PAGE_SIZE__.
    """

    page: Optional[int] = Field(__DEFAULT_PAGE__, description="当前页码")
    pageSize: Optional[int] = Field(__DEFAULT_PAGE_SIZE__, description="每页大小")


D = TypeVar("D", bound=BaseModel)


class PaginatedResponse(BaseModel, Generic[D]):
    """
    分页响应模型

    Args:
        list (List[Optional[D]]): 数据列表
        total (int): 总记录数
        page (int): 当前页码
        pageSize (int): 每页大小
    """

    list: List[Optional[D]] = Field(..., description="数据列表")
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    pageSize: int = Field(..., description="每页大小")


class ClientInfo(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    client_type: Optional[str] = Field(
        None, description="客户端类型：web/app/h5/wechat_miniprogram "
    )
    ip_address: Optional[str] = Field(None, description="访问IP")
    user_agent: Optional[str] = Field(None, description="用户agent")
    endpoint: Optional[str] = Field(None, description="访问url")


class PluginValidationRule(BaseModel):
    """
    插件配置项验证规则模型
    {
        "type": "integer",
        "minimum": 1,
        "maximum": 365,
        "default": 90,
    }
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    type: Optional[str] = Field(None, description="验证类型")
    enum: Optional[List[str]] = Field(None, description="枚举值列表")
    description: Optional[str] = Field(None, description="验证规则描述")
    minimum: Optional[int] = Field(None, description="最小值")
    maximum: Optional[int] = Field(None, description="最大值")
    default: Optional[str] = Field(None, description="默认值")
    maxLength: Optional[int] = Field(None, description="最大长度")
    minLength: Optional[int] = Field(None, description="最小长度")
    pattern: Optional[str] = Field(None, description="正则表达式")
    
    


class PluginConfigItem(BaseModel):
    """
    插件配置项模型:
    {
        "key": "default_storage_backend",
        "default": "local",
        "description": "默认存储后端类型（local/s3/oss等）",
        "validation_rule": {
            "type": "string",
            "enum": ["local", "s3", "oss", "cos"],
            "description": "存储后端类型",
        },
    }
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    key: str = Field(..., description="配置项key")
    default: str = Field(..., description="配置项默认值")
    description: str = Field(..., description="配置项描述")
    validation_rule: PluginValidationRule = Field(..., description="配置项验证规则")

