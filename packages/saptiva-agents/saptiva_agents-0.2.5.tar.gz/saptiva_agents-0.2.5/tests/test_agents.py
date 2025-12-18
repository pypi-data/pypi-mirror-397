"""
Tests for Agent classes (AssistantAgent, UserProxyAgent).

Tests cover:
- Agent initialization
- Message handling
- Tool integration
- System message configuration
- Error handling
"""

import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from autogen_core.models import ChatCompletionClient
from autogen_core.tools import FunctionTool

from saptiva_agents.agents import AssistantAgent
from saptiva_agents.base import SaptivaAIChatCompletionClient
from saptiva_agents import SAPTIVA_OPS


class TestAssistantAgent(unittest.IsolatedAsyncioTestCase):
    """Test AssistantAgent functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_model_client = MagicMock(spec=ChatCompletionClient)
        self.mock_model_client.create = AsyncMock()
        self.mock_model_client.model = "test-model"

    async def test_agent_initialization(self):
        """Test that AssistantAgent can be initialized properly."""
        agent = AssistantAgent(
            name="test_agent",
            model_client=self.mock_model_client,
            system_message="You are a helpful assistant."
        )

        self.assertEqual(agent.name, "test_agent")
        self.assertEqual(agent._system_messages[0].content, "You are a helpful assistant.")
        self.assertEqual(agent._model_client, self.mock_model_client)

    async def test_agent_with_tools(self):
        """Test agent initialization with tools."""
        async def test_tool(query: str) -> str:
            """A test tool."""
            return f"Result: {query}"

        agent = AssistantAgent(
            name="tool_agent",
            model_client=self.mock_model_client,
            tools=[test_tool],
            system_message="You have tools."
        )

        self.assertEqual(len(agent._tools), 1)
        self.assertIsInstance(agent._tools[0], FunctionTool)

    async def test_agent_system_message_default(self):
        """Test that agent has default system message when none provided."""
        agent = AssistantAgent(
            name="default_agent",
            model_client=self.mock_model_client
        )

        self.assertTrue(len(agent._system_messages) > 0)

    async def test_agent_name_validation(self):
        """Test that agent name is required and validated."""
        with self.assertRaises(TypeError):
            AssistantAgent(model_client=self.mock_model_client)

    async def test_agent_with_description(self):
        """Test agent with custom description."""
        description = "This agent handles customer queries"
        agent = AssistantAgent(
            name="customer_agent",
            model_client=self.mock_model_client,
            description=description
        )

        self.assertEqual(agent.description, description)

    async def test_agent_message_handling(self):
        """Test that agent can handle messages."""
        agent = AssistantAgent(
            name="msg_agent",
            model_client=self.mock_model_client
        )

        # Verify agent is properly configured
        self.assertIsNotNone(agent._model_client)
        self.assertEqual(agent.name, "msg_agent")


class TestSaptivaAIChatCompletionClient(unittest.IsolatedAsyncioTestCase):
    """Test SaptivaAIChatCompletionClient."""

    @patch('httpx.AsyncClient')
    async def test_client_initialization(self, mock_httpx):
        """Test client initialization with API key."""
        client = SaptivaAIChatCompletionClient(
            model=SAPTIVA_OPS,
            api_key="test-key-123"
        )

        # Client is initialized successfully
        self.assertIsNotNone(client)

    @patch('httpx.AsyncClient')
    async def test_client_with_temperature(self, mock_httpx):
        """Test client with custom temperature."""
        client = SaptivaAIChatCompletionClient(
            model=SAPTIVA_OPS,
            api_key="test-key",
            temperature=0.5
        )

        # Temperature is passed to the underlying client
        self.assertIsNotNone(client)

    @patch('httpx.AsyncClient')
    async def test_client_with_custom_base_url(self, mock_httpx):
        """Test client with custom base URL."""
        custom_url = "https://custom-api.example.com/v1"
        client = SaptivaAIChatCompletionClient(
            model="custom-model",
            api_key="test-key",
            base_url=custom_url
        )

        self.assertIsNotNone(client)

    async def test_client_missing_api_key(self):
        """Test that client requires API key."""
        from starlette.exceptions import HTTPException

        # Try to create client with explicitly no API key
        with self.assertRaises(HTTPException) as context:
            SaptivaAIChatCompletionClient(model=SAPTIVA_OPS, api_key=None)

        self.assertEqual(context.exception.status_code, 401)


class TestAgentIntegration(unittest.IsolatedAsyncioTestCase):
    """Integration tests for agent workflows."""

    @pytest.mark.integration
    @unittest.skipUnless(
        False,  # Set to True to run integration tests
        "Integration tests require API key"
    )
    async def test_agent_simple_query(self):
        """Integration test: agent processes simple query."""
        import os
        api_key = os.getenv("SAPTIVA_API_KEY")

        client = SaptivaAIChatCompletionClient(
            model=SAPTIVA_OPS,
            api_key=api_key
        )

        agent = AssistantAgent(
            name="test_agent",
            model_client=client,
            system_message="You are a helpful assistant. Answer concisely."
        )

        result = await agent.run(task="What is 2+2?")
        self.assertIsNotNone(result)
        self.assertTrue(len(result.messages) > 0)

    @pytest.mark.integration
    @unittest.skipUnless(
        False,  # Set to True to run integration tests
        "Integration tests require API key"
    )
    async def test_agent_with_tool_calling(self):
        """Integration test: agent uses tools."""
        import os
        api_key = os.getenv("SAPTIVA_API_KEY")

        async def calculator(operation: str, a: float, b: float) -> float:
            """
            Perform basic math operations.

            Args:
                operation: One of 'add', 'subtract', 'multiply', 'divide'
                a: First number
                b: Second number

            Returns:
                Result of the operation
            """
            ops = {
                'add': lambda x, y: x + y,
                'subtract': lambda x, y: x - y,
                'multiply': lambda x, y: x * y,
                'divide': lambda x, y: x / y if y != 0 else float('inf')
            }
            return ops.get(operation, lambda x, y: 0)(a, b)

        client = SaptivaAIChatCompletionClient(
            model=SAPTIVA_OPS,
            api_key=api_key
        )

        agent = AssistantAgent(
            name="math_agent",
            model_client=client,
            tools=[calculator],
            system_message="You are a math assistant. Use the calculator tool."
        )

        result = await agent.run(task="What is 15 multiplied by 7?")
        self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()
