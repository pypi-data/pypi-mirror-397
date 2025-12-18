"""
FastAPI Intelligent Cache

A production-ready caching library for FastAPI with intelligent invalidation.
"""

from .decorator import cache_config
from .manager import CacheManager
from .service import CacheService
from .dependencies import get_cache_service

__version__ = "0.1.2"

__all__ = [
    "cache_config",
    "CacheManager",
    "CacheService",
    "get_cache_service",
]
