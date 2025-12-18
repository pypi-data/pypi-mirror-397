"""FastAPI dependencies for cache access."""

from fastapi import Request

from .service import CacheService


def get_cache_service(request: Request) -> CacheService:
    """
    FastAPI dependency to inject CacheService.

    Usage:
        @app.post("/admin/clear-cache")
        async def clear_cache(
            cache_service: CacheService = Depends(get_cache_service)
        ):
            await cache_service.clear_all()
            return {"message": "Cache cleared"}
    """
    return request.app.state.cache_service
