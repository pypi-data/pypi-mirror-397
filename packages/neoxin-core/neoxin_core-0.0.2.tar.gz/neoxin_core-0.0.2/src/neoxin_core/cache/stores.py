"""
缓存验证码存储类。
"""
from .config import get_cache

class CacheCodeStore:
    """
    缓存验证码存储类。

    用于将验证码存储在缓存中，以用于后续的验证。

    参数:
        prefix (str): 验证码缓存键的前缀，用于避免键冲突。
    """
    def __init__(self, prefix: str):
        self.c = get_cache()
        self.p = prefix

    def save(self, phone: str, code: str, ttl_seconds: int = 300):
        """
        保存验证码到缓存中。

        参数:
            phone (str): 手机号，用于作为验证码的键。
            code (str): 验证码字符串。
            ttl_seconds (int, 可选): 验证码的过期时间，单位为秒。默认值为 300 秒。
        """
        self.c.set(f"{self.p}{phone}", code, ttl_seconds)

    def verify(self, phone: str, code: str):
        """
        验证验证码是否正确。

        参数:
            phone (str): 手机号，用于作为验证码的键。
            code (str): 验证码字符串。

        返回:
            bool: 如果验证码正确，则返回 True；否则返回 False。
        """
        return self.c.get(f"{self.p}{phone}") == code
