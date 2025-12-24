import jwt
from datetime import datetime, timedelta, timezone
import bcrypt
from .schemas import TokenSubject
from .settings import get_settings


def create_access_token(subject: TokenSubject) -> str:
    """创建访问令牌

    Args:
        subject (str): 令牌主题，通常为用户ID

    Returns:
        str: 编码后的访问令牌
    """
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.jwt_expires_minutes
    )
    payload = subject.model_dump(exclude_unset=True)
    payload["exp"] = expire  # 设置过期时间
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> TokenSubject:
    """解码访问令牌

    Args:
        token (str): 待解码的访问令牌

    Returns:
        dict: 解码后的令牌 payload 内容
    """
    settings = get_settings()
    result = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    return TokenSubject(**result)


def hash_password_bcrypt(password: str) -> str:
    """使用bcrypt哈希密码"""
    # bcrypt会自动处理盐值生成
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password_bcrypt(password: str, hashed: str) -> bool:
    """验证bcrypt哈希"""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False
