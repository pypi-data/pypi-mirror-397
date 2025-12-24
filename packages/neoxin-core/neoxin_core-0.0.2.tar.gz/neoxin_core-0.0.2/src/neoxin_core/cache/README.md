# neo-cache

轻量内存缓存，支持 TTL，提供单例 `get_cache()`。

## 导出
- `get_cache()`, `Cache`

## 示例
```python
from cache import get_cache
c = get_cache()
c.set("k", "v", ttl=60)
assert c.get("k") == "v"
```

