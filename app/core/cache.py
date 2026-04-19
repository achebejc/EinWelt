"""Redis caching helpers.

Usage:
    from app.core.cache import cache_get, cache_set, cache_delete

    value = cache_get("my-key")
    cache_set("my-key", {"data": 1}, ttl=300)
    cache_delete("my-key")

All values are JSON-serialised. Returns None on cache miss or when Redis is
unavailable (fail-open strategy — the application continues without caching).
"""
import json
import logging
from typing import Any, Optional

import redis as _redis

from app.core.config import settings

logger = logging.getLogger(__name__)

# Module-level Redis client — lazily initialised
_client: Optional[_redis.Redis] = None


def _get_client() -> Optional[_redis.Redis]:
    global _client
    if _client is None:
        try:
            _client = _redis.from_url(
                settings.redis_url,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2,
            )
            _client.ping()
        except Exception as exc:
            logger.warning("Redis unavailable — caching disabled: %s", exc)
            _client = None
    return _client


def cache_get(key: str) -> Optional[Any]:
    """Return the cached value for *key*, or None on miss / error."""
    client = _get_client()
    if client is None:
        return None
    try:
        raw = client.get(key)
        return json.loads(raw) if raw is not None else None
    except Exception as exc:
        logger.debug("cache_get error for key=%s: %s", key, exc)
        return None


def cache_set(key: str, value: Any, ttl: Optional[int] = None) -> None:
    """Serialise *value* to JSON and store it under *key* with optional TTL."""
    client = _get_client()
    if client is None:
        return
    try:
        client.set(key, json.dumps(value, default=str), ex=ttl or settings.cache_ttl)
    except Exception as exc:
        logger.debug("cache_set error for key=%s: %s", key, exc)


def cache_delete(key: str) -> None:
    """Remove *key* from the cache."""
    client = _get_client()
    if client is None:
        return
    try:
        client.delete(key)
    except Exception as exc:
        logger.debug("cache_delete error for key=%s: %s", key, exc)


def cache_delete_pattern(pattern: str) -> None:
    """Remove all keys matching *pattern* (e.g. 'user:*')."""
    client = _get_client()
    if client is None:
        return
    try:
        keys = client.keys(pattern)
        if keys:
            client.delete(*keys)
    except Exception as exc:
        logger.debug("cache_delete_pattern error for pattern=%s: %s", pattern, exc)
