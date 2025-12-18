"""@cache_config decorator for endpoint-level cache configuration."""

from functools import wraps
from typing import Any, Callable, Optional

# Metadata key for storing cache config on endpoint functions
CACHE_CONFIG_KEY = "_cache_config"


class CacheConfig:
    """Cache configuration for an endpoint."""

    def __init__(
        self,
        enabled: bool = True,
        ttl_seconds: Optional[int] = None,
        key_prefix: Optional[str] = None,
        vary_by: Optional[list] = None,
    ):
        self.enabled = enabled
        self.ttl_seconds = ttl_seconds
        self.key_prefix = key_prefix
        self.vary_by = vary_by or []


def cache_config(
    enabled: bool = True,
    ttl_seconds: Optional[int] = None,
    key_prefix: Optional[str] = None,
    vary_by: Optional[list] = None,
) -> Callable:
    """
    Decorator to configure caching for a FastAPI endpoint.

    Args:
        enabled: Whether caching is enabled for this endpoint
        ttl_seconds: Time-to-live in seconds (overrides default)
        key_prefix: Custom prefix added in front of generated cache keys
        vary_by: List of attribute names on `request.state` to vary cache by
                 (e.g., ['user_id']). These attributes are read at runtime
                 by the middleware and included in the cache key.

    Examples:
        @app.get("/spaces")
        @cache_config(ttl_seconds=3600)
        async def list_spaces():
            ...

        @app.get("/spaces/{space_id}")
        @cache_config(ttl_seconds=86400)
        async def get_space(space_id: str):
            ...

        @app.get("/my-profile")
        @cache_config(ttl_seconds=300, vary_by=["user_id"])
        async def get_profile(request: Request):
            # `request.state.user_id` will be used as part of the cache key
            ...
    """

    def decorator(func: Callable) -> Callable:
        # Store config as metadata on function
        config = CacheConfig(
            enabled=enabled,
            ttl_seconds=ttl_seconds,
            key_prefix=key_prefix,
            vary_by=vary_by,
        )
        setattr(func, CACHE_CONFIG_KEY, config)

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            return await func(*args, **kwargs)

        # Preserve the config on wrapper
        setattr(wrapper, CACHE_CONFIG_KEY, config)

        return wrapper

    return decorator


def get_cache_config(func: Callable) -> Optional[CacheConfig]:
    """
    Extract cache config from endpoint function.

    Args:
        func: Endpoint function

    Returns:
        CacheConfig if present, None otherwise
    """
    return getattr(func, CACHE_CONFIG_KEY, None)
