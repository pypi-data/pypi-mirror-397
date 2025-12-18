"""Redis cache backend with non-blocking error handling."""

import datetime
import json
import logging
from decimal import Decimal
from typing import Any, List, Optional, Tuple
from uuid import UUID

try:
    import redis.asyncio as redis
except ImportError:
    redis = None  # type: ignore

from .base import CacheBackend

logger = logging.getLogger(__name__)


class EnhancedJSONEncoder(json.JSONEncoder):
    """
    JSON Encoder that handles common Python types.
    - datetime/date -> ISO string
    - UUID -> str
    - Decimal -> float
    """

    def default(self, o: Any) -> Any:
        if isinstance(o, (datetime.datetime, datetime.date)):
            return o.isoformat()
        if isinstance(o, UUID):
            return str(o)
        if isinstance(o, Decimal):
            return float(o)
        return super().default(o)


class RedisBackend(CacheBackend):
    """
    Redis cache backend with graceful error handling.

    Features:
    - Non-blocking: Redis errors don't crash the app
    - Connection pooling
    - Automatic serialization (JSON with extended types)
    - Error logging
    - Cursor-based scan support
    """

    def __init__(
        self,
        url: str = "redis://localhost:6379",
        db: int = 0,
        password: Optional[str] = None,
        decode_responses: bool = False,
        socket_timeout: int = 5,
        socket_connect_timeout: int = 5,
        retry_on_timeout: bool = True,
        max_connections: int = 50,
        key_prefix: str = "",
    ):
        if redis is None:
            raise ImportError(
                "redis package is required for RedisBackend. " "Install it with: pip install redis"
            )

        self.url = url
        self.db = db
        self.password = password
        self.decode_responses = decode_responses
        self.socket_timeout = socket_timeout
        self.socket_connect_timeout = socket_connect_timeout
        self.retry_on_timeout = retry_on_timeout
        self.max_connections = max_connections
        self.key_prefix = key_prefix
        self._client: Optional[redis.Redis] = None
        self._connected = False

    def _add_prefix(self, key: str) -> str:
        """Add key prefix if configured."""
        if self.key_prefix:
            return f"{self.key_prefix}:{key}"
        return key

    def _remove_prefix(self, key: str) -> str:
        """Remove key prefix if configured."""
        if self.key_prefix and key.startswith(f"{self.key_prefix}:"):
            return key[len(self.key_prefix) + 1 :]
        return key

    async def _get_client(self) -> Optional[redis.Redis]:
        """Get or create Redis client with error handling."""
        if self._client is not None:
            return self._client

        try:
            self._client = redis.from_url(
                self.url,
                db=self.db,
                password=self.password,
                decode_responses=self.decode_responses,
                socket_timeout=self.socket_timeout,
                socket_connect_timeout=self.socket_connect_timeout,
                retry_on_timeout=self.retry_on_timeout,
                max_connections=self.max_connections,
            )
            await self._client.ping()
            self._connected = True
            logger.info(f"Redis connected: {self.url}")
            return self._client
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            self._connected = False
            return None

    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis, return None on error."""
        try:
            client = await self._get_client()
            if client is None:
                return None

            prefixed_key = self._add_prefix(key)
            value = await client.get(prefixed_key)

            if value is None:
                return None

            # Deserialize
            if isinstance(value, bytes):
                value = value.decode("utf-8")

            return json.loads(value)
        except Exception as e:
            logger.error(f"Redis GET error for key '{key}': {e}")
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in Redis, return False on error."""
        try:
            client = await self._get_client()
            if client is None:
                return False

            prefixed_key = self._add_prefix(key)

            # Serialize with custom encoder
            serialized = json.dumps(value, cls=EnhancedJSONEncoder)

            # Set with optional TTL
            if ttl:
                await client.setex(prefixed_key, ttl, serialized)
            else:
                await client.set(prefixed_key, serialized)

            return True
        except Exception as e:
            logger.error(f"Redis SET error for key '{key}': {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from Redis."""
        try:
            client = await self._get_client()
            if client is None:
                return False

            prefixed_key = self._add_prefix(key)
            await client.delete(prefixed_key)
            return True
        except Exception as e:
            logger.error(f"Redis DELETE error for key '{key}': {e}")
            return False

    async def clear(self, pattern: str = "*") -> int:
        """Clear keys matching pattern."""
        count = 0
        # IMPORTANT: Use _add_prefix so empty prefix doesn't produce ':*'
        prefixed_pattern = self._add_prefix(pattern)

        # Batch deletion using pipeline
        keys_to_delete = []
        batch_size = 1000

        # Check if client available
        client = await self._get_client()
        if client is None:
            return 0

        async for k in client.scan_iter(match=prefixed_pattern):
            keys_to_delete.append(k)
            if len(keys_to_delete) >= batch_size:
                await client.delete(*keys_to_delete)
                count += len(keys_to_delete)
                keys_to_delete = []

        if keys_to_delete:
            await client.delete(*keys_to_delete)
            count += len(keys_to_delete)

        return count

    async def scan(
        self, pattern: str = "*", cursor: int = 0, count: int = 100
    ) -> Tuple[int, List[str]]:
        """
        Scan keys with cursor-based pagination.

        Returns:
            Tuple[next_cursor, list_of_keys]
        """
        try:
            client = await self._get_client()
            if client is None:
                return 0, []

            prefixed_pattern = self._add_prefix(pattern)

            # Redis SCAN returns (cursor, [keys])
            next_cursor, keys = await client.scan(
                cursor=cursor, match=prefixed_pattern, count=count
            )

            # Decode and remove prefix
            decoded_keys = []
            for k in keys:
                if isinstance(k, bytes):
                    k = k.decode("utf-8")
                decoded_keys.append(self._remove_prefix(k))

            return next_cursor, decoded_keys
        except Exception as e:
            logger.error(f"Redis SCAN error: {e}")
            return 0, []

    async def keys(self, pattern: str = "*") -> List[str]:
        """
        List all keys matching pattern.

        WARNING: unsafe for large datasets. Use scan() instead.
        Kept for backward compatibility.
        """
        try:
            client = await self._get_client()
            if client is None:
                return []

            # Reuse scan to avoid blocking, but still accumulate everything
            # This is still dangerous for memory but non-blocking for Redis
            keys = []
            cursor = 0
            while True:
                cursor, batch = await self.scan(pattern, cursor, count=1000)
                keys.extend(batch)
                if cursor == 0:
                    break

            return keys
        except Exception as e:
            logger.error(f"Redis KEYS error: {e}")
            return []

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        try:
            client = await self._get_client()
            if client is None:
                return False

            prefixed_key = self._add_prefix(key)
            return await client.exists(prefixed_key) > 0
        except Exception as e:
            logger.error(f"Redis EXISTS error for key '{key}': {e}")
            return False

    async def ttl(self, key: str) -> Optional[int]:
        """Get remaining TTL (seconds), -1 if no TTL, -2 if not exists."""
        try:
            client = await self._get_client()
            if client is None:
                return None

            prefixed_key = self._add_prefix(key)
            return await client.ttl(prefixed_key)
        except Exception as e:
            logger.error(f"Redis TTL error for key '{key}': {e}")
            return None

    async def ping(self) -> bool:
        """Health check."""
        try:
            client = await self._get_client()
            if client is None:
                return False

            await client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis PING error: {e}")
            return False

    async def close(self) -> None:
        """Close Redis connection."""
        if self._client:
            await self._client.close()
            self._client = None
            self._connected = False
