"""
Global singletons for rate limiting and caching.

These are shared across all tool instances to provide:
- Per-domain rate limiting (prevents overwhelming external APIs)
- Cross-team cache sharing (reduces redundant requests)

Usage:
    from saptiva_agents.core import get_global_rate_limiter, get_global_cache

    limiter = get_global_rate_limiter()
    await limiter.acquire("https://api.example.com/search")
    try:
        result = await fetch_data()
    finally:
        limiter.release("https://api.example.com/search")

    cache = get_global_cache()
    cached = await cache.get("search:query")
    if cached is None:
        result = await search()
        await cache.set("search:query", result, ttl_s=300)
"""

from __future__ import annotations

import asyncio
import time
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any, Optional
from urllib.parse import urlparse


@dataclass
class RateLimitConfig:
    """Configuration for per-domain rate limiting."""

    min_interval_s: float = 0.5
    """Minimum seconds between requests to same domain."""

    max_concurrent: int = 3
    """Maximum concurrent requests to same domain."""


class GlobalRateLimiter:
    """
    Singleton rate limiter with per-domain semaphores.

    Thread-safe and async-safe. Provides fair access across
    all tool instances sharing the same domain.

    Example:
        limiter = GlobalRateLimiter()
        limiter.configure_domain("api.tavily.com", RateLimitConfig(min_interval_s=1.0))

        async with limiter.limit("https://api.tavily.com/search"):
            result = await fetch()
    """

    _instance: Optional["GlobalRateLimiter"] = None
    _initialized: bool = False

    def __new__(cls) -> "GlobalRateLimiter":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._initialized = True
        self._lock = asyncio.Lock()
        self._domain_semaphores: dict[str, asyncio.Semaphore] = {}
        self._domain_last_request: dict[str, float] = {}
        self._domain_config: dict[str, RateLimitConfig] = {}
        self._default_config = RateLimitConfig()

    def configure_domain(self, domain: str, config: RateLimitConfig) -> None:
        """
        Configure rate limits for a specific domain.

        Args:
            domain: Domain name (e.g., "api.tavily.com")
            config: Rate limit configuration
        """
        self._domain_config[domain.lower()] = config

    def configure_defaults(self, config: RateLimitConfig) -> None:
        """Configure default rate limits for unconfigured domains."""
        self._default_config = config

    def _get_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            parsed = urlparse(url)
            return (parsed.netloc or "unknown").lower()
        except Exception:
            return "unknown"

    async def acquire(self, url: str) -> None:
        """
        Acquire rate limit slot for URL domain.

        Blocks until a slot is available and minimum interval has passed.

        Args:
            url: URL being accessed
        """
        domain = self._get_domain(url)
        config = self._domain_config.get(domain, self._default_config)

        async with self._lock:
            if domain not in self._domain_semaphores:
                self._domain_semaphores[domain] = asyncio.Semaphore(config.max_concurrent)
                self._domain_last_request[domain] = 0.0

        await self._domain_semaphores[domain].acquire()

        # Enforce minimum interval
        async with self._lock:
            now = time.monotonic()
            last = self._domain_last_request.get(domain, 0.0)
            wait_s = config.min_interval_s - (now - last)

        if wait_s > 0:
            await asyncio.sleep(wait_s)

        async with self._lock:
            self._domain_last_request[domain] = time.monotonic()

    def release(self, url: str) -> None:
        """
        Release rate limit slot for URL domain.

        Args:
            url: URL that was accessed
        """
        domain = self._get_domain(url)
        if domain in self._domain_semaphores:
            self._domain_semaphores[domain].release()

    async def __aenter__(self) -> "GlobalRateLimiter":
        return self

    async def __aexit__(self, *args) -> None:
        pass

    def get_stats(self) -> dict[str, Any]:
        """Get rate limiter statistics."""
        return {
            "domains_tracked": len(self._domain_semaphores),
            "configured_domains": list(self._domain_config.keys()),
        }

    @classmethod
    def reset(cls) -> None:
        """Reset singleton instance (for testing)."""
        cls._instance = None


@dataclass
class CacheEntry:
    """Cache entry with TTL."""

    value: Any
    expires_at: float


class GlobalCache:
    """
    Singleton LRU cache with TTL support.

    Shared across all tool instances for search/read results.
    Uses OrderedDict for LRU eviction.

    Example:
        cache = GlobalCache()
        await cache.set("key", {"data": "value"}, ttl_s=300)
        result = await cache.get("key")  # Returns {"data": "value"}
    """

    _instance: Optional["GlobalCache"] = None
    _initialized: bool = False

    def __new__(cls) -> "GlobalCache":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(
        self,
        max_entries: int = 1024,
        default_ttl_s: float = 300.0,
    ) -> None:
        if self._initialized:
            return
        self._initialized = True
        self._lock = asyncio.Lock()
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._max_entries = max_entries
        self._default_ttl_s = default_ttl_s
        self._hits = 0
        self._misses = 0

    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache if not expired.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        async with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                self._misses += 1
                return None

            if time.monotonic() > entry.expires_at:
                self._cache.pop(key, None)
                self._misses += 1
                return None

            # Move to end for LRU
            self._cache.move_to_end(key)
            self._hits += 1
            return entry.value

    async def set(self, key: str, value: Any, ttl_s: Optional[float] = None) -> None:
        """
        Set value in cache with optional TTL override.

        Args:
            key: Cache key
            value: Value to cache
            ttl_s: Optional TTL override (uses default if not specified)
        """
        ttl = ttl_s if ttl_s is not None else self._default_ttl_s
        expires_at = time.monotonic() + ttl

        async with self._lock:
            self._cache[key] = CacheEntry(value=value, expires_at=expires_at)
            self._cache.move_to_end(key)

            # Evict oldest entries if over capacity
            while len(self._cache) > self._max_entries:
                self._cache.popitem(last=False)

    async def delete(self, key: str) -> bool:
        """
        Delete key from cache.

        Returns:
            True if key existed and was deleted
        """
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    async def clear(self) -> None:
        """Clear all cache entries."""
        async with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0

    async def cleanup_expired(self) -> int:
        """
        Remove expired entries.

        Returns:
            Number of entries removed
        """
        now = time.monotonic()
        removed = 0
        async with self._lock:
            expired_keys = [k for k, v in self._cache.items() if now > v.expires_at]
            for key in expired_keys:
                del self._cache[key]
                removed += 1
        return removed

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0.0
        return {
            "entries": len(self._cache),
            "max_entries": self._max_entries,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate_percent": round(hit_rate, 2),
        }

    @classmethod
    def reset(cls) -> None:
        """Reset singleton instance (for testing)."""
        cls._instance = None


# Convenience functions
def get_global_rate_limiter() -> GlobalRateLimiter:
    """Get or create global rate limiter singleton."""
    return GlobalRateLimiter()


def get_global_cache() -> GlobalCache:
    """Get or create global cache singleton."""
    return GlobalCache()
