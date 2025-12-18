"""
Web Search Tool - Native implementation with pluggable providers.

This module provides a minimal, production-oriented web search tool that can be
used by Saptiva/AutoGen agents. It intentionally avoids heavy dependencies and
relies only on aiohttp.

Current providers:
- searxng: JSON API compatible with SearXNG instances (self-hosted).
- tavily: Tavily Search API (SaaS, configurable endpoint).

The tool returns structured results suitable for multi-agent research patterns.
"""

from __future__ import annotations

import asyncio
import logging
import os
import random
import time
from collections import OrderedDict
from contextlib import asynccontextmanager, nullcontext
from typing import Any, Optional

import aiohttp

from saptiva_agents import DEFAULT_LANG
from saptiva_agents.core import ROOT_LOGGER_NAME, get_request_id
from saptiva_agents.core._research_context import get_research_context
from saptiva_agents.core._singletons import get_global_cache, get_global_rate_limiter
from saptiva_agents.tools._saptiva_tool import SaptivaTool

try:  # Optional OpenTelemetry support (no hard dependency)
    from opentelemetry import trace  # type: ignore
except Exception:  # pragma: no cover
    trace = None  # type: ignore


logger = logging.getLogger(ROOT_LOGGER_NAME)

_RETRYABLE_STATUSES = {429, 500, 502, 503, 504}


def _span(name: str, **attrs):  # type: ignore
    if trace is None:
        return nullcontext()
    tracer = trace.get_tracer(ROOT_LOGGER_NAME)
    return tracer.start_as_current_span(name, attributes=attrs)


class WebSearchTool(SaptivaTool[dict]):
    """
    Web search tool using a configurable provider (default: SearXNG).

    Example:
        tool = WebSearchTool(base_url="https://searx.example.com")
        results = await tool("quantum computing", num_results=5)
    """

    name: str = "web_search"
    description: str = (
        "Busca en la web usando un proveedor configurable y retorna resultados "
        "estructurados (título, url, snippet, fuente)."
    )

    def __init__(
        self,
        provider: Optional[str] = None,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout_s: float = 10.0,
        safe_search: bool = True,
        lang: str = DEFAULT_LANG,
        max_retries: int = 2,
        backoff_base_s: float = 0.4,
        backoff_max_s: float = 4.0,
        min_interval_s: float = 0.0,
        cache_ttl_s: float = 300.0,
        cache_max_entries: int = 128,
        session: Optional[aiohttp.ClientSession] = None,
        reuse_session: bool = False,
        use_global_cache: bool = False,
        use_global_rate_limiter: bool = False,
    ) -> None:
        resolved_provider = (
            (provider or os.getenv("SAPTIVA_SEARCH_PROVIDER") or os.getenv("SEARCH_PROVIDER") or "searxng")
            .strip()
            .lower()
        )
        self.provider = resolved_provider

        if resolved_provider == "tavily":
            self.base_url = (
                base_url
                or os.getenv("SAPTIVA_TAVILY_BASE_URL")
                or os.getenv("TAVILY_BASE_URL")
                or "https://api.tavily.com/search"
            )
            self.api_key = (
                api_key
                or os.getenv("SAPTIVA_TAVILY_API_KEY")
                or os.getenv("TAVILY_API_KEY")
                or os.getenv("SAPTIVA_SEARCH_API_KEY")
            )
        else:
            # Default to searxng
            self.base_url = (
                base_url
                or os.getenv("SAPTIVA_SEARCH_BASE_URL")
                or os.getenv("SEARXNG_BASE_URL")
            )
            self.api_key = api_key or os.getenv("SAPTIVA_SEARCH_API_KEY") or os.getenv("SEARXNG_API_KEY")

        # Retry / rate-limit tuning (env overrides are optional)
        env_retries = os.getenv("SAPTIVA_SEARCH_MAX_RETRIES")
        if env_retries:
            try:
                max_retries = int(env_retries)
            except ValueError:
                pass
        env_min_interval = os.getenv("SAPTIVA_SEARCH_MIN_INTERVAL_S")
        if env_min_interval:
            try:
                min_interval_s = float(env_min_interval)
            except ValueError:
                pass

        self.timeout_s = timeout_s
        self.safe_search = safe_search
        self.lang = lang
        self.max_retries = max(0, int(max_retries))
        self.backoff_base_s = max(0.0, float(backoff_base_s))
        self.backoff_max_s = max(self.backoff_base_s, float(backoff_max_s))
        self.min_interval_s = max(0.0, float(min_interval_s))

        # Simple in-memory cache per tool instance.
        self.cache_ttl_s = max(0.0, float(cache_ttl_s))
        self.cache_max_entries = max(0, int(cache_max_entries))
        self._cache: OrderedDict[tuple[Any, ...], tuple[float, list[dict[str, Any]]]] = OrderedDict()
        self._cache_lock = asyncio.Lock()

        # Rate limiting across concurrent calls.
        self._rate_lock = asyncio.Lock()
        self._last_request_ts = 0.0

        # Optional persistent session pooling.
        self._session: Optional[aiohttp.ClientSession] = session
        self._owns_session = False
        self._reuse_session = bool(reuse_session)
        self._session_lock = asyncio.Lock()

        # Global singletons integration
        self._use_global_cache = bool(use_global_cache)
        self._use_global_rate_limiter = bool(use_global_rate_limiter)

    async def _arun(
        self,
        query: str,
        num_results: int = 5,
        lang: Optional[str] = None,
        safe_search: Optional[bool] = None,
        request_id: Optional[str] = None,
    ) -> dict:
        """
        Execute web search and return structured results.

        Args:
            query: Search query
            num_results: Max number of results (1-20)
            lang: Optional override for language code
            safe_search: Optional override for safe search

        Returns:
            dict with keys: success, query, provider, results, error(optional)
        """
        if not isinstance(query, str) or not query.strip():
            return {"success": False, "results": [], "error": "Query vacío o inválido."}

        if num_results < 1:
            num_results = 1
        if num_results > 20:
            num_results = 20

        request_id = request_id or get_request_id()
        provider = (self.provider or "searxng").lower()
        lang = lang or self.lang
        safe_search = self.safe_search if safe_search is None else safe_search

        # Track query in research context if available
        research_ctx = get_research_context()
        if research_ctx is not None:
            # Track the query (returns False if already used)
            research_ctx.add_query(query)

        cache_key = (provider, query.strip().lower(), num_results, lang, bool(safe_search))
        cached = await self._cache_get(cache_key)
        if cached is not None:
            logger.info("web_search cache_hit provider=%s results=%d request_id=%s", provider, len(cached), request_id)
            return {
                "success": True,
                "query": query,
                "provider": provider,
                "results": cached,
                "cached": True,
            }

        if provider not in {"searxng", "tavily"}:
            return {"success": False, "results": [], "error": f"Proveedor de búsqueda no soportado: {provider}"}

        if provider == "searxng" and not self.base_url:
            return {
                "success": False,
                "results": [],
                "error": "base_url no configurado. Define SAPTIVA_SEARCH_BASE_URL o pásalo al tool.",
            }

        if provider == "tavily" and not self.api_key:
            return {
                "success": False,
                "results": [],
                "error": "Tavily api_key no configurado. Define SAPTIVA_TAVILY_API_KEY o pásalo al tool.",
            }

        start = time.time()
        try:
            with _span("web_search", provider=provider, request_id=request_id or ""):
                if provider == "tavily":
                    results = await self._search_tavily(
                        query=query,
                        num_results=num_results,
                        lang=lang,
                        safe_search=safe_search,
                        request_id=request_id,
                    )
                else:
                    results = await self._search_searxng(
                        query=query,
                        num_results=num_results,
                        lang=lang,
                        safe_search=safe_search,
                        request_id=request_id,
                    )
            await self._cache_set(cache_key, results)
            elapsed = (time.time() - start) * 1000
            logger.info(
                "web_search provider=%s results=%d ms=%.1f request_id=%s",
                provider,
                len(results),
                elapsed,
                request_id,
            )
            return {"success": True, "query": query, "provider": provider, "results": results}
        except Exception as e:
            logger.exception("web_search failed provider=%s query=%r", provider, query)
            return {
                "success": False,
                "query": query,
                "provider": provider,
                "results": [],
                "error": str(e),
            }

    async def _cache_get(self, key: tuple[Any, ...]) -> Optional[list[dict[str, Any]]]:
        # Use global cache if enabled
        if self._use_global_cache:
            cache = get_global_cache()
            cache_key_str = f"web_search:{':'.join(str(k) for k in key)}"
            return await cache.get(cache_key_str)

        # Fall back to instance cache
        if self.cache_ttl_s <= 0 or self.cache_max_entries <= 0:
            return None
        now = time.monotonic()
        async with self._cache_lock:
            entry = self._cache.get(key)
            if not entry:
                return None
            ts, value = entry
            if now - ts > self.cache_ttl_s:
                self._cache.pop(key, None)
                return None
            self._cache.move_to_end(key)
            return value

    async def _cache_set(self, key: tuple[Any, ...], value: list[dict[str, Any]]) -> None:
        # Use global cache if enabled
        if self._use_global_cache:
            cache = get_global_cache()
            cache_key_str = f"web_search:{':'.join(str(k) for k in key)}"
            await cache.set(cache_key_str, value, ttl_s=self.cache_ttl_s)
            return

        # Fall back to instance cache
        if self.cache_ttl_s <= 0 or self.cache_max_entries <= 0:
            return
        now = time.monotonic()
        async with self._cache_lock:
            self._cache[key] = (now, value)
            self._cache.move_to_end(key)
            while len(self._cache) > self.cache_max_entries:
                self._cache.popitem(last=False)

    def _compute_backoff(self, attempt: int) -> float:
        delay = min(self.backoff_base_s * (2 ** (attempt - 1)), self.backoff_max_s)
        return delay * random.uniform(0.9, 1.1)

    async def _respect_rate_limit(self, url: Optional[str] = None) -> None:
        # Use global rate limiter if enabled
        if self._use_global_rate_limiter and url:
            limiter = get_global_rate_limiter()
            await limiter.acquire(url)
            return

        # Fall back to instance rate limiting
        if self.min_interval_s <= 0:
            return
        async with self._rate_lock:
            now = time.monotonic()
            wait_s = self.min_interval_s - (now - self._last_request_ts)
            if wait_s > 0:
                await asyncio.sleep(wait_s)
            self._last_request_ts = time.monotonic()

    def _release_rate_limit(self, url: Optional[str] = None) -> None:
        """Release rate limit slot (only for global limiter)."""
        if self._use_global_rate_limiter and url:
            limiter = get_global_rate_limiter()
            limiter.release(url)

    async def _fetch_json_with_retries(
        self,
        session: aiohttp.ClientSession,
        method: str,
        url: str,
        request_id: Optional[str],
        **kwargs: Any,
    ) -> Any:
        total_attempts = self.max_retries + 1
        last_error: Optional[Exception] = None

        for attempt in range(1, total_attempts + 1):
            await self._respect_rate_limit(url)
            try:
                async with session.request(method, url, **kwargs) as response:
                    if response.status in _RETRYABLE_STATUSES and attempt < total_attempts:
                        retry_after = response.headers.get("Retry-After")
                        delay = self._compute_backoff(attempt)
                        if retry_after:
                            try:
                                delay = max(delay, float(retry_after))
                            except ValueError:
                                pass
                        logger.warning(
                            "web_search retry status=%d attempt=%d delay=%.2f request_id=%s",
                            response.status,
                            attempt,
                            delay,
                            request_id,
                        )
                        await asyncio.sleep(delay)
                        continue

                    if response.status != 200:
                        body = await response.text()
                        raise RuntimeError(f"{self.provider} error {response.status}: {body[:200]}")
                    return await response.json()
            except aiohttp.ClientError as e:
                last_error = e
                if attempt < total_attempts:
                    delay = self._compute_backoff(attempt)
                    logger.warning(
                        "web_search retry error=%s attempt=%d delay=%.2f request_id=%s",
                        type(e).__name__,
                        attempt,
                        delay,
                        request_id,
                    )
                    await asyncio.sleep(delay)
                    continue
                raise

        if last_error:
            raise last_error
        raise RuntimeError("web_search failed with unknown error")

    async def _search_searxng(
        self,
        query: str,
        num_results: int,
        lang: str,
        safe_search: bool,
        request_id: Optional[str],
    ) -> list[dict[str, Any]]:
        base_url = self.base_url.rstrip("/")
        url = f"{base_url}/search"

        params: dict[str, Any] = {
            "q": query,
            "format": "json",
            "language": lang,
            "safesearch": 1 if safe_search else 0,
        }
        if self.api_key:
            params["apikey"] = self.api_key

        timeout = aiohttp.ClientTimeout(total=self.timeout_s)
        headers = {
            "User-Agent": "SaptivaAgents/0.2.5 (+https://saptiva.com) aiohttp",
        }

        async with self._get_session(headers=headers, timeout=timeout) as session:
            data = await self._fetch_json_with_retries(
                session,
                "GET",
                url,
                request_id=request_id,
                params=params,
            )

        raw_results = data.get("results", []) if isinstance(data, dict) else []
        results: list[dict[str, Any]] = []
        seen: set[str] = set()

        for item in raw_results:
            link = item.get("url") or item.get("link") or ""
            if not link or link in seen:
                continue
            seen.add(link)
            results.append(
                {
                    "title": item.get("title") or "",
                    "url": link,
                    "snippet": item.get("content") or item.get("snippet") or "",
                    "source": item.get("engine") or item.get("source"),
                    "score": item.get("score"),
                }
            )
            if len(results) >= num_results:
                break

        return results

    async def _search_tavily(
        self,
        query: str,
        num_results: int,
        lang: str,
        safe_search: bool,
        request_id: Optional[str],
    ) -> list[dict[str, Any]]:
        url = (self.base_url or "https://api.tavily.com/search").rstrip("/")
        timeout = aiohttp.ClientTimeout(total=self.timeout_s)
        headers = {
            "User-Agent": "SaptivaAgents/0.2.5 (+https://saptiva.com) aiohttp",
            "Content-Type": "application/json",
        }
        payload: dict[str, Any] = {
            "api_key": self.api_key,
            "query": query,
            "max_results": num_results,
            "search_depth": "basic",
            "include_answer": False,
            "include_raw_content": False,
            "include_images": False,
            "language": lang,
            "safe_search": safe_search,
        }

        async with self._get_session(headers=headers, timeout=timeout) as session:
            data = await self._fetch_json_with_retries(
                session,
                "POST",
                url,
                request_id=request_id,
                json=payload,
            )

        raw_results = data.get("results", []) if isinstance(data, dict) else []
        results: list[dict[str, Any]] = []
        seen: set[str] = set()

        for item in raw_results:
            link = item.get("url") or ""
            if not link or link in seen:
                continue
            seen.add(link)
            results.append(
                {
                    "title": item.get("title") or "",
                    "url": link,
                    "snippet": item.get("content") or "",
                    "source": "tavily",
                    "score": item.get("score") or item.get("relevance_score"),
                }
            )
            if len(results) >= num_results:
                break

        return results

    @asynccontextmanager
    async def _get_session(self, headers: dict[str, str], timeout: aiohttp.ClientTimeout):
        # If caller provided a session, use it.
        if self._session is not None and not self._session.closed:
            yield self._session
            return

        # If we want a persistent session, lazily create and reuse it.
        if self._reuse_session:
            async with self._session_lock:
                if self._session is None or self._session.closed:
                    self._session = aiohttp.ClientSession(headers=headers, timeout=timeout)
                    self._owns_session = True
            assert self._session is not None
            yield self._session
            return

        # Default: ephemeral session per call.
        async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
            yield session

    async def aclose(self) -> None:
        """Close any owned persistent aiohttp session."""
        if self._owns_session and self._session is not None and not self._session.closed:
            await self._session.close()


# Convenience function for direct use (matches tool signature)
async def web_search(
    query: str,
    num_results: int = 5,
    lang: str = DEFAULT_LANG,
    safe_search: bool = True,
    provider: Optional[str] = None,
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
    request_id: Optional[str] = None,
) -> dict:
    """Convenience function to run a one-off web search."""
    tool = WebSearchTool(
        provider=provider,
        base_url=base_url,
        api_key=api_key,
        safe_search=safe_search,
        lang=lang,
    )
    return await tool._arun(
        query=query,
        num_results=num_results,
        lang=lang,
        safe_search=safe_search,
        request_id=request_id,
    )
