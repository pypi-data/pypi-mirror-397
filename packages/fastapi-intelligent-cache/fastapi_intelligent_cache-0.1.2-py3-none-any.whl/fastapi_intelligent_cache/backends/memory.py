"""In-memory cache backend for testing and development."""

import re
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

from .base import CacheBackend


class MemoryBackend(CacheBackend):
    """
    In-memory cache backend.

    Features:
    - Fast (no network calls)
    - Automatic expiration
    - Pattern matching
    - Useful for testing and development
    """

    def __init__(self):
        self._store: Dict[str, Dict[str, Any]] = {}
        # Each entry: {"value": ..., "expires_at": datetime | None}

    def _is_expired(self, key: str) -> bool:
        """Check if key has expired."""
        if key not in self._store:
            return True

        entry = self._store[key]
        expires_at = entry.get("expires_at")

        if expires_at is None:
            return False

        return datetime.now(timezone.utc) > expires_at

    async def get(self, key: str) -> Optional[Any]:
        """Get value from memory."""
        if key not in self._store or self._is_expired(key):
            # Clean up expired key
            if key in self._store:
                del self._store[key]
            return None

        return self._store[key]["value"]

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in memory with optional TTL."""
        expires_at = None
        if ttl:
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl)

        self._store[key] = {
            "value": value,
            "expires_at": expires_at,
        }
        return True

    async def delete(self, key: str) -> bool:
        """Delete key from memory."""
        if key in self._store:
            del self._store[key]
            return True
        return False

    async def clear(self, pattern: str = "*") -> int:
        """Clear keys matching pattern."""
        import fnmatch

        regex_pattern = fnmatch.translate(pattern)
        keys_to_delete = [k for k in self._store.keys() if re.match(regex_pattern, k)]

        for k in keys_to_delete:
            del self._store[k]

        return len(keys_to_delete)

    async def scan(
        self, pattern: str = "*", cursor: int = 0, count: int = 100
    ) -> Tuple[int, List[str]]:
        """
        Scan keys with pagination.

        Since this is memory backend, we just slice the list of keys.
        """
        # Get all valid keys matching pattern
        all_keys = await self.keys(pattern)

        # Simple list slicing for simulation
        start = cursor
        end = cursor + count

        batch = all_keys[start:end]

        # Calculate next cursor
        next_cursor = end if end < len(all_keys) else 0

        return next_cursor, batch

    async def keys(self, pattern: str = "*") -> List[str]:
        """List keys matching glob-style pattern."""
        import fnmatch

        # fnmatch.translate produces a regex that matches the entire string
        regex_pattern = fnmatch.translate(pattern)

        # Filter expired keys and match pattern
        valid_keys = [
            k for k in self._store.keys() if not self._is_expired(k) and re.match(regex_pattern, k)
        ]

        # Sort for consistent pagination in scan
        valid_keys.sort()

        return valid_keys

    async def exists(self, key: str) -> bool:
        """Check if key exists and is not expired."""
        return key in self._store and not self._is_expired(key)

    async def ttl(self, key: str) -> Optional[int]:
        """Get remaining TTL (seconds), -1 if no TTL, -2 if not exists."""
        if key not in self._store or self._is_expired(key):
            return -2  # Key doesn't exist

        entry = self._store[key]
        expires_at = entry.get("expires_at")

        if expires_at is None:
            return -1  # No TTL

        remaining = (expires_at - datetime.now(timezone.utc)).total_seconds()
        return int(remaining)

    async def ping(self) -> bool:
        """Health check (always True for memory backend)."""
        return True
