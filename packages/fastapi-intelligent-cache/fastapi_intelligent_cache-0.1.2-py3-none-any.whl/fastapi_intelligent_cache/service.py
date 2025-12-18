"""Cache service for high-level cache operations."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from .backends.base import CacheBackend

logger = logging.getLogger(__name__)


class CacheService:
    """
    High-level cache service.

    Provides:
    - Get/set with metadata wrapper
    - Pattern-based clearing
    - Key listing
    - Stats tracking
    """

    def __init__(self, backend: CacheBackend):
        self.backend = backend
        self._hits = 0
        self._misses = 0

    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Unwraps metadata if present.
        """
        cached = await self.backend.get(key)

        if cached is None:
            self._misses += 1
            return None

        self._hits += 1

        # Unwrap metadata if present
        if isinstance(cached, dict) and "data" in cached:
            return cached["data"]

        return cached

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        include_metadata: bool = True,
    ) -> bool:
        """
        Set value in cache.

        Optionally wraps with metadata (lastModifiedDateTime).
        """
        if include_metadata:
            payload = {
                "data": value,
                "lastModifiedDateTime": datetime.now(timezone.utc)
                .isoformat()
                .replace("+00:00", "Z"),
            }
        else:
            payload = value

        return await self.backend.set(key, payload, ttl)

    async def delete(self, key: str) -> bool:
        """Delete single key."""
        return await self.backend.delete(key)

    async def clear_pattern(self, pattern: str) -> int:
        """
        Clear all keys matching glob pattern.

        Args:
            pattern: Glob-style pattern (e.g., 'GET:spaces:*')

        Returns:
            Number of keys deleted
        """
        try:
            # Delegate to backend for efficiency (Redis can SCAN+batch delete)
            deleted_count = await self.backend.clear(pattern)
            logger.info(f"Cleared {deleted_count} keys matching pattern: {pattern}")
            return deleted_count

        except Exception as e:
            logger.error(f"Error clearing pattern '{pattern}': {e}")
            return 0

    async def clear_all(self) -> int:
        """Clear all cache keys."""
        try:
            count = await self.backend.clear("*")  # Clear all with wildcard pattern
            logger.info(f"Cleared all cache ({count} items)")
            return count
        except Exception as e:
            logger.error(f"Error clearing all cache: {e}")
            return 0

    async def list_keys(
        self, pattern: str = "*", limit: int = 100, cursor: int = 0
    ) -> Dict[str, Any]:
        """
        List keys with metadata and pagination.

        Returns:
            Dict containing 'keys' (list), 'cursor' (int/str)
        """
        try:
            next_cursor, keys = await self.backend.scan(pattern, cursor, count=limit)

            results = []
            for key in keys:
                ttl = await self.backend.ttl(key)
                results.append(
                    {
                        "key": key,
                        "ttl": ttl,
                    }
                )

            return {
                "keys": results,
                "cursor": next_cursor,
            }

        except Exception as e:
            logger.error(f"Error listing keys: {e}")
            return {"keys": [], "cursor": 0}

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        return await self.backend.exists(key)

    async def ping(self) -> bool:
        """Health check."""
        return await self.backend.ping()

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dict with hits, misses, hit_rate
        """
        total = self._hits + self._misses
        hit_rate = self._hits / total if total > 0 else 0.0

        return {
            "hits": self._hits,
            "misses": self._misses,
            "total": total,
            "hit_rate": round(hit_rate, 3),
        }

    def reset_stats(self) -> None:
        """Reset hit/miss counters."""
        self._hits = 0
        self._misses = 0
