"""Cache manager for FastAPI integration."""

import logging
from typing import Any, List, Optional, Sequence

from fastapi import FastAPI

from .backends.base import CacheBackend
from .backends.memory import MemoryBackend
from .middleware import CacheMiddleware, InvalidationMiddleware
from .service import CacheService

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Central manager for cache integration with FastAPI.

    Usage:
        app = FastAPI()

        cache_manager = CacheManager(
            backend=RedisBackend(url="redis://localhost:6379"),
            default_ttl=60,
        )
        cache_manager.init_app(app)
    """

    def __init__(
        self,
        backend: Optional[CacheBackend] = None,
        default_ttl: int = 60,
        enabled: bool = True,
        include_admin_routes: bool = False,
        admin_auth_dependency: Optional[Any] = None,
        admin_dependencies: Optional[Sequence[Any]] = None,
        max_response_size: int = 10 * 1024 * 1024,  # 10MB default
    ):
        """
        Initialize cache manager.

        Args:
            backend: Cache backend (defaults to MemoryBackend)
            default_ttl: Default TTL in seconds
            enabled: Whether caching is enabled globally
            include_admin_routes: Whether to mount admin routes
            admin_auth_dependency: Single dependency for admin routes (convenience)
            admin_dependencies: Sequence of dependencies for admin routes
            max_response_size: Maximum response size to cache (bytes). Responses
                larger than this will not be cached. Default: 10MB
        """
        # Validate parameters
        if default_ttl < 0:
            raise ValueError("default_ttl must be non-negative")

        if max_response_size <= 0:
            raise ValueError("max_response_size must be positive")

        if max_response_size > 100 * 1024 * 1024:  # 100MB
            logger.warning(
                f"max_response_size is very large ({max_response_size} bytes). "
                "This may cause memory issues. Recommended: 10MB or less."
            )

        self.backend = backend or MemoryBackend()
        self.default_ttl = default_ttl
        self.enabled = enabled
        self.include_admin_routes = include_admin_routes
        self.max_response_size = max_response_size
        self.service = CacheService(self.backend)

        # Admin route dependencies (e.g. auth). If both are provided, the explicit
        # `admin_dependencies` wins. `admin_auth_dependency` is a convenience for
        # the common single-dependency case.
        if admin_dependencies is not None:
            self.admin_dependencies: List[Any] = list(admin_dependencies)
        elif admin_auth_dependency is not None:
            self.admin_dependencies = [admin_auth_dependency]
        else:
            self.admin_dependencies = []
        self._app: Optional[FastAPI] = None

    def init_app(self, app: FastAPI) -> None:
        """
        Initialize cache with FastAPI app.

        Registers middleware and optionally admin routes.
        """
        self._app = app

        if not self.enabled:
            logger.warning("Cache is disabled")
            return

        # Register middleware
        # CRITICAL: Middlewares execute in REVERSE order of registration
        # So register CacheMiddleware first (it will execute first), then InvalidationMiddleware
        # This ensures: Request → CacheMiddleware (read) → ... → InvalidationMiddleware (write)
        app.add_middleware(
            CacheMiddleware,
            cache_service=self.service,
            default_ttl=self.default_ttl,
            max_response_size=self.max_response_size,
        )
        app.add_middleware(InvalidationMiddleware, cache_service=self.service)

        # Store service in app state for dependency injection
        app.state.cache_service = self.service

        # Optionally register admin routes
        if self.include_admin_routes:
            self._register_admin_routes(app)

        logger.info(f"Cache initialized with {self.backend.__class__.__name__}")

    def _register_admin_routes(self, app: FastAPI) -> None:
        """Register admin API routes."""
        from .admin.routes import create_admin_router

        router = create_admin_router(self.service, dependencies=self.admin_dependencies)
        app.include_router(router, prefix="/api/cache", tags=["cache"])

        logger.info("Admin cache routes registered at /api/cache")

    async def close(self) -> None:
        """Close cache backend connection."""
        await self.backend.close()
