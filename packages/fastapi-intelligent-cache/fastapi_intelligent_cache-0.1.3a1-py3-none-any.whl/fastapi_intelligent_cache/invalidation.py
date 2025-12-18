"""
Cache invalidation strategies.

Ported from: services/apis/mobile-app-bff/src/app/modules/cache/interceptors/cache-write-invalidation.interceptor.ts
"""

from typing import List

from .key_generator import is_id_like, normalize_path


def generate_invalidation_patterns(method: str, path: str) -> List[str]:
    """
    Generate cache patterns to invalidate on write operations.

    Strategy:
    1. Clear current resource and its children (GET:resource:id*)
    2. Walk up hierarchy, clearing parent lists where segments are IDs

    Args:
        method: HTTP method (POST, PUT, PATCH, DELETE)
        path: Request path

    Returns:
        List of glob patterns to clear

    Examples:
        PATCH /api/spaces/123
        → ['GET:spaces:123*', 'GET:spaces:*']

        POST /api/spaces/123/items
        → ['GET:spaces:123:items*', 'GET:spaces:123:*', 'GET:spaces:*']

        DELETE /api/spaces/123/items/456
        → ['GET:spaces:123:items:456*', 'GET:spaces:123:items:*',
           'GET:spaces:123:*', 'GET:spaces:*']
    """
    # Normalize path
    normalized = normalize_path(path)

    if not normalized:
        return []

    # Split into segments
    segments = normalized.split(":")

    patterns: List[str] = []

    # Always clear the current resource and its children
    patterns.append(f"GET:{normalized}*")

    # Walk up the hierarchy
    # For each ID-like segment, clear the parent collection AND the resource itself
    for i in range(len(segments) - 1, 0, -1):
        if is_id_like(segments[i]):
            # 1. Clear parent collection (e.g. spaces:*)
            parent_path = ":".join(segments[:i])
            if parent_path:
                patterns.append(f"GET:{parent_path}:*")
                patterns.append(f"GET:{parent_path}")

            # 2. Clear the specific resource (e.g. spaces:123:*)
            # This covers the resource detail and any direct sub-resources not covered by the initial clear
            # (though initial clear matches normalized*, which covers deeply nested.
            #  But if we are at items:456, we also want to clear spaces:123 whatever)
            resource_path = ":".join(segments[: i + 1])
            patterns.append(f"GET:{resource_path}:*")

    # Also clear keys that include a custom prefix BEFORE "GET:".
    # Example: @cache_config(key_prefix="tenantA") results in keys like:
    #   tenantA:GET:spaces:123
    # Invalidation is path-based and doesn't know per-endpoint prefixes, so we
    # include wildcard-prefixed patterns to ensure they are cleared too.
    wildcard_prefix_patterns: List[str] = []
    for p in patterns:
        if p.startswith("GET:"):
            wildcard_prefix_patterns.append(f"*:{p}")

    # De-duplicate while preserving order
    all_patterns = patterns + wildcard_prefix_patterns
    deduped: List[str] = []
    seen = set()
    for p in all_patterns:
        if p not in seen:
            seen.add(p)
            deduped.append(p)

    return deduped


def should_invalidate(method: str, status_code: int, path: str) -> bool:
    """
    Determine if a request should trigger cache invalidation.

    Rules:
    1. Only POST, PUT, PATCH, DELETE methods
    2. Only 2xx status codes (success)
    3. Skip admin cache routes

    Args:
        method: HTTP method
        status_code: Response status code
        path: Request path

    Returns:
        True if should invalidate cache
    """
    # Only write methods
    if method not in ("POST", "PUT", "PATCH", "DELETE"):
        return False

    # Only successful responses
    if not (200 <= status_code < 300):
        return False

    # Skip cache admin routes to avoid recursion
    if "/api/cache" in path or "/cache/" in path:
        return False

    return True
