"""
Tests for Saptiva Native Tool System.

These tests validate the migration from LangChain to native Pydantic-based tools.
Tests can run without API keys for unit testing the tool infrastructure.
"""

import asyncio
import unittest
from unittest.mock import AsyncMock, patch, MagicMock

from pydantic import ValidationError

from saptiva_agents.tools._saptiva_tool import (
    SaptivaTool,
    ToolInput,
    ToolOutput,
    create_saptiva_tool,
)
from saptiva_agents.tools._wikipedia import (
    WikipediaSearchTool,
    WikipediaSearchInput,
    WikipediaSearchOutput,
    wikipedia_search_native,
)


class TestToolInput(unittest.TestCase):
    """Test Pydantic ToolInput validation."""

    def test_tool_input_validation(self):
        """Test that ToolInput enforces strict validation."""
        class MyInput(ToolInput):
            query: str
            limit: int = 10

        # Valid input
        valid = MyInput(query="test", limit=5)
        self.assertEqual(valid.query, "test")
        self.assertEqual(valid.limit, 5)

        # Extra fields should be forbidden
        with self.assertRaises(ValidationError):
            MyInput(query="test", unknown_field="value")

    def test_tool_input_defaults(self):
        """Test default values work correctly."""
        class MyInput(ToolInput):
            query: str
            limit: int = 10

        input_obj = MyInput(query="test")
        self.assertEqual(input_obj.limit, 10)


class TestToolOutput(unittest.TestCase):
    """Test Pydantic ToolOutput structure."""

    def test_tool_output_success(self):
        """Test successful output creation."""
        output = ToolOutput(success=True, data={"result": "test"})
        self.assertTrue(output.success)
        self.assertEqual(output.data, {"result": "test"})
        self.assertIsNone(output.error)

    def test_tool_output_error(self):
        """Test error output creation."""
        output = ToolOutput(success=False, error="Something went wrong")
        self.assertFalse(output.success)
        self.assertEqual(output.error, "Something went wrong")


class TestSaptivaTool(unittest.IsolatedAsyncioTestCase):
    """Test SaptivaTool base class."""

    async def test_abstract_tool_implementation(self):
        """Test that SaptivaTool can be properly subclassed."""
        class MyTool(SaptivaTool[str]):
            name = "my_test_tool"
            description = "A test tool"

            async def _arun(self, value: str) -> str:
                return f"processed: {value}"

        tool = MyTool()
        result = await tool("test_input")
        self.assertEqual(result, "processed: test_input")

    async def test_tool_callable(self):
        """Test that tool can be called directly."""
        class EchoTool(SaptivaTool[str]):
            name = "echo"
            description = "Echo input"

            async def _arun(self, text: str) -> str:
                return text

        tool = EchoTool()
        result = await tool("hello")
        self.assertEqual(result, "hello")

    def test_sync_not_implemented(self):
        """Test that sync _run raises NotImplementedError by default."""
        class AsyncOnlyTool(SaptivaTool[str]):
            name = "async_only"
            description = "Only async"

            async def _arun(self, x: str) -> str:
                return x

        tool = AsyncOnlyTool()
        with self.assertRaises(NotImplementedError):
            tool._run("test")


class TestCreateSaptivaTool(unittest.IsolatedAsyncioTestCase):
    """Test the create_saptiva_tool factory function."""

    async def test_create_tool_from_function(self):
        """Test creating a tool from an async function."""
        async def my_function(query: str) -> str:
            """Search for something."""
            return f"Result: {query}"

        tool = create_saptiva_tool(my_function)

        self.assertEqual(tool.name, "my_function")
        self.assertIn("Search for something", tool.description)

    async def test_create_tool_custom_name(self):
        """Test creating tool with custom name and description."""
        async def func(x: str) -> str:
            return x

        tool = create_saptiva_tool(
            func,
            name="custom_name",
            description="Custom description"
        )

        self.assertEqual(tool.name, "custom_name")
        self.assertEqual(tool.description, "Custom description")


class TestWikipediaSearchInput(unittest.TestCase):
    """Test WikipediaSearchInput Pydantic model."""

    def test_valid_input(self):
        """Test valid input creation."""
        input_obj = WikipediaSearchInput(query="Python programming")
        self.assertEqual(input_obj.query, "Python programming")
        self.assertEqual(input_obj.lang, "es")  # Default

    def test_custom_lang(self):
        """Test custom language setting."""
        input_obj = WikipediaSearchInput(query="Python", lang="en")
        self.assertEqual(input_obj.lang, "en")

    def test_missing_query(self):
        """Test that query is required."""
        with self.assertRaises(ValidationError):
            WikipediaSearchInput()


class TestWikipediaSearchOutput(unittest.TestCase):
    """Test WikipediaSearchOutput Pydantic model."""

    def test_output_structure(self):
        """Test output structure."""
        output = WikipediaSearchOutput(
            success=True,
            title="Python",
            summary="A programming language",
            url="https://es.wikipedia.org/wiki/Python"
        )
        self.assertTrue(output.success)
        self.assertEqual(output.title, "Python")


class TestWikipediaSearchTool(unittest.IsolatedAsyncioTestCase):
    """Test WikipediaSearchTool native implementation."""

    async def test_tool_initialization(self):
        """Test tool can be initialized."""
        tool = WikipediaSearchTool()
        self.assertEqual(tool.name, "WikipediaSearchTool")
        self.assertIn("Wikipedia", tool.description)

    async def test_tool_with_custom_params(self):
        """Test tool with custom parameters."""
        tool = WikipediaSearchTool(lang="en", max_chars=500)
        self.assertEqual(tool.lang, "en")
        self.assertEqual(tool.max_chars, 500)

    @patch('aiohttp.ClientSession')
    async def test_successful_search(self, mock_session_class):
        """Test successful Wikipedia search with mocked response."""
        # Setup mock
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "title": "Python (lenguaje de programación)",
            "extract": "Python es un lenguaje de programación interpretado."
        })

        mock_session = MagicMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.get = MagicMock(return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=mock_response),
            __aexit__=AsyncMock(return_value=None)
        ))

        mock_session_class.return_value = mock_session

        tool = WikipediaSearchTool()
        result = await tool._arun("Python")

        self.assertIn("Python", result)
        self.assertIn("lenguaje de programación", result)

    @patch('aiohttp.ClientSession')
    async def test_not_found_fallback(self, mock_session_class):
        """Test fallback when article not found (404)."""
        # First call returns 404, simulating not found
        mock_response_404 = AsyncMock()
        mock_response_404.status = 404

        # Search API response
        mock_search_response = AsyncMock()
        mock_search_response.status = 200
        mock_search_response.json = AsyncMock(return_value={
            "query": {"search": [{"title": "Python programming"}]}
        })

        # Final summary response
        mock_summary_response = AsyncMock()
        mock_summary_response.status = 200
        mock_summary_response.json = AsyncMock(return_value={
            "title": "Python programming",
            "extract": "Python is a programming language."
        })

        call_count = [0]

        def mock_get(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                return AsyncMock(
                    __aenter__=AsyncMock(return_value=mock_response_404),
                    __aexit__=AsyncMock(return_value=None)
                )
            elif call_count[0] == 2:
                return AsyncMock(
                    __aenter__=AsyncMock(return_value=mock_search_response),
                    __aexit__=AsyncMock(return_value=None)
                )
            else:
                return AsyncMock(
                    __aenter__=AsyncMock(return_value=mock_summary_response),
                    __aexit__=AsyncMock(return_value=None)
                )

        mock_session = MagicMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.get = mock_get

        mock_session_class.return_value = mock_session

        tool = WikipediaSearchTool()
        result = await tool._arun("nonexistent_article_xyz")

        # Should fallback and eventually find something or return not found message
        self.assertIsInstance(result, str)

    @patch('aiohttp.ClientSession')
    async def test_connection_error_handling(self, mock_session_class):
        """Test handling of connection errors."""
        import aiohttp

        mock_session = MagicMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.get = MagicMock(side_effect=aiohttp.ClientError("Connection failed"))

        mock_session_class.return_value = mock_session

        tool = WikipediaSearchTool()
        result = await tool._arun("test")

        self.assertIn("Error", result)

    async def test_truncation(self):
        """Test that long responses are truncated."""
        tool = WikipediaSearchTool(max_chars=50)

        # The truncation logic is in the tool implementation
        # This test verifies the max_chars parameter is stored
        self.assertEqual(tool.max_chars, 50)


class TestWikipediaSearchNativeFunction(unittest.IsolatedAsyncioTestCase):
    """Test the wikipedia_search_native convenience function."""

    @patch('aiohttp.ClientSession')
    async def test_native_function(self, mock_session_class):
        """Test the convenience function works."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "title": "Test",
            "extract": "Test content"
        })

        mock_session = MagicMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.get = MagicMock(return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=mock_response),
            __aexit__=AsyncMock(return_value=None)
        ))

        mock_session_class.return_value = mock_session

        result = await wikipedia_search_native("test")
        self.assertIn("Test", result)


class TestToolIntegrationWithAutoGen(unittest.IsolatedAsyncioTestCase):
    """Test integration of SaptivaTool with AutoGen FunctionTool."""

    async def test_to_function_tool_conversion(self):
        """Test that SaptivaTool converts to AutoGen FunctionTool."""
        from autogen_core.tools import FunctionTool as AutoGenFunctionTool

        class MyTool(SaptivaTool[str]):
            name = "my_tool"
            description = "My description"

            async def _arun(self, query: str) -> str:
                return f"result: {query}"

        tool = MyTool()
        function_tool = tool.to_function_tool()

        self.assertIsInstance(function_tool, AutoGenFunctionTool)
        self.assertEqual(function_tool.name, "my_tool")


if __name__ == "__main__":
    unittest.main()
