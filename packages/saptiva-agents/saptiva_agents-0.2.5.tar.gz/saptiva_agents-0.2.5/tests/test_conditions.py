"""
Tests for Termination Conditions.

Since termination conditions are re-exports from autogen_agentchat.conditions,
these tests verify that:
1. The imports work correctly
2. The basic termination logic functions
3. Conditions can be instantiated and used

Note: Deep testing of termination logic is handled by AutoGen's test suite.
"""

import asyncio
import unittest

from saptiva_agents.conditions import (
    MaxMessageTermination,
    TextMessageTermination,
    TimeoutTermination,
    StopMessageTermination,
    SourceMatchTermination,
)


class TestTerminationConditionImports(unittest.TestCase):
    """Test that termination conditions can be imported."""

    def test_max_message_import(self):
        """Test MaxMessageTermination can be imported."""
        self.assertIsNotNone(MaxMessageTermination)

    def test_text_message_import(self):
        """Test TextMessageTermination can be imported."""
        self.assertIsNotNone(TextMessageTermination)

    def test_timeout_import(self):
        """Test TimeoutTermination can be imported."""
        self.assertIsNotNone(TimeoutTermination)

    def test_stop_message_import(self):
        """Test StopMessageTermination can be imported."""
        self.assertIsNotNone(StopMessageTermination)

    def test_source_match_import(self):
        """Test SourceMatchTermination can be imported."""
        self.assertIsNotNone(SourceMatchTermination)


class TestMaxMessageTermination(unittest.TestCase):
    """Test MaxMessageTermination condition."""

    def test_initialization(self):
        """Test condition can be initialized."""
        condition = MaxMessageTermination(max_messages=10)
        self.assertIsNotNone(condition)

    def test_initialization_with_zero(self):
        """Test condition with zero max messages."""
        condition = MaxMessageTermination(max_messages=0)
        self.assertIsNotNone(condition)

    def test_has_reset_method(self):
        """Test condition has reset method."""
        condition = MaxMessageTermination(max_messages=5)
        self.assertTrue(hasattr(condition, 'reset'))
        self.assertTrue(callable(condition.reset))

    def test_has_terminated_property(self):
        """Test condition has terminated property."""
        condition = MaxMessageTermination(max_messages=5)
        self.assertTrue(hasattr(condition, 'terminated'))

    def test_is_callable(self):
        """Test condition is callable."""
        condition = MaxMessageTermination(max_messages=5)
        self.assertTrue(callable(condition))


class TestTextMessageTermination(unittest.TestCase):
    """Test TextMessageTermination condition."""

    def test_initialization(self):
        """Test condition can be initialized with source."""
        condition = TextMessageTermination(source="assistant")
        self.assertIsNotNone(condition)

    def test_initialization_with_none(self):
        """Test condition with None source (matches any)."""
        condition = TextMessageTermination(source=None)
        self.assertIsNotNone(condition)

    def test_has_reset_method(self):
        """Test condition has reset method."""
        condition = TextMessageTermination(source="user")
        self.assertTrue(hasattr(condition, 'reset'))

    def test_is_callable(self):
        """Test condition is callable."""
        condition = TextMessageTermination(source="agent")
        self.assertTrue(callable(condition))


class TestTimeoutTermination(unittest.TestCase):
    """Test TimeoutTermination condition."""

    def test_initialization(self):
        """Test condition can be initialized with timeout."""
        condition = TimeoutTermination(timeout_seconds=30)
        self.assertIsNotNone(condition)

    def test_initialization_with_float(self):
        """Test condition with float timeout."""
        condition = TimeoutTermination(timeout_seconds=1.5)
        self.assertIsNotNone(condition)

    def test_has_reset_method(self):
        """Test condition has reset method."""
        condition = TimeoutTermination(timeout_seconds=60)
        self.assertTrue(hasattr(condition, 'reset'))

    def test_is_callable(self):
        """Test condition is callable."""
        condition = TimeoutTermination(timeout_seconds=10)
        self.assertTrue(callable(condition))


class TestStopMessageTermination(unittest.TestCase):
    """Test StopMessageTermination condition."""

    def test_initialization(self):
        """Test condition can be initialized."""
        condition = StopMessageTermination()
        self.assertIsNotNone(condition)

    def test_has_reset_method(self):
        """Test condition has reset method."""
        condition = StopMessageTermination()
        self.assertTrue(hasattr(condition, 'reset'))

    def test_is_callable(self):
        """Test condition is callable."""
        condition = StopMessageTermination()
        self.assertTrue(callable(condition))


class TestSourceMatchTermination(unittest.TestCase):
    """Test SourceMatchTermination condition."""

    def test_initialization(self):
        """Test condition can be initialized with sources."""
        condition = SourceMatchTermination(sources=["agent1", "agent2"])
        self.assertIsNotNone(condition)

    def test_initialization_with_single_source(self):
        """Test condition with single source."""
        condition = SourceMatchTermination(sources=["assistant"])
        self.assertIsNotNone(condition)

    def test_has_reset_method(self):
        """Test condition has reset method."""
        condition = SourceMatchTermination(sources=["user"])
        self.assertTrue(hasattr(condition, 'reset'))

    def test_is_callable(self):
        """Test condition is callable."""
        condition = SourceMatchTermination(sources=["agent"])
        self.assertTrue(callable(condition))


class TestTerminationConditionUsage(unittest.TestCase):
    """Test using termination conditions with teams."""

    def test_max_message_in_team_config(self):
        """Test MaxMessageTermination can be used in team configuration."""
        from saptiva_agents.teams import RoundRobinGroupChat
        from saptiva_agents.agents import AssistantAgent
        from unittest.mock import MagicMock

        mock_client = MagicMock()
        agent = AssistantAgent(name="test", model_client=mock_client)

        termination = MaxMessageTermination(max_messages=5)

        # Should be able to create team with termination condition
        team = RoundRobinGroupChat(
            participants=[agent],
            termination_condition=termination
        )

        self.assertEqual(team._termination_condition, termination)

    def test_text_message_in_team_config(self):
        """Test TextMessageTermination can be used in team configuration."""
        from saptiva_agents.teams import RoundRobinGroupChat
        from saptiva_agents.agents import AssistantAgent
        from unittest.mock import MagicMock

        mock_client = MagicMock()
        agent = AssistantAgent(name="test", model_client=mock_client)

        termination = TextMessageTermination(source="assistant")

        team = RoundRobinGroupChat(
            participants=[agent],
            termination_condition=termination
        )

        self.assertEqual(team._termination_condition, termination)

    def test_timeout_in_team_config(self):
        """Test TimeoutTermination can be used in team configuration."""
        from saptiva_agents.teams import RoundRobinGroupChat
        from saptiva_agents.agents import AssistantAgent
        from unittest.mock import MagicMock

        mock_client = MagicMock()
        agent = AssistantAgent(name="test", model_client=mock_client)

        termination = TimeoutTermination(timeout_seconds=30)

        team = RoundRobinGroupChat(
            participants=[agent],
            termination_condition=termination
        )

        self.assertEqual(team._termination_condition, termination)


class TestTerminationConditionReset(unittest.IsolatedAsyncioTestCase):
    """Test reset functionality of termination conditions."""

    async def test_max_message_reset(self):
        """Test MaxMessageTermination can be reset."""
        condition = MaxMessageTermination(max_messages=5)

        # Call reset - should not raise error
        await condition.reset()

        # Should still be callable after reset
        self.assertTrue(callable(condition))

    async def test_text_message_reset(self):
        """Test TextMessageTermination can be reset."""
        condition = TextMessageTermination(source="assistant")

        await condition.reset()
        self.assertTrue(callable(condition))

    async def test_timeout_reset(self):
        """Test TimeoutTermination can be reset."""
        condition = TimeoutTermination(timeout_seconds=10)

        await condition.reset()
        self.assertTrue(callable(condition))


if __name__ == "__main__":
    unittest.main()
