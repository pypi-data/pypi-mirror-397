"""
依赖项模块

提供 FastAPI 路由函数所需的依赖项。
"""

from typing import Annotated, Dict
from fastapi import HTTPException, status, Header, Depends, Request, FastAPI
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from .db import get_session_local
from .security import decode_token
from .storage import get_storage_manager, StorageManager
from .settings import get_settings, CoreSettings
from .plugin import PluginManager
from .schemas import ClientInfo


def get_app(request: Request):
    """获取FastAPI应用实例"""
    return request.app


def get_core_settings() -> CoreSettings:
    """
    获取系统配置
    """
    return get_settings()


def get_plugin_manager(app: FastAPI = Depends(get_app)) -> PluginManager:
    """
    获取插件管理器
    """
    return PluginManager(app)


def get_plugin_config(
    plugin_name: str = "", plugin_manager: PluginManager = Depends(get_plugin_manager)
):
    """
    获取插件配置
    """
    if not plugin_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="插件名称不能为空"
        )
    return plugin_manager.get_config(plugin_name)


def get_db():
    """
    获取数据库会话依赖项

    用于在 FastAPI 路由函数中获取数据库会话。

    Yields:
        Session: 数据库会话实例
    """
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_auth_optional(authorization: str = Header(None)):
    """
    获取当前登录用户信息依赖项
    """
    if not authorization:
        return None
    # 解析Authorization头，验证token
    token = authorization.split("Bearer ")[1]
    if not token:
        return None

    try:
        # 验证token是否有效
        payload = decode_token(token)
        return {
            "id": payload.id,
            "account": payload.account,
            "login_type": payload.login_type,
        }
    except ExpiredSignatureError:
        # token已过期
        return None
    except InvalidTokenError:
        # token无效
        return None
    except Exception as e:
        # 其他异常
        return None


def get_current_auth(authorization: str = Header(None)):
    """
    获取当前登录用户信息依赖项
    """
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未登录")
    # 解析Authorization头，验证token
    token = authorization.split("Bearer ")[1]
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未登录")

    try:
        # 验证token是否有效
        payload = decode_token(token)
        return {
            "id": payload.id,
            "account": payload.account,
            "login_type": payload.login_type,
        }
    except ExpiredSignatureError:
        # token已过期
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="token已过期"
        )
    except InvalidTokenError:
        # token无效
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="token无效"
        )
    except Exception as e:
        # 其他异常
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="token无效"
        ) from e


def get_current_auth_user_id(auth_user=Depends(get_current_auth)):
    """
    获取当前登录用户ID依赖项
    """
    return auth_user["id"]


def require_authenticated(auth_user=Depends(get_current_auth)):
    """
    登录依赖, 从Authorization头中获取token, 验证token是否有效
    """
    return auth_user


def get_real_ip(request: Request) -> str:
    """
    获取真实IP地址依赖项
    """
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else None


RealIPDep = Annotated[str, Depends(get_real_ip)]

def detect_client_type(request: Request) -> str:
    """
    从User-Agent检测客户端类型

    Args:
        request: FastAPI请求对象

    Returns:
        str: 客户端类型 (web/app/h5/wechat_miniprogram)
    """
    user_agent = request.headers.get("user-agent", "").lower()

    # 微信小程序
    if "miniprogram" in user_agent or "micromessenger" in user_agent:
        if "miniprogram" in user_agent:
            return "wechat_miniprogram"
        return "wechat"

    # 移动端APP
    if any(keyword in user_agent for keyword in ["android", "iphone", "ipad"]):
        # 如果包含自定义APP标识
        if "app" in user_agent or "mobile" in user_agent:
            return "app"
        # H5页面
        return "h5"

    # 默认为Web端
    return "web"



def get_client_info(request: Request) -> ClientInfo:
    """
    获取客户端信息

    Args:
        request: FastAPI请求对象

    Returns:
        Dict: 包含客户端类型、IP、User-Agent等信息
    """
    client_type = detect_client_type(request)

    # 获取真实IP（考虑代理）
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        ip_address = forwarded_for.split(",")[0].strip()
    else:
        ip_address = request.client.host if request.client else None
        
    return ClientInfo(
        client_type=client_type,
        ip_address=ip_address,
        user_agent=request.headers.get("user-agent"),
        endpoint= str(request.url.path),
    )


ClientInfoDep = Annotated[Dict, Depends(get_client_info)]

# 类型注解，方便在路由中使用
StorageManagerDep = Annotated[StorageManager, Depends(get_storage_manager)]
