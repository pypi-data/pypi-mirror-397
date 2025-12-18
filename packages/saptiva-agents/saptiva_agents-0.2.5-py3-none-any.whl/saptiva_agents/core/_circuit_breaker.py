"""
Circuit breaker pattern for provider failover.

Tracks failure rates per provider and enables automatic fallback
when a provider becomes unhealthy.

Usage:
    from saptiva_agents.core import get_circuit_breaker

    cb = get_circuit_breaker()

    # Check if provider is available before calling
    if await cb.is_available("searxng"):
        try:
            result = await search_with_searxng()
            await cb.record_success("searxng")
        except Exception:
            await cb.record_failure("searxng")

    # Or get first available from fallback list
    provider = await cb.get_available_provider(["searxng", "tavily"])
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from saptiva_agents._constants import ROOT_LOGGER_NAME

logger = logging.getLogger(ROOT_LOGGER_NAME)


class CircuitState(str, Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation, requests allowed
    OPEN = "open"  # Failing, requests blocked
    HALF_OPEN = "half_open"  # Testing recovery, limited requests


@dataclass
class ProviderStats:
    """Statistics and state for a single provider."""

    failures: int = 0
    """Consecutive failure count."""

    successes: int = 0
    """Consecutive success count (used in half-open state)."""

    last_failure_time: float = 0.0
    """Timestamp of last failure."""

    state: CircuitState = CircuitState.CLOSED
    """Current circuit state."""

    state_changed_at: float = field(default_factory=time.monotonic)
    """Timestamp when state last changed."""

    total_requests: int = 0
    """Total requests through this provider."""

    total_failures: int = 0
    """Total failures (historical)."""


class CircuitBreaker:
    """
    Circuit breaker for managing provider health and failover.

    When a provider's consecutive failure count exceeds threshold,
    the circuit opens and requests fail fast. After recovery timeout,
    circuit becomes half-open to test recovery with limited requests.

    This is a singleton to share state across all tool instances.

    Example:
        cb = CircuitBreaker()
        cb.configure(failure_threshold=5, recovery_timeout_s=60)

        # In tool code:
        provider = await cb.get_available_provider(["searxng", "tavily"])
        if provider is None:
            return {"error": "All providers unavailable"}

        try:
            result = await call_provider(provider)
            await cb.record_success(provider)
        except Exception as e:
            await cb.record_failure(provider)
            raise
    """

    _instance: Optional["CircuitBreaker"] = None
    _initialized: bool = False

    def __new__(cls) -> "CircuitBreaker":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout_s: float = 60.0,
        success_threshold: int = 2,
    ) -> None:
        if self._initialized:
            return
        self._initialized = True
        self._lock = asyncio.Lock()
        self._providers: dict[str, ProviderStats] = {}
        self._failure_threshold = failure_threshold
        self._recovery_timeout_s = recovery_timeout_s
        self._success_threshold = success_threshold

    def configure(
        self,
        failure_threshold: Optional[int] = None,
        recovery_timeout_s: Optional[float] = None,
        success_threshold: Optional[int] = None,
    ) -> None:
        """
        Configure circuit breaker parameters.

        Args:
            failure_threshold: Failures before circuit opens
            recovery_timeout_s: Seconds before half-open state
            success_threshold: Successes in half-open to close circuit
        """
        if failure_threshold is not None:
            self._failure_threshold = max(1, failure_threshold)
        if recovery_timeout_s is not None:
            self._recovery_timeout_s = max(0.01, recovery_timeout_s)  # Allow very short for testing
        if success_threshold is not None:
            self._success_threshold = max(1, success_threshold)

    async def is_available(self, provider: str) -> bool:
        """
        Check if provider is available (circuit not open).

        Args:
            provider: Provider name to check

        Returns:
            True if requests should be allowed
        """
        async with self._lock:
            stats = self._providers.get(provider)
            if stats is None:
                return True

            if stats.state == CircuitState.CLOSED:
                return True

            if stats.state == CircuitState.OPEN:
                # Check if recovery timeout elapsed
                elapsed = time.monotonic() - stats.state_changed_at
                if elapsed > self._recovery_timeout_s:
                    stats.state = CircuitState.HALF_OPEN
                    stats.state_changed_at = time.monotonic()
                    stats.successes = 0
                    logger.info(
                        "circuit_breaker provider=%s state=half_open after %.1fs",
                        provider,
                        elapsed,
                    )
                    return True
                return False

            # HALF_OPEN: allow requests to test recovery
            return True

    async def record_success(self, provider: str) -> None:
        """
        Record successful request to provider.

        Args:
            provider: Provider name
        """
        async with self._lock:
            if provider not in self._providers:
                self._providers[provider] = ProviderStats()

            stats = self._providers[provider]
            stats.total_requests += 1
            stats.failures = 0  # Reset consecutive failures

            if stats.state == CircuitState.HALF_OPEN:
                stats.successes += 1
                if stats.successes >= self._success_threshold:
                    stats.state = CircuitState.CLOSED
                    stats.state_changed_at = time.monotonic()
                    stats.successes = 0
                    logger.info(
                        "circuit_breaker provider=%s state=closed (recovered)",
                        provider,
                    )

    async def record_failure(self, provider: str, error: Optional[str] = None) -> None:
        """
        Record failed request to provider.

        Args:
            provider: Provider name
            error: Optional error description
        """
        async with self._lock:
            if provider not in self._providers:
                self._providers[provider] = ProviderStats()

            stats = self._providers[provider]
            stats.total_requests += 1
            stats.total_failures += 1
            stats.failures += 1
            stats.last_failure_time = time.monotonic()

            if stats.state == CircuitState.HALF_OPEN:
                # Failure during half-open -> reopen circuit
                stats.state = CircuitState.OPEN
                stats.state_changed_at = time.monotonic()
                logger.warning(
                    "circuit_breaker provider=%s state=open (half-open failure) error=%s",
                    provider,
                    error,
                )
            elif stats.state == CircuitState.CLOSED:
                if stats.failures >= self._failure_threshold:
                    stats.state = CircuitState.OPEN
                    stats.state_changed_at = time.monotonic()
                    logger.warning(
                        "circuit_breaker provider=%s state=open (threshold=%d reached) error=%s",
                        provider,
                        self._failure_threshold,
                        error,
                    )

    async def get_available_provider(self, providers: list[str]) -> Optional[str]:
        """
        Get first available provider from ordered list.

        Args:
            providers: Ordered list of provider names (preference order)

        Returns:
            First available provider name, or None if all unavailable
        """
        for provider in providers:
            if await self.is_available(provider):
                return provider
        return None

    async def get_provider_stats(self, provider: str) -> Optional[ProviderStats]:
        """Get stats for a specific provider."""
        async with self._lock:
            return self._providers.get(provider)

    def get_all_stats(self) -> dict[str, dict]:
        """Get stats for all tracked providers."""
        return {
            name: {
                "state": stats.state.value,
                "failures": stats.failures,
                "total_requests": stats.total_requests,
                "total_failures": stats.total_failures,
                "last_failure_time": stats.last_failure_time,
            }
            for name, stats in self._providers.items()
        }

    async def reset_provider(self, provider: str) -> None:
        """Reset stats for a specific provider."""
        async with self._lock:
            if provider in self._providers:
                del self._providers[provider]
                logger.info("circuit_breaker provider=%s reset", provider)

    async def reset_all(self) -> None:
        """Reset all provider stats."""
        async with self._lock:
            self._providers.clear()
            logger.info("circuit_breaker all providers reset")

    @classmethod
    def reset(cls) -> None:
        """Reset singleton instance (for testing)."""
        cls._instance = None


def get_circuit_breaker() -> CircuitBreaker:
    """Get or create global circuit breaker singleton."""
    return CircuitBreaker()
