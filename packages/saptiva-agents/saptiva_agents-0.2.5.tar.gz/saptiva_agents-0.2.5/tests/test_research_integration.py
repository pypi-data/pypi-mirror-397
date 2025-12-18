"""Tests for research context, singletons, and orchestration integration."""

from __future__ import annotations

import asyncio
import types
import unittest
from unittest.mock import MagicMock, patch

from saptiva_agents.core._research_context import (
    ResearchPhase,
    SharedResearchContext,
    Source,
    get_research_context,
    research_context,
)
from saptiva_agents.core._research_models import (
    ResearchPlan,
    ResearchPlanSubquestion,
    extract_plan_from_text,
    validate_research_plan,
)
from saptiva_agents.core._singletons import (
    GlobalCache,
    GlobalRateLimiter,
    get_global_cache,
    get_global_rate_limiter,
)
from saptiva_agents.core._structured_logging import (
    AgentTurnEvent,
    TeamEvent,
    TurnTimer,
)


class TestSharedResearchContext(unittest.TestCase):
    """Test SharedResearchContext behavior."""

    def test_add_source_unique(self):
        """Sources with unique URLs should be added."""
        ctx = SharedResearchContext()
        s1 = Source(url="https://a.com", title="A", snippet="...")
        s2 = Source(url="https://b.com", title="B", snippet="...")

        self.assertTrue(ctx.add_source(s1))
        self.assertTrue(ctx.add_source(s2))
        self.assertEqual(len(ctx.collected_sources), 2)

    def test_add_source_duplicate_rejected(self):
        """Duplicate URLs should be rejected."""
        ctx = SharedResearchContext()
        s1 = Source(url="https://a.com", title="A", snippet="...")
        s2 = Source(url="https://a.com", title="A2", snippet="...")

        self.assertTrue(ctx.add_source(s1))
        self.assertFalse(ctx.add_source(s2))
        self.assertEqual(len(ctx.collected_sources), 1)

    def test_mark_failed(self):
        """Failed URLs should be tracked."""
        ctx = SharedResearchContext()
        ctx.mark_failed("https://fail.com", "HTTP 403")

        self.assertIn("https://fail.com", ctx.failed_urls)
        self.assertTrue(ctx.should_skip_url("https://fail.com"))

    def test_should_skip_visited(self):
        """Already visited URLs should be skipped."""
        ctx = SharedResearchContext()
        ctx.visited_urls.add("https://visited.com")

        self.assertTrue(ctx.should_skip_url("https://visited.com"))

    def test_phase_transitions(self):
        """Phase should transition correctly."""
        ctx = SharedResearchContext()
        self.assertEqual(ctx.plan_state.current_phase, ResearchPhase.PLANNING)

        ctx.transition_phase(ResearchPhase.SEARCHING)
        self.assertEqual(ctx.plan_state.current_phase, ResearchPhase.SEARCHING)

    def test_get_stats(self):
        """Stats should include key metrics."""
        ctx = SharedResearchContext()
        ctx.add_source(Source(url="https://a.com", title="A", snippet="..."))
        ctx.mark_failed("https://fail.com")
        ctx.search_queries_used.add("test query")

        stats = ctx.get_stats()
        self.assertEqual(stats["sources_collected"], 1)
        self.assertEqual(stats["urls_failed"], 1)
        self.assertEqual(stats["queries_used"], 1)

    def test_add_query_normalization(self):
        """Queries should be normalized for deduplication."""
        ctx = SharedResearchContext()

        self.assertTrue(ctx.add_query("Test Query"))
        self.assertFalse(ctx.add_query("test query"))  # Normalized duplicate
        self.assertFalse(ctx.add_query("  TEST QUERY  "))  # Normalized duplicate


class TestResearchContextVar(unittest.IsolatedAsyncioTestCase):
    """Test contextvar behavior for research context."""

    async def test_context_manager(self):
        """Context should be accessible within context manager."""
        with research_context() as ctx:
            ctx.add_source(Source(url="https://a.com", title="A"))
            retrieved = get_research_context()
            self.assertIsNotNone(retrieved)
            self.assertIs(ctx, retrieved)

    async def test_context_none_outside_block(self):
        """Context should be None outside of context block."""
        self.assertIsNone(get_research_context())

    async def test_isolation_between_tasks(self):
        """Each async task should have isolated context."""
        results = []

        async def task_with_context(task_id: str):
            with research_context() as ctx:
                ctx.search_queries_used.add(f"query_{task_id}")
                await asyncio.sleep(0.01)
                retrieved = get_research_context()
                results.append((task_id, len(retrieved.search_queries_used)))

        await asyncio.gather(
            task_with_context("a"),
            task_with_context("b"),
            task_with_context("c"),
        )

        # Each task should have exactly 1 query (isolated)
        for task_id, count in results:
            self.assertEqual(count, 1, f"Task {task_id} should have isolated context")


class TestResearchModels(unittest.TestCase):
    """Test Pydantic research models."""

    def test_research_plan_valid(self):
        """Valid plan should be created."""
        plan = ResearchPlan(
            query="What is quantum computing?",
            subquestions=[
                ResearchPlanSubquestion(
                    id="sq1",
                    question="What are qubits?",
                    keywords=["qubit", "quantum bit"],
                    min_sources=2,
                )
            ],
            min_total_sources=3,
        )
        self.assertEqual(plan.query, "What is quantum computing?")
        self.assertEqual(len(plan.subquestions), 1)

    def test_research_plan_validation_error(self):
        """Invalid plan should raise validation error."""
        with self.assertRaises(Exception):  # Pydantic ValidationError
            ResearchPlan(
                query="ab",  # too short (min_length=5)
                subquestions=[],  # too few (min_length=1)
            )

    def test_validate_research_plan_dict(self):
        """Plan dict should be validated."""
        plan_dict = {
            "query": "Test query here that is long enough",
            "subquestions": [
                {"id": "sq1", "question": "Sub question", "keywords": ["k1"], "min_sources": 1}
            ],
        }
        result = validate_research_plan(plan_dict)
        self.assertTrue(result.valid)
        self.assertIsNotNone(result.plan)

    def test_extract_plan_from_text(self):
        """Plan JSON should be extracted from text."""
        text = '''
        Here is my plan:
        ```json
        {
            "query": "Test query",
            "subquestions": [{"id": "1", "question": "Q1", "keywords": ["k"]}]
        }
        ```
        '''
        extracted = extract_plan_from_text(text)
        self.assertIsNotNone(extracted)
        self.assertEqual(extracted["query"], "Test query")

    def test_extract_plan_no_json(self):
        """No JSON in text should return None."""
        text = "No JSON here, just plain text."
        extracted = extract_plan_from_text(text)
        self.assertIsNone(extracted)


class TestGlobalSingletons(unittest.IsolatedAsyncioTestCase):
    """Test global rate limiter and cache singletons."""

    def setUp(self):
        GlobalRateLimiter.reset()
        GlobalCache.reset()

    def tearDown(self):
        GlobalRateLimiter.reset()
        GlobalCache.reset()

    async def test_rate_limiter_singleton(self):
        """Rate limiter should be singleton."""
        rl1 = get_global_rate_limiter()
        rl2 = get_global_rate_limiter()
        self.assertIs(rl1, rl2)

    async def test_cache_singleton(self):
        """Cache should be singleton."""
        c1 = get_global_cache()
        c2 = get_global_cache()
        self.assertIs(c1, c2)

    async def test_rate_limiter_acquire_release(self):
        """Rate limiter should manage semaphores per domain."""
        rl = get_global_rate_limiter()

        await rl.acquire("https://example.com/page1")
        await rl.acquire("https://example.com/page2")  # Same domain
        await rl.acquire("https://other.com/page")  # Different domain

        rl.release("https://example.com/page1")
        rl.release("https://example.com/page2")
        rl.release("https://other.com/page")

    async def test_cache_get_set(self):
        """Cache should store and retrieve values."""
        GlobalCache.reset()
        cache = get_global_cache()

        await cache.set("key1", {"data": "value"})
        result = await cache.get("key1")

        self.assertEqual(result, {"data": "value"})

    async def test_cache_miss(self):
        """Cache miss should return None."""
        GlobalCache.reset()
        cache = get_global_cache()
        result = await cache.get("nonexistent")
        self.assertIsNone(result)

    async def test_cache_stats(self):
        """Cache should track hit/miss stats."""
        GlobalCache.reset()
        cache = get_global_cache()

        await cache.set("key1", "value1")
        await cache.get("key1")  # Hit
        await cache.get("missing")  # Miss

        stats = cache.get_stats()
        self.assertEqual(stats["hits"], 1)
        self.assertEqual(stats["misses"], 1)


class TestStructuredLogging(unittest.TestCase):
    """Test structured logging events."""

    def test_agent_turn_event(self):
        """AgentTurnEvent should be created with all fields."""
        event = AgentTurnEvent(
            team_id="team-123",
            agent_name="WebSearcher",
            turn_number=5,
            phase="SEARCHING",
            input_tokens=100,
            output_tokens=50,
            duration_ms=1234.5,
        )
        self.assertEqual(event.agent_name, "WebSearcher")
        self.assertEqual(event.turn_number, 5)

    def test_team_event(self):
        """TeamEvent should be created with all fields."""
        event = TeamEvent(
            team_id="team-123",
            event_type="start",
            total_turns=0,
            sources_collected=0,
        )
        self.assertEqual(event.event_type, "start")
        self.assertEqual(event.team_id, "team-123")

    def test_turn_timer(self):
        """TurnTimer should measure duration."""
        timer = TurnTimer()

        with timer:
            pass

        self.assertGreater(timer.duration_ms, 0)


class FakeAgent(types.SimpleNamespace):
    @property
    def name(self):
        return self.__dict__["name"]


class FakeTeam:
    def __init__(self, participants, model_client, termination_condition, max_turns):
        self._participants = participants
        self._model_client = model_client
        self._termination_condition = termination_condition
        self._max_turns = max_turns


class TestDeepResearchTeamWithOrchestration(unittest.IsolatedAsyncioTestCase):
    """Test create_deep_research_team with orchestration enabled."""

    @patch("saptiva_agents.teams.research_team.SelectorGroupChat", new=FakeTeam)
    @patch(
        "saptiva_agents.teams.research_team.AssistantAgent",
        side_effect=lambda *args, **kwargs: FakeAgent(**kwargs),
    )
    @patch("saptiva_agents.teams.research_team.SaptivaAIChatCompletionClient")
    async def test_returns_tuple_with_orchestration(self, mock_client_class, _mock_agent):
        """With orchestration enabled, should return (team, orchestrator)."""
        from saptiva_agents.teams.research_team import (
            DeepResearchTeamConfig,
            create_deep_research_team,
        )
        from saptiva_agents.teams._research_orchestrator import ResearchOrchestrator

        mock_client_class.return_value = MagicMock(extra_kwargs={"api_key": "k"})
        base_client = MagicMock(extra_kwargs={"api_key": "k"})

        config = DeepResearchTeamConfig(
            enable_orchestration=True,
            use_global_cache=True,
            use_global_rate_limiter=True,
            team_timeout_s=120,
        )

        result = await create_deep_research_team(base_client, config=config)

        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        team, orchestrator = result
        self.assertIsInstance(orchestrator, ResearchOrchestrator)

    @patch("saptiva_agents.teams.research_team.SelectorGroupChat", new=FakeTeam)
    @patch(
        "saptiva_agents.teams.research_team.AssistantAgent",
        side_effect=lambda *args, **kwargs: FakeAgent(**kwargs),
    )
    @patch("saptiva_agents.teams.research_team.SaptivaAIChatCompletionClient")
    async def test_returns_team_without_orchestration(self, mock_client_class, _mock_agent):
        """With orchestration disabled, should return just team."""
        from saptiva_agents.teams.research_team import (
            DeepResearchTeamConfig,
            create_deep_research_team,
        )

        mock_client_class.return_value = MagicMock(extra_kwargs={"api_key": "k"})
        base_client = MagicMock(extra_kwargs={"api_key": "k"})

        config = DeepResearchTeamConfig(enable_orchestration=False)

        result = await create_deep_research_team(base_client, config=config)

        self.assertIsInstance(result, FakeTeam)
        self.assertNotIsInstance(result, tuple)


if __name__ == "__main__":
    unittest.main()
