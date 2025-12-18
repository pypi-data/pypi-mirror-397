"""Tests for circuit breaker implementation."""

from __future__ import annotations

import asyncio
import unittest

from saptiva_agents.core._circuit_breaker import (
    CircuitBreaker,
    CircuitState,
    get_circuit_breaker,
)


class TestCircuitBreakerStates(unittest.IsolatedAsyncioTestCase):
    """Test circuit breaker state transitions."""

    def setUp(self):
        CircuitBreaker.reset()

    def tearDown(self):
        CircuitBreaker.reset()

    async def test_initial_state_closed(self):
        """All providers should start in CLOSED state."""
        cb = get_circuit_breaker()
        self.assertTrue(await cb.is_available("provider_a"))

    async def test_opens_after_failure_threshold(self):
        """Circuit should open after reaching failure threshold."""
        cb = get_circuit_breaker()
        cb.configure(failure_threshold=3, recovery_timeout_s=1.0)

        # Record failures
        for i in range(3):
            await cb.record_failure("provider_a", f"Error {i}")

        # Should be open now
        self.assertFalse(await cb.is_available("provider_a"))

    async def test_success_resets_failures(self):
        """Success should reset failure count."""
        cb = get_circuit_breaker()
        cb.configure(failure_threshold=3)

        await cb.record_failure("provider_a")
        await cb.record_failure("provider_a")
        await cb.record_success("provider_a")

        # Failure count should be reset, need 3 more failures to open
        await cb.record_failure("provider_a")
        await cb.record_failure("provider_a")
        self.assertTrue(await cb.is_available("provider_a"))

    async def test_half_open_after_timeout(self):
        """Circuit should transition to HALF_OPEN after recovery timeout."""
        CircuitBreaker.reset()  # Ensure clean state
        cb = get_circuit_breaker()
        cb.configure(failure_threshold=2, recovery_timeout_s=0.1)

        # Open the circuit
        await cb.record_failure("provider_timeout")
        await cb.record_failure("provider_timeout")
        self.assertFalse(await cb.is_available("provider_timeout"))

        # Wait for recovery timeout (with margin)
        await asyncio.sleep(0.2)

        # Should be in HALF_OPEN now (allows one request)
        self.assertTrue(await cb.is_available("provider_timeout"))

    async def test_half_open_success_closes(self):
        """Success in HALF_OPEN state should close the circuit."""
        CircuitBreaker.reset()  # Ensure clean state
        cb = get_circuit_breaker()
        cb.configure(failure_threshold=2, recovery_timeout_s=0.1, success_threshold=1)

        # Open the circuit
        await cb.record_failure("provider_success")
        await cb.record_failure("provider_success")

        # Wait for recovery timeout (with margin)
        await asyncio.sleep(0.2)

        # Trigger half-open by checking availability
        await cb.is_available("provider_success")

        # Record success in HALF_OPEN
        await cb.record_success("provider_success")

        # Should be CLOSED now
        self.assertTrue(await cb.is_available("provider_success"))

    async def test_half_open_failure_reopens(self):
        """Failure in HALF_OPEN state should reopen the circuit."""
        cb = get_circuit_breaker()
        cb.configure(failure_threshold=2, recovery_timeout_s=0.05)

        # Open the circuit
        await cb.record_failure("provider_a")
        await cb.record_failure("provider_a")

        # Wait for recovery timeout
        await asyncio.sleep(0.1)

        # Trigger half-open by checking availability
        await cb.is_available("provider_a")

        # Record failure in HALF_OPEN
        await cb.record_failure("provider_a")

        # Should be OPEN again
        self.assertFalse(await cb.is_available("provider_a"))


class TestCircuitBreakerFallback(unittest.IsolatedAsyncioTestCase):
    """Test circuit breaker fallback behavior."""

    def setUp(self):
        CircuitBreaker.reset()

    def tearDown(self):
        CircuitBreaker.reset()

    async def test_get_available_provider_all_healthy(self):
        """Should return first provider when all are healthy."""
        cb = get_circuit_breaker()
        providers = ["searxng", "tavily", "duckduckgo"]

        result = await cb.get_available_provider(providers)
        self.assertEqual(result, "searxng")

    async def test_get_available_provider_fallback(self):
        """Should fallback to next healthy provider."""
        cb = get_circuit_breaker()
        cb.configure(failure_threshold=2)
        providers = ["searxng", "tavily", "duckduckgo"]

        # Open circuit for first provider
        await cb.record_failure("searxng")
        await cb.record_failure("searxng")

        result = await cb.get_available_provider(providers)
        self.assertEqual(result, "tavily")

    async def test_get_available_provider_multiple_fallbacks(self):
        """Should skip multiple unhealthy providers."""
        cb = get_circuit_breaker()
        cb.configure(failure_threshold=2)
        providers = ["searxng", "tavily", "duckduckgo"]

        # Open circuit for first two providers
        await cb.record_failure("searxng")
        await cb.record_failure("searxng")
        await cb.record_failure("tavily")
        await cb.record_failure("tavily")

        result = await cb.get_available_provider(providers)
        self.assertEqual(result, "duckduckgo")

    async def test_get_available_provider_all_down(self):
        """Should return None when all providers are down."""
        cb = get_circuit_breaker()
        cb.configure(failure_threshold=2)
        providers = ["searxng", "tavily"]

        # Open circuit for all providers
        await cb.record_failure("searxng")
        await cb.record_failure("searxng")
        await cb.record_failure("tavily")
        await cb.record_failure("tavily")

        result = await cb.get_available_provider(providers)
        self.assertIsNone(result)


class TestCircuitBreakerSingleton(unittest.IsolatedAsyncioTestCase):
    """Test circuit breaker singleton behavior."""

    def setUp(self):
        CircuitBreaker.reset()

    def tearDown(self):
        CircuitBreaker.reset()

    async def test_singleton_behavior(self):
        """get_circuit_breaker should return same instance."""
        cb1 = get_circuit_breaker()
        cb2 = get_circuit_breaker()
        self.assertIs(cb1, cb2)

    async def test_singleton_state_persists(self):
        """State should persist across get_circuit_breaker calls."""
        cb1 = get_circuit_breaker()
        cb1.configure(failure_threshold=2)
        await cb1.record_failure("provider_a")
        await cb1.record_failure("provider_a")

        # Get again - should have same state
        cb2 = get_circuit_breaker()
        self.assertFalse(await cb2.is_available("provider_a"))

    async def test_reset_clears_singleton(self):
        """CircuitBreaker.reset() should clear singleton."""
        cb1 = get_circuit_breaker()
        cb1.configure(failure_threshold=2)
        await cb1.record_failure("provider_a")
        await cb1.record_failure("provider_a")

        CircuitBreaker.reset()

        cb2 = get_circuit_breaker()
        # Should be a new instance with fresh state
        self.assertTrue(await cb2.is_available("provider_a"))


class TestCircuitBreakerConcurrency(unittest.IsolatedAsyncioTestCase):
    """Test circuit breaker under concurrent access."""

    def setUp(self):
        CircuitBreaker.reset()

    def tearDown(self):
        CircuitBreaker.reset()

    async def test_concurrent_failures(self):
        """Circuit should handle concurrent failures correctly."""
        cb = get_circuit_breaker()
        cb.configure(failure_threshold=10)

        # Simulate 10 concurrent failures
        tasks = [cb.record_failure("provider_a") for _ in range(10)]
        await asyncio.gather(*tasks)

        # Circuit should be open
        self.assertFalse(await cb.is_available("provider_a"))

    async def test_concurrent_mixed_operations(self):
        """Circuit should handle mixed operations correctly."""
        cb = get_circuit_breaker()
        cb.configure(failure_threshold=5)

        async def mixed_ops():
            await cb.record_failure("provider_a")
            await cb.record_success("provider_b")
            await cb.is_available("provider_a")
            await cb.is_available("provider_b")

        tasks = [mixed_ops() for _ in range(5)]
        await asyncio.gather(*tasks)

        # provider_b should still be available (only successes)
        self.assertTrue(await cb.is_available("provider_b"))


class TestCircuitBreakerStats(unittest.IsolatedAsyncioTestCase):
    """Test circuit breaker statistics tracking."""

    def setUp(self):
        CircuitBreaker.reset()

    def tearDown(self):
        CircuitBreaker.reset()

    async def test_get_all_stats(self):
        """Should track stats for all providers."""
        cb = get_circuit_breaker()

        await cb.record_success("provider_a")
        await cb.record_failure("provider_b")

        stats = cb.get_all_stats()

        self.assertIn("provider_a", stats)
        self.assertIn("provider_b", stats)
        self.assertEqual(stats["provider_a"]["total_requests"], 1)
        self.assertEqual(stats["provider_b"]["total_failures"], 1)

    async def test_reset_provider(self):
        """Should reset stats for specific provider."""
        cb = get_circuit_breaker()
        cb.configure(failure_threshold=2)

        await cb.record_failure("provider_a")
        await cb.record_failure("provider_a")
        self.assertFalse(await cb.is_available("provider_a"))

        await cb.reset_provider("provider_a")

        self.assertTrue(await cb.is_available("provider_a"))

    async def test_reset_all(self):
        """Should reset stats for all providers."""
        cb = get_circuit_breaker()
        cb.configure(failure_threshold=2)

        await cb.record_failure("provider_a")
        await cb.record_failure("provider_a")
        await cb.record_failure("provider_b")
        await cb.record_failure("provider_b")

        await cb.reset_all()

        self.assertTrue(await cb.is_available("provider_a"))
        self.assertTrue(await cb.is_available("provider_b"))


if __name__ == "__main__":
    unittest.main()
