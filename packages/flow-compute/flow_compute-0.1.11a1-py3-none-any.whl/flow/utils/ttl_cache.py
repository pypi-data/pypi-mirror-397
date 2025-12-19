"""Simple TTL (Time-To-Live) cache implementation."""

import time
from typing import Generic, TypeVar

K = TypeVar("K")
V = TypeVar("V")


class TTLCache(Generic[K, V]):
    """A simple in-memory cache with TTL (time-to-live) support.

    Thread-safety: This implementation is NOT thread-safe. If used in a
    multi-threaded context, external synchronization is required.

    Example:
        >>> cache = TTLCache[str, dict](ttl_seconds=60.0)
        >>> cache.set("key1", {"data": "value"})
        >>> result = cache.get("key1")  # Returns {"data": "value"}
        >>> # After 60 seconds...
        >>> result = cache.get("key1")  # Returns None (expired)
    """

    def __init__(self, ttl_seconds: float = 60.0):
        """Initialize TTL cache.

        Args:
            ttl_seconds: Time-to-live in seconds for cached entries
        """
        self._cache: dict[K, tuple[V, float]] = {}
        self._ttl = float(ttl_seconds)

    def get(self, key: K) -> V | None:
        """Get value from cache if not expired.

        Args:
            key: Cache key

        Returns:
            Cached value if found and not expired, None otherwise
        """
        if cached := self._cache.get(key):
            value, timestamp = cached
            if time.time() - timestamp < self._ttl:
                return value
            # Expired - remove from cache
            del self._cache[key]
        return None

    def set(self, key: K, value: V) -> None:
        """Set value in cache with current timestamp.

        Args:
            key: Cache key
            value: Value to cache
        """
        self._cache[key] = (value, time.time())

    def clear(self) -> None:
        """Clear all cached entries."""
        self._cache.clear()

    def __contains__(self, key: K) -> bool:
        """Check if key exists and is not expired."""
        return self.get(key) is not None

    def __len__(self) -> int:
        """Return number of cached entries (including expired ones)."""
        return len(self._cache)
