"""Admin API routes for cache management."""

from typing import Any, List, Optional, Sequence

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from ..service import CacheService


class KeyInfo(BaseModel):
    """Cache key information."""

    key: str
    ttl: Optional[int]


class KeysResponse(BaseModel):
    """Response for list keys with pagination."""

    keys: List[KeyInfo]
    cursor: int = 0


class ClearResponse(BaseModel):
    """Response for clear operations."""

    message: str
    cleared_count: int


class StatsResponse(BaseModel):
    """Cache statistics response."""

    hits: int
    misses: int
    total: int
    hit_rate: float


def create_admin_router(
    cache_service: CacheService,
    dependencies: Optional[Sequence[Any]] = None,
) -> APIRouter:
    """
    Create admin router for cache management.

    Routes:
    - GET /keys - List all cache keys (paginated)
    - DELETE /keys/{key} - Delete specific key
    - POST /clear - Clear all or by pattern
    - GET /stats - Get cache statistics
    - GET /health - Health check

    Args:
        cache_service: CacheService instance to operate on.
        dependencies: Optional sequence of FastAPI dependencies (e.g. auth)
            that will be applied to all admin routes.
    """
    router = APIRouter(dependencies=list(dependencies) if dependencies else None)

    @router.get("/keys", response_model=KeysResponse)
    async def list_keys(
        pattern: str = Query("*", description="Glob pattern"),
        limit: int = Query(100, description="Items per page"),
        cursor: int = Query(0, description="Cursor for pagination"),
    ):
        """List cache keys matching pattern (paginated)."""
        result = await cache_service.list_keys(pattern, limit=limit, cursor=cursor)
        return result

    @router.delete("/keys/{key}")
    async def delete_key(key: str):
        """Delete a specific cache key."""
        success = await cache_service.delete(key)
        if not success:
            raise HTTPException(status_code=404, detail=f"Key '{key}' not found")
        return {"message": f"Key '{key}' deleted"}

    @router.post("/clear", response_model=ClearResponse)
    async def clear_cache(pattern: Optional[str] = Query(None, description="Glob pattern")):
        """
        Clear cache.

        - No pattern: Clears all cache
        - With pattern: Clears keys matching glob pattern
        """
        if pattern:
            cleared_count = await cache_service.clear_pattern(pattern)
            return ClearResponse(
                message=f"Cleared keys matching pattern: {pattern}", cleared_count=cleared_count
            )
        else:
            cleared_count = await cache_service.clear_all()
            return ClearResponse(message="All cache cleared", cleared_count=cleared_count)

    @router.get("/stats", response_model=StatsResponse)
    async def get_stats():
        """Get cache statistics (hits, misses, hit rate)."""
        stats = cache_service.get_stats()
        return StatsResponse(**stats)

    @router.get("/health")
    async def health_check():
        """Check cache backend health."""
        is_healthy = await cache_service.ping()
        if not is_healthy:
            raise HTTPException(status_code=503, detail="Cache backend is unhealthy")
        return {"status": "healthy"}

    return router
