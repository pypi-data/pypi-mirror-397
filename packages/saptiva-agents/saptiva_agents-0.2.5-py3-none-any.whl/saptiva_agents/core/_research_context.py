"""
Shared research context for multi-agent research teams.

Uses contextvars for async-safe shared state between agents.
Follows the pattern established in _observability.py.

Usage:
    from saptiva_agents.core import research_context, get_research_context

    with research_context() as ctx:
        # All agents in this context share the same state
        ctx.add_source(Source(url="https://example.com", title="Example"))
        result = await team.run(task="Research quantum computing")
"""

from __future__ import annotations

import time
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterator, Optional

from pydantic import BaseModel, Field


class ResearchPhase(str, Enum):
    """Research workflow phases."""

    PLANNING = "planning"
    SEARCHING = "searching"
    READING = "reading"
    SYNTHESIZING = "synthesizing"
    VERIFYING = "verifying"
    COMPLETE = "complete"


class Source(BaseModel):
    """A collected research source."""

    url: str = Field(..., description="Source URL")
    title: Optional[str] = Field(default=None, description="Page title")
    snippet: Optional[str] = Field(default=None, description="Search result snippet")
    content: Optional[str] = Field(default=None, description="Extracted content (truncated)")
    quotes: list[str] = Field(default_factory=list, description="Notable quotes from source")
    accessed_at: float = Field(default_factory=time.time, description="Unix timestamp when accessed")

    class Config:
        extra = "allow"


class PlanState(BaseModel):
    """Research plan state tracking."""

    subquestions: list[str] = Field(default_factory=list, description="Subquestions to answer")
    sufficiency_criteria: list[str] = Field(default_factory=list, description="Criteria for completeness")
    current_phase: ResearchPhase = Field(default=ResearchPhase.PLANNING, description="Current workflow phase")
    current_subquestion_idx: int = Field(default=0, ge=0, description="Index of current subquestion")
    iterations: int = Field(default=0, ge=0, description="Number of search/read iterations")


@dataclass
class SharedResearchContext:
    """
    Shared state between research agents.

    This context is automatically available to all agents within a
    `research_context()` block via `get_research_context()`.

    Attributes:
        visited_urls: URLs that have been successfully read
        failed_urls: URLs that failed (403, blocked, timeout)
        collected_sources: Successfully collected sources with content
        plan_state: Current research plan state
        gaps_detected: Gaps identified by Critic agent
        search_queries_used: Search queries already executed
    """

    visited_urls: set[str] = field(default_factory=set)
    failed_urls: set[str] = field(default_factory=set)
    collected_sources: list[Source] = field(default_factory=list)
    plan_state: PlanState = field(default_factory=PlanState)
    gaps_detected: list[str] = field(default_factory=list)
    search_queries_used: set[str] = field(default_factory=set)

    def add_source(self, source: Source) -> bool:
        """
        Add source if URL not already visited.

        Args:
            source: Source to add

        Returns:
            True if added, False if URL was already visited
        """
        if source.url in self.visited_urls:
            return False
        self.visited_urls.add(source.url)
        self.collected_sources.append(source)
        return True

    def mark_failed(self, url: str, reason: Optional[str] = None) -> None:
        """
        Mark URL as failed (403, blocked, timeout, etc.).

        Args:
            url: URL that failed
            reason: Optional failure reason for logging
        """
        self.failed_urls.add(url)

    def should_skip_url(self, url: str) -> bool:
        """
        Check if URL should be skipped.

        Returns True if URL was already visited or failed.
        """
        return url in self.visited_urls or url in self.failed_urls

    def add_query(self, query: str) -> bool:
        """
        Track a search query.

        Args:
            query: Search query string

        Returns:
            True if query is new, False if already used
        """
        normalized = query.strip().lower()
        if normalized in self.search_queries_used:
            return False
        self.search_queries_used.add(normalized)
        return True

    def transition_phase(self, new_phase: ResearchPhase) -> None:
        """
        Transition to new research phase.

        Args:
            new_phase: Target phase
        """
        self.plan_state.current_phase = new_phase

    def increment_iteration(self) -> int:
        """Increment and return iteration count."""
        self.plan_state.iterations += 1
        return self.plan_state.iterations

    def has_sufficient_sources(self, min_sources: int = 3) -> bool:
        """Check if minimum sources have been collected."""
        return len(self.collected_sources) >= min_sources

    def get_stats(self) -> dict:
        """Get context statistics for logging."""
        return {
            "sources_collected": len(self.collected_sources),
            "urls_visited": len(self.visited_urls),
            "urls_failed": len(self.failed_urls),
            "queries_used": len(self.search_queries_used),
            "gaps_detected": len(self.gaps_detected),
            "current_phase": self.plan_state.current_phase.value,
            "iterations": self.plan_state.iterations,
        }


# Context variable for shared research context
_research_context_var: ContextVar[Optional[SharedResearchContext]] = ContextVar(
    "saptiva_research_context", default=None
)


def get_research_context() -> Optional[SharedResearchContext]:
    """
    Get current research context from async context.

    Returns None if not within a research_context() block.
    """
    return _research_context_var.get()


@contextmanager
def research_context(ctx: Optional[SharedResearchContext] = None) -> Iterator[SharedResearchContext]:
    """
    Set research context for current async context.

    Creates new context if none provided. The context is available
    to all code within this block via get_research_context().

    Args:
        ctx: Optional existing context to use

    Yields:
        SharedResearchContext: The active research context

    Example:
        with research_context() as ctx:
            ctx.add_source(Source(url="https://example.com"))
            result = await team.run(task="Research topic")
            print(f"Collected {len(ctx.collected_sources)} sources")
    """
    if ctx is None:
        ctx = SharedResearchContext()

    token = _research_context_var.set(ctx)
    try:
        yield ctx
    finally:
        _research_context_var.reset(token)
