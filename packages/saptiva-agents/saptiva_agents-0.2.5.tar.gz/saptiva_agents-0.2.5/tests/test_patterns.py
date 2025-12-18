"""
Integration tests for Agent Patterns.

Tests the 4 main agent patterns documented in README:
1. Research Agent with Tools
2. Supervisor-Worker Pattern
3. Sequential Processing Pipeline
4. Consensus Building

These are integration tests that require API keys and should be
run selectively.
"""

import os
import unittest
from unittest.mock import AsyncMock, MagicMock

import pytest

from saptiva_agents import SAPTIVA_OPS, SAPTIVA_TURBO
from saptiva_agents.agents import AssistantAgent
from saptiva_agents.base import SaptivaAIChatCompletionClient
from saptiva_agents.conditions import MaxMessageTermination
from saptiva_agents.teams import RoundRobinGroupChat, SelectorGroupChat
from saptiva_agents.tools import wikipedia_search


@pytest.mark.integration
class TestResearchAgentPattern(unittest.IsolatedAsyncioTestCase):
    """Test Pattern 1: Research Agent with Tools."""

    @classmethod
    def setUpClass(cls):
        """Set up API client for all tests."""
        cls.api_key = os.getenv("SAPTIVA_API_KEY")
        cls.skip_tests = not cls.api_key

    @unittest.skipIf(
        skip_tests := not os.getenv("SAPTIVA_API_KEY"),
        "Requires SAPTIVA_API_KEY environment variable"
    )
    async def test_research_agent_with_wikipedia(self):
        """Test research agent using Wikipedia tool."""
        model_client = SaptivaAIChatCompletionClient(
            model=SAPTIVA_TURBO,  # Tool calling model
            api_key=self.api_key
        )

        async def search_mock(query: str) -> str:
            """Mock search for testing."""
            return f"Research results for: {query}"

        agent = AssistantAgent(
            name="researcher",
            model_client=model_client,
            tools=[search_mock],
            system_message="You research topics using available tools."
        )

        result = await agent.run(task="Research Python programming")
        self.assertIsNotNone(result)
        self.assertTrue(len(result.messages) > 0)

    @unittest.skipIf(
        skip_tests := not os.getenv("SAPTIVA_API_KEY"),
        "Requires SAPTIVA_API_KEY environment variable"
    )
    async def test_research_agent_with_multiple_tools(self):
        """Test research agent with multiple tools."""
        model_client = SaptivaAIChatCompletionClient(
            model=SAPTIVA_TURBO,
            api_key=self.api_key
        )

        async def search_papers(query: str, max_results: int = 5) -> str:
            """Mock academic paper search."""
            return f"Found {max_results} papers about: {query}"

        async def get_weather(location: str) -> str:
            """Mock weather lookup."""
            return f"Weather in {location}: Sunny, 25°C"

        agent = AssistantAgent(
            name="research_assistant",
            model_client=model_client,
            tools=[search_papers, get_weather],
            system_message="""You research topics using:
            1. search_papers for academic information
            2. get_weather for weather data
            """
        )

        result = await agent.run(task="Research climate change and check weather in Paris")
        self.assertIsNotNone(result)


@pytest.mark.integration
class TestSupervisorWorkerPattern(unittest.IsolatedAsyncioTestCase):
    """Test Pattern 2: Supervisor-Worker Pattern."""

    @classmethod
    def setUpClass(cls):
        """Set up API client for all tests."""
        cls.api_key = os.getenv("SAPTIVA_API_KEY")

    @unittest.skipIf(
        skip_tests := not os.getenv("SAPTIVA_API_KEY"),
        "Requires SAPTIVA_API_KEY environment variable"
    )
    async def test_supervisor_worker_coordination(self):
        """Test supervisor coordinating workers."""
        model_client = SaptivaAIChatCompletionClient(
            model=SAPTIVA_TURBO,
            api_key=self.api_key
        )

        # Specialist workers
        data_analyst = AssistantAgent(
            name="data_analyst",
            model_client=model_client,
            system_message="You analyze data and provide insights."
        )

        report_writer = AssistantAgent(
            name="writer",
            model_client=model_client,
            system_message="You write clear, professional reports."
        )

        # Supervisor coordinates via SelectorGroupChat
        team = SelectorGroupChat(
            participants=[data_analyst, report_writer],
            model_client=model_client,
            termination_condition=MaxMessageTermination(max_messages=8)
        )

        result = await team.run(task="Analyze sales data and create a report")
        self.assertIsNotNone(result)


@pytest.mark.integration
class TestSequentialPipelinePattern(unittest.IsolatedAsyncioTestCase):
    """Test Pattern 3: Sequential Processing Pipeline."""

    @classmethod
    def setUpClass(cls):
        """Set up API client for all tests."""
        cls.api_key = os.getenv("SAPTIVA_API_KEY")

    @unittest.skipIf(
        skip_tests := not os.getenv("SAPTIVA_API_KEY"),
        "Requires SAPTIVA_API_KEY environment variable"
    )
    async def test_sequential_pipeline(self):
        """Test sequential processing pipeline."""
        model_client = SaptivaAIChatCompletionClient(
            model=SAPTIVA_OPS,
            api_key=self.api_key
        )

        agents = [
            AssistantAgent(
                name="validator",
                model_client=model_client,
                system_message="Validate and clean input data. Output structured format."
            ),
            AssistantAgent(
                name="analyzer",
                model_client=model_client,
                system_message="Analyze cleaned data. Provide insights."
            ),
            AssistantAgent(
                name="formatter",
                model_client=model_client,
                system_message="Format insights into final report. Say DONE when complete."
            )
        ]

        # Process sequentially: limit to one turn per agent.
        team = RoundRobinGroupChat(
            participants=agents,
            max_turns=3
        )

        result = await team.run(
            task="Process this data: [1, 2, 3, 4, 5]",
            output_task_messages=False,
        )
        self.assertIsNotNone(result)

        # TaskResult.messages may include extra agent events; verify all stages spoke.
        sources = {getattr(m, "source", None) for m in result.messages}
        self.assertTrue({"validator", "analyzer", "formatter"}.issubset(sources))

    @unittest.skipIf(
        skip_tests := not os.getenv("SAPTIVA_API_KEY"),
        "Requires SAPTIVA_API_KEY environment variable"
    )
    async def test_pipeline_function_approach(self):
        """Test pipeline using function composition."""
        model_client = SaptivaAIChatCompletionClient(
            model=SAPTIVA_OPS,
            api_key=self.api_key
        )

        agents = [
            AssistantAgent(
                name="step1",
                model_client=model_client,
                system_message="Step 1: Extract numbers"
            ),
            AssistantAgent(
                name="step2",
                model_client=model_client,
                system_message="Step 2: Double each number"
            ),
        ]

        async def process_pipeline(data: str) -> str:
            """Process data through pipeline."""
            result = data
            for agent in agents:
                response = await agent.run(task=result)
                result = response.messages[-1].content

            return result

        result = await process_pipeline("numbers: 1, 2, 3")
        self.assertIsNotNone(result)


@pytest.mark.integration
class TestConsensusBuildingPattern(unittest.IsolatedAsyncioTestCase):
    """Test Pattern 4: Consensus Building."""

    @classmethod
    def setUpClass(cls):
        """Set up API client for all tests."""
        cls.api_key = os.getenv("SAPTIVA_API_KEY")

    @unittest.skipIf(
        skip_tests := not os.getenv("SAPTIVA_API_KEY"),
        "Requires SAPTIVA_API_KEY environment variable"
    )
    async def test_consensus_voting(self):
        """Test consensus building with multiple evaluators."""
        model_client = SaptivaAIChatCompletionClient(
            model=SAPTIVA_OPS,
            api_key=self.api_key
        )

        evaluators = [
            AssistantAgent(
                name=f"evaluator_{i}",
                model_client=model_client,
                system_message=f"You are evaluator {i}. Analyze and vote YES or NO."
            )
            for i in range(3)
        ]

        async def get_consensus(question: str) -> dict:
            """Get consensus from evaluators."""
            votes = []
            for evaluator in evaluators:
                response = await evaluator.run(task=question)
                vote = response.messages[-1].content
                votes.append(vote)

            # Simple majority
            yes_votes = sum(1 for v in votes if 'YES' in str(v).upper())
            consensus = "YES" if yes_votes > len(votes) / 2 else "NO"

            return {
                "votes": votes,
                "consensus": consensus,
                "vote_count": {"YES": yes_votes, "NO": len(votes) - yes_votes}
            }

        result = await get_consensus("Should we implement feature X?")
        self.assertIn("consensus", result)
        self.assertIn("votes", result)
        self.assertEqual(len(result["votes"]), 3)

    @unittest.skipIf(
        skip_tests := not os.getenv("SAPTIVA_API_KEY"),
        "Requires SAPTIVA_API_KEY environment variable"
    )
    async def test_consensus_with_team(self):
        """Test consensus using team orchestration."""
        model_client = SaptivaAIChatCompletionClient(
            model=SAPTIVA_OPS,
            api_key=self.api_key
        )

        evaluators = [
            AssistantAgent(
                name=f"evaluator_{i}",
                model_client=model_client,
                system_message=f"You are evaluator {i}. Provide your assessment."
            )
            for i in range(3)
        ]

        team = RoundRobinGroupChat(
            participants=evaluators,
            max_turns=3,
        )

        result = await team.run(
            task="Evaluate: Is Python good for web development?",
            output_task_messages=False,
        )
        self.assertIsNotNone(result)
        sources = {getattr(m, "source", None) for m in result.messages}
        expected_sources = {f"evaluator_{i}" for i in range(3)}
        self.assertTrue(expected_sources.issubset(sources))


class TestPatternsMocked(unittest.IsolatedAsyncioTestCase):
    """Test patterns with mocked dependencies (no API key needed)."""

    def setUp(self):
        """Set up mocked model client."""
        self.mock_model_client = MagicMock()
        self.mock_model_client.create = AsyncMock(
            return_value=MagicMock(content="Mocked response")
        )

    async def test_research_pattern_structure(self):
        """Test research pattern structure without API calls."""
        async def mock_tool(query: str) -> str:
            return f"Result for {query}"

        agent = AssistantAgent(
            name="researcher",
            model_client=self.mock_model_client,
            tools=[mock_tool],
            system_message="Research assistant"
        )

        self.assertEqual(len(agent._tools), 1)
        self.assertEqual(agent.name, "researcher")

    async def test_supervisor_pattern_structure(self):
        """Test supervisor pattern structure without API calls."""
        supervisor = AssistantAgent(
            name="supervisor",
            model_client=self.mock_model_client
        )

        workers = [
            AssistantAgent(name=f"worker_{i}", model_client=self.mock_model_client)
            for i in range(2)
        ]

        team = RoundRobinGroupChat(
            participants=[supervisor] + workers,
            termination_condition=MaxMessageTermination(max_messages=5)
        )

        self.assertEqual(len(team._participants), 3)

    async def test_pipeline_pattern_structure(self):
        """Test pipeline pattern structure without API calls."""
        stages = [
            AssistantAgent(name="stage1", model_client=self.mock_model_client),
            AssistantAgent(name="stage2", model_client=self.mock_model_client),
            AssistantAgent(name="stage3", model_client=self.mock_model_client),
        ]

        team = RoundRobinGroupChat(
            participants=stages,
            termination_condition=MaxMessageTermination(max_messages=3)
        )

        self.assertEqual(len(team._participants), 3)

    async def test_consensus_pattern_structure(self):
        """Test consensus pattern structure without API calls."""
        evaluators = [
            AssistantAgent(name=f"eval_{i}", model_client=self.mock_model_client)
            for i in range(5)
        ]

        self.assertEqual(len(evaluators), 5)


if __name__ == "__main__":
    unittest.main()
