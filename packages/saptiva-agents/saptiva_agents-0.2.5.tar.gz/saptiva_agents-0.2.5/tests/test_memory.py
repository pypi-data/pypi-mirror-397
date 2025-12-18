"""
Tests for Memory systems.

Tests cover:
- ListMemory (in-memory)
- Memory integration with agents
- Memory edge cases

Note: These tests verify the memory wrapper around AutoGen's ListMemory.
Deep testing of memory logic is handled by AutoGen's test suite.
"""

import unittest
from unittest.mock import AsyncMock, MagicMock

from saptiva_agents.memory import ListMemory, MemoryContent, MemoryMimeType


class TestListMemory(unittest.IsolatedAsyncioTestCase):
    """Test ListMemory implementation."""

    async def test_memory_initialization(self):
        """Test memory can be initialized."""
        memory = ListMemory()
        self.assertIsNotNone(memory)
        self.assertEqual(len(memory.content), 0)

    async def test_memory_add_message(self):
        """Test adding messages to memory."""
        memory = ListMemory()

        content1 = MemoryContent(content="Hello", mime_type=MemoryMimeType.TEXT)
        content2 = MemoryContent(content="Hi there!", mime_type=MemoryMimeType.TEXT)

        await memory.add(content1)
        await memory.add(content2)

        self.assertEqual(len(memory.content), 2)

    async def test_memory_get_content(self):
        """Test retrieving content from memory."""
        memory = ListMemory()

        content1 = MemoryContent(content="Message 1", mime_type=MemoryMimeType.TEXT)
        content2 = MemoryContent(content="Response 1", mime_type=MemoryMimeType.TEXT)
        content3 = MemoryContent(content="Message 2", mime_type=MemoryMimeType.TEXT)

        await memory.add(content1)
        await memory.add(content2)
        await memory.add(content3)

        self.assertEqual(len(memory.content), 3)
        self.assertEqual(memory.content[0].content, "Message 1")
        self.assertEqual(memory.content[1].content, "Response 1")

    async def test_memory_clear(self):
        """Test clearing memory."""
        memory = ListMemory()

        content = MemoryContent(content="Test message", mime_type=MemoryMimeType.TEXT)
        await memory.add(content)
        self.assertEqual(len(memory.content), 1)

        await memory.clear()
        self.assertEqual(len(memory.content), 0)

    async def test_memory_with_initialization_content(self):
        """Test memory initialized with content."""
        initial_content = [
            MemoryContent(content="Message 1", mime_type=MemoryMimeType.TEXT),
            MemoryContent(content="Message 2", mime_type=MemoryMimeType.TEXT),
        ]

        memory = ListMemory(memory_contents=initial_content)

        self.assertEqual(len(memory.content), 2)

    async def test_memory_empty_state(self):
        """Test memory in empty state."""
        memory = ListMemory()

        self.assertEqual(len(memory.content), 0)
        self.assertEqual(memory.content, [])


class TestMemoryIntegration(unittest.IsolatedAsyncioTestCase):
    """Test memory integration with agents."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_model_client = MagicMock()
        self.mock_model_client.create = AsyncMock()

    async def test_agent_with_memory(self):
        """Test agent using memory for conversation history."""
        from saptiva_agents.agents import AssistantAgent

        memory = ListMemory()
        agent = AssistantAgent(
            name="memory_agent",
            model_client=self.mock_model_client,
            system_message="You remember conversations."
        )

        # Memory and agent can coexist
        self.assertIsNotNone(agent)
        self.assertIsNotNone(memory)

    async def test_memory_persistence_across_calls(self):
        """Test that memory persists across multiple operations."""
        memory = ListMemory()

        # Simulate multiple interactions
        content1 = MemoryContent(content="What is Python?", mime_type=MemoryMimeType.TEXT)
        content2 = MemoryContent(content="Python is a programming language.", mime_type=MemoryMimeType.TEXT)
        content3 = MemoryContent(content="Tell me more", mime_type=MemoryMimeType.TEXT)

        await memory.add(content1)
        await memory.add(content2)
        await memory.add(content3)

        self.assertEqual(len(memory.content), 3)

        # Memory should persist (same reference)
        content_again = memory.content
        self.assertEqual(len(content_again), 3)


class TestMemoryContentTypes(unittest.TestCase):
    """Test MemoryContent with different types."""

    def test_text_content(self):
        """Test MemoryContent with text."""
        content = MemoryContent(content="Hello", mime_type=MemoryMimeType.TEXT)
        self.assertEqual(content.content, "Hello")
        self.assertEqual(content.mime_type, MemoryMimeType.TEXT)

    def test_content_with_metadata(self):
        """Test MemoryContent with metadata."""
        metadata = {"role": "user", "timestamp": "2024-01-01"}
        content = MemoryContent(
            content="Message",
            mime_type=MemoryMimeType.TEXT,
            metadata=metadata
        )
        self.assertEqual(content.metadata, metadata)

    def test_json_content(self):
        """Test MemoryContent with JSON."""
        json_data = {"key": "value", "number": 42}
        content = MemoryContent(
            content=json_data,
            mime_type=MemoryMimeType.JSON
        )
        self.assertEqual(content.content, json_data)


class TestMemoryEdgeCases(unittest.IsolatedAsyncioTestCase):
    """Test edge cases in memory systems."""

    async def test_memory_with_very_long_content(self):
        """Test memory handling very long content."""
        memory = ListMemory()

        long_message = "A" * 10000  # 10k characters
        content = MemoryContent(content=long_message, mime_type=MemoryMimeType.TEXT)
        await memory.add(content)

        self.assertEqual(len(memory.content), 1)
        self.assertEqual(len(memory.content[0].content), 10000)

    async def test_memory_with_special_characters(self):
        """Test memory handling special characters."""
        memory = ListMemory()

        special_msg = "Hello 世界 🌍 \n\t\r Special: <>&\"'"
        content = MemoryContent(content=special_msg, mime_type=MemoryMimeType.TEXT)
        await memory.add(content)

        self.assertEqual(memory.content[0].content, special_msg)

    async def test_memory_concurrent_access(self):
        """Test memory under concurrent access."""
        memory = ListMemory()

        # Add messages concurrently
        import asyncio
        tasks = [
            memory.add(MemoryContent(content=f"Message {i}", mime_type=MemoryMimeType.TEXT))
            for i in range(10)
        ]

        await asyncio.gather(*tasks)

        self.assertEqual(len(memory.content), 10)

    async def test_memory_with_empty_string(self):
        """Test memory handling empty string."""
        memory = ListMemory()

        content = MemoryContent(content="", mime_type=MemoryMimeType.TEXT)
        await memory.add(content)

        self.assertEqual(len(memory.content), 1)
        self.assertEqual(memory.content[0].content, "")


class TestMemoryQuery(unittest.IsolatedAsyncioTestCase):
    """Test memory query functionality."""

    async def test_memory_query_empty(self):
        """Test querying empty memory."""
        memory = ListMemory()

        result = await memory.query("")
        self.assertIsNotNone(result)

    async def test_memory_query_with_content(self):
        """Test querying memory with content."""
        memory = ListMemory()

        content = MemoryContent(content="Test message", mime_type=MemoryMimeType.TEXT)
        await memory.add(content)

        result = await memory.query("test")
        self.assertIsNotNone(result)


class TestMemoryLimits(unittest.IsolatedAsyncioTestCase):
    """Test memory limit helpers."""

    async def test_limit_memory_to_last_n(self):
        from saptiva_agents.memory._base_memory import limit_memory_to_last_n

        memory = ListMemory()
        for i in range(5):
            await memory.add(MemoryContent(content=f"m{i}", mime_type=MemoryMimeType.TEXT))

        limited = limit_memory_to_last_n(memory, 3)
        self.assertEqual([c.content for c in limited.content], ["m2", "m3", "m4"])

    async def test_memory_manager_applies_limit(self):
        from saptiva_agents.memory._list_memory import MemoryManager

        memory = ListMemory()
        manager = MemoryManager(memory, max_items=2)
        await manager.add(MemoryContent(content="a", mime_type=MemoryMimeType.TEXT))
        await manager.add(MemoryContent(content="b", mime_type=MemoryMimeType.TEXT))
        await manager.add(MemoryContent(content="c", mime_type=MemoryMimeType.TEXT))

        self.assertEqual(manager.current_count, 2)
        self.assertTrue(manager.is_full)
        self.assertEqual([c.content for c in memory.content], ["b", "c"])

        manager.set_limit(3)
        self.assertFalse(manager.is_full)


class TestRedisMemory(unittest.IsolatedAsyncioTestCase):
    """Unit tests for RedisMemory wrapper without RedisVL installed."""

    async def test_redis_memory_wrapper_import_and_basic_ops(self):
        import importlib
        import sys
        import types
        from unittest.mock import patch

        fake_module = types.ModuleType("autogen_ext.memory.redis")

        class FakeRedisMemoryConfig:  # pragma: no cover
            pass

        class FakeRedisMemory:
            def __init__(self, **kwargs):
                self.kwargs = kwargs
                self.content = []

            async def add(self, item):
                self.content.append(item)

            async def clear(self):
                self.content.clear()

        fake_module.RedisMemoryConfig = FakeRedisMemoryConfig
        fake_module.RedisMemory = FakeRedisMemory

        # Ensure fresh import of wrapper uses our fake base module.
        sys.modules.pop("saptiva_agents.memory.redis._redis_memory", None)
        sys.modules.pop("saptiva_agents.memory.redis", None)

        with patch.dict(sys.modules, {"autogen_ext.memory.redis": fake_module}):
            redis_mod = importlib.import_module("saptiva_agents.memory.redis._redis_memory")
            RedisMemory = redis_mod.RedisMemory

            memory = RedisMemory(redis_url="redis://localhost:6379", session_id="test-session")
            await memory.add(MemoryContent(content="hi", mime_type=MemoryMimeType.TEXT))
            self.assertEqual(len(memory.content), 1)
            self.assertEqual(memory.kwargs["redis_url"], "redis://localhost:6379")
            await memory.clear()
            self.assertEqual(memory.content, [])


class TestChromaDBMemory(unittest.IsolatedAsyncioTestCase):
    """Unit tests for ChromaDBVectorMemory wrapper without chromadb installed."""

    async def test_chromadb_vector_memory_wrapper_import_and_query(self):
        import importlib
        import sys
        import types
        from unittest.mock import patch

        fake_module = types.ModuleType("autogen_ext.memory.chromadb")

        class FakeConfig:  # pragma: no cover
            def __init__(self, **kwargs):
                self.kwargs = kwargs

        class FakeChromaDBVectorMemory:
            def __init__(self, config=None, **kwargs):
                self.config = config
                self.kwargs = kwargs
                self.content = []

            async def add(self, item):
                self.content.append(item)

            async def query(self, query):
                return list(self.content)

            async def close(self):
                return None

        # Provide all symbols imported by wrapper module.
        fake_module.ChromaDBVectorMemoryConfig = FakeConfig
        fake_module.PersistentChromaDBVectorMemoryConfig = FakeConfig
        fake_module.HttpChromaDBVectorMemoryConfig = FakeConfig
        fake_module.SentenceTransformerEmbeddingFunctionConfig = FakeConfig
        fake_module.ChromaDBVectorMemory = FakeChromaDBVectorMemory

        sys.modules.pop("saptiva_agents.memory.chromadb", None)

        with patch.dict(sys.modules, {"autogen_ext.memory.chromadb": fake_module}):
            chroma_mod = importlib.import_module("saptiva_agents.memory.chromadb")
            ChromaDBVectorMemory = chroma_mod.ChromaDBVectorMemory

            memory = ChromaDBVectorMemory(config=fake_module.PersistentChromaDBVectorMemoryConfig(collection_name="c"))
            await memory.add(MemoryContent(content="Python", mime_type=MemoryMimeType.TEXT))
            results = await memory.query("Python programming")
            self.assertEqual(len(results), 1)


if __name__ == "__main__":
    unittest.main()
