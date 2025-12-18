"""
Web Page Read Tool - Native aiohttp implementation.

Fetches a URL and returns cleaned, plain text content suitable for
LLM-based research agents. No heavy HTML parsing dependencies by default.

Optional extractor (via extras) can improve robustness for messy pages:
- trafilatura (recommended) when installed.
"""

from __future__ import annotations

import asyncio
import html as html_lib
import logging
import os
import random
import re
import time
from collections import OrderedDict
from contextlib import asynccontextmanager, nullcontext
from typing import Any, Optional

import aiohttp

from saptiva_agents.core import ROOT_LOGGER_NAME, get_request_id
from saptiva_agents.core._research_context import Source, get_research_context
from saptiva_agents.core._singletons import get_global_cache, get_global_rate_limiter
from saptiva_agents.tools._saptiva_tool import SaptivaTool


logger = logging.getLogger(ROOT_LOGGER_NAME)

DEFAULT_MAX_CHARS = 6000
DEFAULT_TIMEOUT_S = 15.0
_RETRYABLE_STATUSES = {429, 500, 502, 503, 504}

try:  # Optional OpenTelemetry support (no hard dependency)
    from opentelemetry import trace  # type: ignore
except Exception:  # pragma: no cover
    trace = None  # type: ignore


def _span(name: str, **attrs):  # type: ignore
    if trace is None:
        return nullcontext()
    tracer = trace.get_tracer(ROOT_LOGGER_NAME)
    return tracer.start_as_current_span(name, attributes=attrs)

_SCRIPT_STYLE_RE = re.compile(r"(?is)<(script|style|noscript).*?>.*?</\\1>")
_TAG_RE = re.compile(r"(?s)<[^>]+>")
_WHITESPACE_RE = re.compile(r"\\s+")
_TITLE_RE = re.compile(r"(?is)<title[^>]*>(.*?)</title>")


def _extract_title(html_text: str) -> Optional[str]:
    match = _TITLE_RE.search(html_text)
    if not match:
        return None
    title = html_lib.unescape(match.group(1)).strip()
    return title or None


def _html_to_text(html_text: str) -> str:
    # Remove scripts/styles
    text = _SCRIPT_STYLE_RE.sub(" ", html_text)
    # Strip tags
    text = _TAG_RE.sub(" ", text)
    # Unescape entities
    text = html_lib.unescape(text)
    # Collapse whitespace
    return _WHITESPACE_RE.sub(" ", text).strip()


class WebReadTool(SaptivaTool[dict]):
    """
    Read and clean text from a web page.

    Example:
        tool = WebReadTool()
        page = await tool("https://example.com")
    """

    name: str = "read_page"
    description: str = (
        "Descarga una URL y devuelve texto limpio con metadatos (title, final_url). "
        "Útil para agentes de investigación."
    )

    def __init__(
        self,
        timeout_s: float = DEFAULT_TIMEOUT_S,
        max_chars: int = DEFAULT_MAX_CHARS,
        headers: Optional[dict[str, str]] = None,
        extractor: str = "simple",
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
        # Retry / rate-limit tuning (env overrides are optional)
        env_retries = os.getenv("SAPTIVA_READ_MAX_RETRIES")
        if env_retries:
            try:
                max_retries = int(env_retries)
            except ValueError:
                pass
        env_min_interval = os.getenv("SAPTIVA_READ_MIN_INTERVAL_S")
        if env_min_interval:
            try:
                min_interval_s = float(env_min_interval)
            except ValueError:
                pass

        self.timeout_s = timeout_s
        self.max_chars = max_chars
        self.headers = headers or {
            "User-Agent": "SaptivaAgents/0.2.5 (+https://saptiva.com) aiohttp",
            "Accept": "text/html,application/xhtml+xml",
        }
        self.extractor = (extractor or "simple").strip().lower()
        self.max_retries = max(0, int(max_retries))
        self.backoff_base_s = max(0.0, float(backoff_base_s))
        self.backoff_max_s = max(self.backoff_base_s, float(backoff_max_s))
        self.min_interval_s = max(0.0, float(min_interval_s))

        self.cache_ttl_s = max(0.0, float(cache_ttl_s))
        self.cache_max_entries = max(0, int(cache_max_entries))
        self._cache: OrderedDict[tuple[Any, ...], tuple[float, dict[str, Any]]] = OrderedDict()
        self._cache_lock = asyncio.Lock()

        self._rate_lock = asyncio.Lock()
        self._last_request_ts = 0.0

        self._session: Optional[aiohttp.ClientSession] = session
        self._owns_session = False
        self._reuse_session = bool(reuse_session)
        self._session_lock = asyncio.Lock()

        # Global singletons integration
        self._use_global_cache = bool(use_global_cache)
        self._use_global_rate_limiter = bool(use_global_rate_limiter)

    async def _arun(
        self,
        url: str,
        timeout_s: Optional[float] = None,
        max_chars: Optional[int] = None,
        extractor: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> dict:
        if not isinstance(url, str) or not url.strip():
            return {"success": False, "error": "URL inválida.", "url": url, "text": ""}

        request_id = request_id or get_request_id()
        timeout_s = timeout_s or self.timeout_s
        max_chars = max_chars or self.max_chars
        extractor = (extractor or self.extractor or "simple").strip().lower()

        # Check research context for already visited/failed URLs
        research_ctx = get_research_context()
        if research_ctx is not None:
            if research_ctx.should_skip_url(url):
                logger.info("read_page skipping url=%s (already visited/failed) request_id=%s", url, request_id)
                return {
                    "success": False,
                    "error": "URL already visited or previously failed",
                    "url": url,
                    "text": "",
                    "skipped": True,
                }

        cache_key = (url.strip(), extractor, max_chars)
        cached = await self._cache_get(cache_key)
        if cached is not None:
            logger.info("read_page cache_hit url=%s request_id=%s", url, request_id)
            cached["cached"] = True
            return cached

        start = time.time()
        try:
            with _span("read_page", url=url, extractor=extractor, request_id=request_id or ""):
                timeout = aiohttp.ClientTimeout(total=timeout_s)
                async with self._get_session(timeout=timeout) as session:
                    response, raw_html = await self._fetch_text_with_retries(
                        session=session,
                        url=url,
                        request_id=request_id,
                    )

                final_url = str(response.url)
                content_type = response.headers.get("Content-Type", "")

                title = _extract_title(raw_html)
                text = self._extract_text(raw_html, final_url, extractor)

            if len(text) > max_chars:
                text = text[:max_chars] + "..."

            elapsed = (time.time() - start) * 1000
            logger.info(
                "read_page url=%s chars=%d ms=%.1f extractor=%s request_id=%s",
                final_url,
                len(text),
                elapsed,
                extractor,
                request_id,
            )

            result = {
                "success": True,
                "url": url,
                "final_url": final_url,
                "content_type": content_type,
                "title": title,
                "text": text,
                "extractor": extractor,
            }
            await self._cache_set(cache_key, result)

            # Add source to research context if available
            if research_ctx is not None:
                research_ctx.add_source(
                    Source(
                        url=final_url,
                        title=title,
                        content=text[:500] if text else None,
                    )
                )

            return result
        except Exception as e:
            logger.exception("read_page failed url=%r", url)
            # Mark URL as failed in research context
            if research_ctx is not None:
                research_ctx.mark_failed(url, reason=str(e))
            return {"success": False, "error": str(e), "url": url, "text": ""}

    async def _cache_get(self, key: tuple[Any, ...]) -> Optional[dict[str, Any]]:
        # Use global cache if enabled
        if self._use_global_cache:
            cache = get_global_cache()
            cache_key_str = f"read_page:{':'.join(str(k) for k in key)}"
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
            return dict(value)

    async def _cache_set(self, key: tuple[Any, ...], value: dict[str, Any]) -> None:
        # Use global cache if enabled
        if self._use_global_cache:
            cache = get_global_cache()
            cache_key_str = f"read_page:{':'.join(str(k) for k in key)}"
            await cache.set(cache_key_str, value, ttl_s=self.cache_ttl_s)
            return

        # Fall back to instance cache
        if self.cache_ttl_s <= 0 or self.cache_max_entries <= 0:
            return
        now = time.monotonic()
        async with self._cache_lock:
            self._cache[key] = (now, dict(value))
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

    async def _fetch_text_with_retries(
        self,
        session: aiohttp.ClientSession,
        url: str,
        request_id: Optional[str],
    ) -> tuple[aiohttp.ClientResponse, str]:
        total_attempts = self.max_retries + 1
        last_error: Optional[Exception] = None

        for attempt in range(1, total_attempts + 1):
            await self._respect_rate_limit(url)
            try:
                async with session.get(url, allow_redirects=True) as response:
                    if response.status in _RETRYABLE_STATUSES and attempt < total_attempts:
                        retry_after = response.headers.get("Retry-After")
                        delay = self._compute_backoff(attempt)
                        if retry_after:
                            try:
                                delay = max(delay, float(retry_after))
                            except ValueError:
                                pass
                        logger.warning(
                            "read_page retry status=%d attempt=%d delay=%.2f request_id=%s",
                            response.status,
                            attempt,
                            delay,
                            request_id,
                        )
                        await asyncio.sleep(delay)
                        continue

                    if response.status != 200:
                        body = await response.text()
                        raise RuntimeError(f"HTTP {response.status}: {body[:200]}")

                    raw_html = await response.text(errors="ignore")
                    return response, raw_html
            except aiohttp.ClientError as e:
                last_error = e
                if attempt < total_attempts:
                    delay = self._compute_backoff(attempt)
                    logger.warning(
                        "read_page retry error=%s attempt=%d delay=%.2f request_id=%s",
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
        raise RuntimeError("read_page failed with unknown error")

    def _extract_text(self, raw_html: str, final_url: str, extractor: str) -> str:
        if extractor == "trafilatura":
            extracted = self._try_trafilatura(raw_html, final_url)
            if extracted:
                return extracted
            logger.debug("trafilatura unavailable/failed; falling back to simple extractor.")
        return _html_to_text(raw_html)

    @staticmethod
    def _try_trafilatura(raw_html: str, url: str) -> Optional[str]:
        try:
            import trafilatura  # type: ignore

            extracted = trafilatura.extract(
                raw_html,
                url=url,
                include_tables=False,
                include_comments=False,
            )
            if extracted:
                return extracted.strip()
        except Exception:
            return None
        return None

    @asynccontextmanager
    async def _get_session(self, timeout: aiohttp.ClientTimeout):
        if self._session is not None and not self._session.closed:
            yield self._session
            return

        if self._reuse_session:
            async with self._session_lock:
                if self._session is None or self._session.closed:
                    self._session = aiohttp.ClientSession(headers=self.headers, timeout=timeout)
                    self._owns_session = True
            assert self._session is not None
            yield self._session
            return

        async with aiohttp.ClientSession(headers=self.headers, timeout=timeout) as session:
            yield session

    async def aclose(self) -> None:
        """Close any owned persistent aiohttp session."""
        if self._owns_session and self._session is not None and not self._session.closed:
            await self._session.close()


async def read_page(
    url: str,
    timeout_s: float = DEFAULT_TIMEOUT_S,
    max_chars: int = DEFAULT_MAX_CHARS,
    extractor: str = "simple",
    request_id: Optional[str] = None,
) -> dict:
    """Convenience function for reading a URL once."""
    tool = WebReadTool(timeout_s=timeout_s, max_chars=max_chars, extractor=extractor)
    return await tool._arun(
        url=url,
        timeout_s=timeout_s,
        max_chars=max_chars,
        extractor=extractor,
        request_id=request_id,
    )
