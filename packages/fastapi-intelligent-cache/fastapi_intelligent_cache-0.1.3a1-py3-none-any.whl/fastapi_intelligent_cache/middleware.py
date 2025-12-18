"""FastAPI middleware for caching and invalidation."""

import base64
import logging
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import StreamingResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.routing import Match
from starlette.types import ASGIApp

from .decorator import get_cache_config
from .invalidation import generate_invalidation_patterns, should_invalidate
from .key_generator import generate_cache_key
from .service import CacheService

logger = logging.getLogger(__name__)


class CacheMiddleware(BaseHTTPMiddleware):
    """
    Middleware for read-through caching.

    Features:
    - Only caches GET requests
    - Respects @cache_config decorator
    - Honors Cache-Control: no-cache header
    - Sets X-Cache: HIT/MISS response header
    """

    def __init__(
        self,
        app: ASGIApp,
        cache_service: CacheService,
        default_ttl: int = 60,
        max_response_size: int = 10 * 1024 * 1024,  # 10MB default
    ):
        super().__init__(app)
        self.cache_service = cache_service
        self.default_ttl = default_ttl
        self.max_response_size = max_response_size

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with caching logic."""

        # Only cache GET requests
        if request.method != "GET":
            return await call_next(request)

        # Check for Cache-Control: no-cache header
        cache_control = request.headers.get("cache-control", "")
        if "no-cache" in cache_control.lower():
            response = await call_next(request)
            response.headers["X-Cache"] = "SKIP"
            return response

        # Get endpoint function
        endpoint = request.scope.get("endpoint")

        # If endpoint not found (middleware runs before router), try to resolve it manually
        if endpoint is None:
            for route in request.app.routes:
                match, child_scope = route.matches(request.scope)
                if match == Match.FULL:
                    endpoint = route.endpoint
                    # Update scope so we don't look it up again (optional, but good practice)
                    request.scope["endpoint"] = endpoint
                    break

        if endpoint is None:
            # Still no endpoint, skip caching
            return await call_next(request)

        # Check if endpoint has cache config
        config = get_cache_config(endpoint)

        # If no config or disabled, skip caching
        if config is None or not config.enabled:
            logger.debug(f"Caching disabled or not configured for {request.url.path}")
            return await call_next(request)

        # Generate cache key
        query_params = dict(request.query_params)

        # Extract vary_by values from request.state based on config
        vary_by_values = {}
        if config.vary_by:
            for attr in config.vary_by:
                # Safely read attributes from request.state
                value = getattr(request.state, attr, None)
                vary_by_values[attr] = value

        cache_key = generate_cache_key(
            method=request.method,
            path=request.url.path,
            query_params=query_params,
            vary_by=vary_by_values or None,
        )

        # Apply optional per-endpoint key prefix if configured
        if config.key_prefix:
            cache_key = f"{config.key_prefix}:{cache_key}"

        # Try to get from cache
        cached_response = await self.cache_service.get(cache_key)

        if cached_response is not None:
            # Cache hit
            logger.debug(f"Cache HIT: {cache_key}")

            # Decode body from base64 if present, else assume bytes (backwards compat/memory backend)
            content = cached_response.get("body", b"")
            if cached_response.get("is_base64"):
                try:
                    content = base64.b64decode(content)
                except Exception:
                    pass  # Keep as is if decode fails

            response = Response(
                content=content,
                status_code=cached_response.get("status_code", 200),
                headers=cached_response.get("headers", {}),
                media_type=cached_response.get("media_type"),
            )
            response.headers["X-Cache"] = "HIT"
            return response

        # Cache miss - call endpoint
        logger.debug(f"Cache MISS: {cache_key}")
        response = await call_next(request)

        # Only cache successful responses
        if 200 <= response.status_code < 300:
            # 1. Check Content-Length header first if available for early exit
            content_length = response.headers.get("content-length")
            if content_length and int(content_length) > self.max_response_size:
                logger.warning(
                    f"Response too large to cache ({content_length} bytes). "
                    f"Max size: {self.max_response_size} bytes."
                )
                response.headers["X-Cache"] = "SKIP"
                return response

            # 2. Safely read body with size limit
            body = b""
            too_large = False
            async for chunk in response.body_iterator:
                body += chunk
                if len(body) > self.max_response_size:
                    too_large = True
                    break

            if too_large:
                logger.warning(
                    f"Response exceeded max cache size during streaming. Aborting cache for {cache_key}"
                )

                async def chained_iterator():
                    yield body
                    async for remaining_chunk in response.body_iterator:
                        yield remaining_chunk

                # Use StreamingResponse for async iterator
                response = StreamingResponse(
                    content=chained_iterator(),
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.media_type,
                )
                response.headers["X-Cache"] = "SKIP"
                return response

            # Prepare cached response
            # Encode body to base64 to ensure JSON serializability (Redis)
            body_b64 = base64.b64encode(body).decode("ascii")

            # Filter sensitive headers
            headers = dict(response.headers)
            headers.pop("set-cookie", None)

            cached_data = {
                "body": body_b64,
                "is_base64": True,
                "status_code": response.status_code,
                "headers": headers,
                "media_type": response.media_type,
            }

            # Determine TTL
            ttl = config.ttl_seconds if config.ttl_seconds else self.default_ttl

            # Store in cache
            await self.cache_service.set(cache_key, cached_data, ttl=ttl)

            # Recreate response with body
            response = Response(
                content=body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )

        response.headers["X-Cache"] = "MISS"
        return response


class InvalidationMiddleware(BaseHTTPMiddleware):
    """
    Middleware for automatic cache invalidation on writes.

    Features:
    - Triggers on POST, PUT, PATCH, DELETE
    - Only on 2xx status codes
    - Hierarchical invalidation
    - Skips admin cache routes
    """

    def __init__(self, app: ASGIApp, cache_service: CacheService):
        super().__init__(app)
        self.cache_service = cache_service

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with invalidation logic."""

        # Execute request first
        response = await call_next(request)

        # Check if we should invalidate
        if should_invalidate(request.method, response.status_code, request.url.path):
            # Generate invalidation patterns
            patterns = generate_invalidation_patterns(request.method, request.url.path)

            # Clear each pattern
            total_cleared = 0
            for pattern in patterns:
                count = await self.cache_service.clear_pattern(pattern)
                total_cleared += count

            if total_cleared > 0:
                logger.info(
                    f"Invalidated {total_cleared} cache entries for "
                    f"{request.method} {request.url.path}"
                )

        return response
