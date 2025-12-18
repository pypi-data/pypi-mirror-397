"""
Tests for Team orchestration (RoundRobinGroupChat, SelectorGroupChat).

Tests cover:
- Team initialization
- Agent coordination structure
- Termination condition usage
- Team patterns

Note: Deep testing of team logic is handled by AutoGen's test suite.
These tests verify correct usage and integration.
"""

import unittest
from unittest.mock import AsyncMock, MagicMock

import pytest

from saptiva_agents.agents import AssistantAgent
from saptiva_agents.teams import RoundRobinGroupChat, SelectorGroupChat
from saptiva_agents.conditions import MaxMessageTermination, TextMessageTermination


class TestRoundRobinGroupChat(unittest.IsolatedAsyncioTestCase):
    """Test RoundRobinGroupChat team orchestration."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_model_client = MagicMock()
        self.mock_model_client.create = AsyncMock()

    async def test_team_initialization(self):
        """Test that team can be initialized with agents."""
        agent1 = AssistantAgent(
            name="agent1",
            model_client=self.mock_model_client
        )
        agent2 = AssistantAgent(
            name="agent2",
            model_client=self.mock_model_client
        )

        team = RoundRobinGroupChat(
            participants=[agent1, agent2],
            termination_condition=MaxMessageTermination(max_messages=10)
        )

        self.assertEqual(len(team._participants), 2)
        self.assertIsNotNone(team._termination_condition)

    async def test_team_initialization_without_termination(self):
        """Test team can be created without termination condition."""
        agent = AssistantAgent(
            name="agent",
            model_client=self.mock_model_client
        )

        # termination_condition is optional in AutoGen
        team = RoundRobinGroupChat(
            participants=[agent],
            termination_condition=None
        )

        self.assertEqual(len(team._participants), 1)

    async def test_team_with_max_turns(self):
        """Test team with max_turns parameter."""
        agent = AssistantAgent(
            name="agent",
            model_client=self.mock_model_client
        )

        team = RoundRobinGroupChat(
            participants=[agent],
            max_turns=5
        )

        self.assertEqual(len(team._participants), 1)

    async def test_team_with_multiple_agents(self):
        """Test team with multiple agents."""
        agents = [
            AssistantAgent(name=f"agent{i}", model_client=self.mock_model_client)
            for i in range(5)
        ]

        team = RoundRobinGroupChat(
            participants=agents,
            termination_condition=MaxMessageTermination(max_messages=20)
        )

        self.assertEqual(len(team._participants), 5)


class TestSelectorGroupChat(unittest.IsolatedAsyncioTestCase):
    """Test SelectorGroupChat team orchestration."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_model_client = MagicMock()
        self.mock_model_client.create = AsyncMock()

    async def test_selector_team_initialization(self):
        """Test SelectorGroupChat initialization with model_client."""
        agent1 = AssistantAgent(name="agent1", model_client=self.mock_model_client)
        agent2 = AssistantAgent(name="agent2", model_client=self.mock_model_client)

        # SelectorGroupChat requires at least 2 participants and model_client
        team = SelectorGroupChat(
            participants=[agent1, agent2],
            model_client=self.mock_model_client,
            termination_condition=MaxMessageTermination(max_messages=10)
        )

        self.assertEqual(len(team._participants), 2)
        self.assertIsNotNone(team._model_client)

    async def test_selector_with_max_turns(self):
        """Test SelectorGroupChat with max_turns."""
        agent1 = AssistantAgent(name="agent1", model_client=self.mock_model_client)
        agent2 = AssistantAgent(name="agent2", model_client=self.mock_model_client)

        team = SelectorGroupChat(
            participants=[agent1, agent2],
            model_client=self.mock_model_client,
            max_turns=5
        )

        self.assertEqual(len(team._participants), 2)


class TestTeamTermination(unittest.IsolatedAsyncioTestCase):
    """Test team termination conditions."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_model_client = MagicMock()
        self.mock_model_client.create = AsyncMock()

    async def test_team_with_max_message_termination(self):
        """Test team with MaxMessageTermination."""
        agent = AssistantAgent(name="agent", model_client=self.mock_model_client)

        termination = MaxMessageTermination(max_messages=3)
        team = RoundRobinGroupChat(
            participants=[agent],
            termination_condition=termination
        )

        self.assertEqual(team._termination_condition, termination)

    async def test_team_with_text_message_termination(self):
        """Test team with TextMessageTermination."""
        agent = AssistantAgent(name="agent", model_client=self.mock_model_client)

        termination = TextMessageTermination(source="assistant")
        team = RoundRobinGroupChat(
            participants=[agent],
            termination_condition=termination
        )

        self.assertEqual(team._termination_condition, termination)


class TestTeamPatterns(unittest.IsolatedAsyncioTestCase):
    """Test common team patterns."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_model_client = MagicMock()
        self.mock_model_client.create = AsyncMock()

    async def test_supervisor_worker_pattern(self):
        """Test supervisor-worker pattern structure."""
        # Supervisor
        supervisor = AssistantAgent(
            name="supervisor",
            model_client=self.mock_model_client,
            system_message="You coordinate workers."
        )

        # Workers
        worker1 = AssistantAgent(
            name="worker1",
            model_client=self.mock_model_client,
            system_message="You do task 1."
        )

        worker2 = AssistantAgent(
            name="worker2",
            model_client=self.mock_model_client,
            system_message="You do task 2."
        )

        # Supervisor can delegate to workers via SelectorGroupChat
        team = SelectorGroupChat(
            participants=[supervisor, worker1, worker2],
            model_client=self.mock_model_client,
            termination_condition=MaxMessageTermination(max_messages=10)
        )

        self.assertEqual(len(team._participants), 3)

    async def test_sequential_pipeline_pattern(self):
        """Test sequential processing pipeline."""
        validator = AssistantAgent(
            name="validator",
            model_client=self.mock_model_client,
            system_message="Validate input."
        )

        processor = AssistantAgent(
            name="processor",
            model_client=self.mock_model_client,
            system_message="Process data."
        )

        formatter = AssistantAgent(
            name="formatter",
            model_client=self.mock_model_client,
            system_message="Format output."
        )

        # Sequential processing via RoundRobinGroupChat
        team = RoundRobinGroupChat(
            participants=[validator, processor, formatter],
            termination_condition=MaxMessageTermination(max_messages=3)
        )

        self.assertEqual(len(team._participants), 3)

    async def test_consensus_pattern(self):
        """Test consensus building pattern."""
        evaluators = [
            AssistantAgent(
                name=f"evaluator_{i}",
                model_client=self.mock_model_client,
                system_message=f"You are evaluator {i}."
            )
            for i in range(3)
        ]

        team = RoundRobinGroupChat(
            participants=evaluators,
            termination_condition=MaxMessageTermination(max_messages=3)
        )

        # All evaluators should participate
        self.assertEqual(len(team._participants), 3)


class TestTeamConfiguration(unittest.TestCase):
    """Test team configuration options."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_model_client = MagicMock()

    def test_team_with_name(self):
        """Test team with custom name."""
        agent = AssistantAgent(name="agent", model_client=self.mock_model_client)

        team = RoundRobinGroupChat(
            participants=[agent],
            name="my_team"
        )

        self.assertEqual(team.name, "my_team")

    def test_team_with_description(self):
        """Test team with description."""
        agent = AssistantAgent(name="agent", model_client=self.mock_model_client)

        team = RoundRobinGroupChat(
            participants=[agent],
            description="A test team"
        )

        self.assertEqual(team.description, "A test team")


@pytest.mark.integration
class TestTeamIntegration(unittest.IsolatedAsyncioTestCase):
    """Integration tests for team workflows."""

    @pytest.mark.integration
    @unittest.skipUnless(
        False,  # Set to True to run integration tests
        "Integration tests require API key"
    )
    async def test_round_robin_simple_task(self):
        """Integration test: round robin team processes task."""
        import os
        from saptiva_agents.base import SaptivaAIChatCompletionClient
        from saptiva_agents import SAPTIVA_OPS

        api_key = os.getenv("SAPTIVA_API_KEY")
        client = SaptivaAIChatCompletionClient(
            model=SAPTIVA_OPS,
            api_key=api_key
        )

        agent1 = AssistantAgent(
            name="agent1",
            model_client=client,
            system_message="You are agent 1."
        )

        agent2 = AssistantAgent(
            name="agent2",
            model_client=client,
            system_message="You are agent 2."
        )

        team = RoundRobinGroupChat(
            participants=[agent1, agent2],
            termination_condition=MaxMessageTermination(max_messages=4)
        )

        result = await team.run(task="Simple task")
        self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()
