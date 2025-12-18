"""
Cache key generation utilities.

Ported from: services/apis/mobile-app-bff/src/app/modules/cache/services/cache-key.util.ts
"""

import hashlib
import json
import re
from typing import Any, Dict, Optional


MAX_CACHE_KEY_PART_LENGTH = 128


def normalize_path(path: str) -> str:
    """
    Normalize API path for cache key.

    Rules:
    1. Strip leading '/api' or '/api/' once
    2. Remove any remaining leading '/'
    3. Replace remaining '/' with ':'

    Examples:
        '/api/spaces' → 'spaces'
        '/api/spaces/123' → 'spaces:123'
        '/spaces/123/items/456' → 'spaces:123:items:456'
    """
    # Strip /api or /api/ prefix
    if path.startswith("/api/"):
        path = path[5:]
    elif path.startswith("/api"):
        path = path[4:]

    # Remove leading /
    path = path.lstrip("/")

    # Replace / with :
    normalized = path.replace("/", ":")

    return normalized


def serialize_query_value(value: Any) -> str:
    """
    Serialize a query parameter value deterministically.

    Handles:
    - None/null
    - Lists (recursive)
    - Dicts (sorted keys)
    - Primitives
    """
    if value is None:
        return "null"

    if isinstance(value, bool):
        return "true" if value else "false"

    if isinstance(value, (int, float)):
        return str(value)

    if isinstance(value, str):
        return value

    if isinstance(value, list):
        # Recursively serialize list items
        serialized_items = [serialize_query_value(item) for item in value]
        return json.dumps(serialized_items, separators=(",", ":"), sort_keys=True)

    if isinstance(value, dict):
        # Serialize dict with sorted keys
        return json.dumps(value, separators=(",", ":"), sort_keys=True)

    # Fallback to JSON
    return json.dumps(value, separators=(",", ":"), sort_keys=True)


def extract_query_param_key(query: Dict[str, Any]) -> str:
    """
    Extract and serialize query parameters deterministically.

    Rules:
    1. Sort keys lexicographically
    2. Serialize values deterministically
    3. Join with ':'

    Examples:
        {'b': '2', 'a': '1'} → 'a=1:b=2'
        {} → ''
    """
    if not query:
        return ""

    # Sort keys
    sorted_keys = sorted(query.keys())

    # Build key=value pairs
    parts = []
    for key in sorted_keys:
        value = query[key]
        serialized_value = serialize_query_value(value)
        parts.append(f"{key}={serialized_value}")

    return ":".join(parts)


def compose_key(base_key: str, *parts: str) -> str:
    """
    Compose cache key from base and optional parts.

    Rules:
    1. Filter out empty/None parts
    2. Join with ':'
    3. If total length > MAX_CACHE_KEY_PART_LENGTH, use SHA256 hash

    Examples:
        ('GET:spaces', 'page=1') → 'GET:spaces:page=1'
        ('GET:spaces', 'very_long_string...') → 'GET:spaces:a3f2b9c8...'
    """
    # Filter valid parts
    valid_parts = [p for p in parts if p]

    if not valid_parts:
        return base_key

    # Compose full key
    param_key = ":".join(valid_parts)
    full_key = f"{base_key}:{param_key}"

    # Hash if too long
    if len(param_key) > MAX_CACHE_KEY_PART_LENGTH:
        hash_hex = hashlib.sha256(param_key.encode()).hexdigest()
        return f"{base_key}:{hash_hex}"

    return full_key


def is_id_like(segment: str) -> bool:
    """
    Detect if a path segment looks like an ID.

    Used for intelligent invalidation hierarchy.

    Patterns:
    - Purely numeric: 123, 456
    - UUID-like: 550e8400-e29b-41d4-a716-446655440000
    - MongoDB ObjectId: 507f1f77bcf86cd799439011 (24 hex chars)
    """
    if not segment:
        return False

    # Numeric ID
    if segment.isdigit():
        return True

    # UUID or long hex string (16+ chars)
    if re.match(r"^[0-9a-fA-F-]{16,}$", segment):
        return True

    # MongoDB ObjectId (24 hex chars)
    if re.match(r"^[0-9a-fA-F]{24}$", segment):
        return True

    return False


def generate_cache_key(
    method: str,
    path: str,
    query_params: Optional[Dict[str, Any]] = None,
    vary_by: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Generate deterministic cache key.

    Format: METHOD:normalized_path[:query][:vary][:hash]

    Args:
        method: HTTP method (GET, POST, etc.)
        path: Request path (/api/spaces/123)
        query_params: Query parameters dict
        vary_by: Additional values to vary cache by (e.g., user_id)

    Returns:
        Cache key string

    Examples:
        generate_cache_key('GET', '/api/spaces', {'page': '1'})
        → 'GET:spaces:page=1'

        generate_cache_key('GET', '/api/spaces/123')
        → 'GET:spaces:123'
    """
    # Normalize path
    normalized = normalize_path(path)

    # Base key
    base_key = f"{method}:{normalized}"

    # Extract query params
    query_key = extract_query_param_key(query_params or {})

    # Extract vary_by values
    vary_key = extract_query_param_key(vary_by or {})

    # Compose final key
    return compose_key(base_key, query_key, vary_key)
