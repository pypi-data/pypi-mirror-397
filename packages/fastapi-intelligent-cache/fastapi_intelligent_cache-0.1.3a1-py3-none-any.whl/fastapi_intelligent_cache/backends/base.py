"""Abstract base class for cache backends."""

from abc import ABC, abstractmethod
from typing import Any, List, Optional, Tuple


class CacheBackend(ABC):
    """Abstract base class for cache storage backends."""

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache. Returns None if not found or error."""
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache with optional TTL (seconds).
        Returns True if successful, False otherwise.
        """
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete key from cache. Returns True if successful."""
        pass

    @abstractmethod
    async def clear(self, pattern: str = "*") -> int:
        """Clear keys matching pattern."""
        pass

    @abstractmethod
    async def keys(self, pattern: str = "*") -> List[str]:
        """List keys matching pattern (glob-style)."""
        pass

    @abstractmethod
    async def scan(
        self, pattern: str = "*", cursor: int = 0, count: int = 100
    ) -> Tuple[int, List[str]]:
        """
        Scan keys with cursor-based pagination.
        Returns: (next_cursor, list_of_keys)
        """
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        pass

    @abstractmethod
    async def ttl(self, key: str) -> Optional[int]:
        """
        Get remaining TTL for key (seconds).
        Returns None if error, -1 if no TTL, -2 if not exists.
        """
        pass

    @abstractmethod
    async def ping(self) -> bool:
        """Health check. Returns True if backend is reachable."""
        pass

    async def close(self) -> None:
        """Close backend connection. Optional override."""
        pass
