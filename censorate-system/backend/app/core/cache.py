import redis
from typing import Any, Optional
from .config import Settings


class RedisCache:
    """Redis cache client."""

    _instance: Optional["RedisCache"] = None
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if RedisCache._initialized:
            return
        self.settings = Settings.get()
        self.client = redis.from_url(
            self.settings.REDIS_URL,
            max_connections=self.settings.REDIS_POOL_SIZE
        )
        RedisCache._initialized = True

    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        try:
            return self.client.get(key)
        except Exception as e:
            print(f"Cache get failed: {e}")
            return None

    def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """Set a value in cache with optional expiration."""
        try:
            if ex:
                self.client.setex(key, ex, value)
            else:
                self.client.set(key, value)
            return True
        except Exception as e:
            print(f"Cache set failed: {e}")
            return False

    def delete(self, key: str) -> int:
        """Delete a key from cache."""
        try:
            return self.client.delete(key)
        except Exception as e:
            print(f"Cache delete failed: {e}")
            return 0

    def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        try:
            return self.client.exists(key) > 0
        except Exception as e:
            print(f"Cache exists check failed: {e}")
            return False

    def keys(self, pattern: str) -> list:
        """Get all keys matching a pattern."""
        try:
            return self.client.keys(pattern)
        except Exception as e:
            print(f"Cache keys failed: {e}")
            return []

    def flush(self) -> bool:
        """Flush all keys in cache (use with caution)."""
        try:
            self.client.flushdb()
            return True
        except Exception as e:
            print(f"Cache flush failed: {e}")
            return False


cache = RedisCache()
