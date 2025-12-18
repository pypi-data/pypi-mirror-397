"""
Research workflow orchestrator with phase validation.

Provides programmatic control over research phases, global timeout,
and structured logging instead of relying solely on prompts.

Usage:
    from saptiva_agents.teams import ResearchOrchestrator, OrchestratorConfig

    team = await create_deep_research_team(client, config)
    orchestrator = ResearchOrchestrator(team, OrchestratorConfig(team_timeout_s=300))

    result = await orchestrator.run(task="Research quantum computing")
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from typing import Any, AsyncIterator, Optional

from pydantic import BaseModel, Field

from saptiva_agents._constants import ROOT_LOGGER_NAME
from saptiva_agents.core._observability import get_request_id
from saptiva_agents.core._research_context import (
    ResearchPhase,
    SharedResearchContext,
    get_research_context,
    research_context,
)
from saptiva_agents.core._structured_logging import (
    TeamEvent,
    TeamTimer,
    log_team_event,
)

logger = logging.getLogger(ROOT_LOGGER_NAME)


class OrchestratorConfig(BaseModel):
    """Configuration for research orchestrator."""

    team_timeout_s: float = Field(
        default=300.0,
        ge=30.0,
        le=1800.0,
        description="Global timeout for team execution in seconds",
    )
    min_sources_for_synthesis: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Minimum sources required before synthesis phase",
    )
    max_iterations: int = Field(
        default=20,
        ge=3,
        le=50,
        description="Maximum search/read iterations before forcing completion",
    )
    require_critic_approval: bool = Field(
        default=True,
        description="Require Critic approval before completion",
    )
    auto_create_context: bool = Field(
        default=True,
        description="Automatically create research context if not present",
    )


class PhaseTransitionError(Exception):
    """Invalid phase transition attempted."""

    pass


class ResearchTimeoutError(Exception):
    """Research team exceeded timeout."""

    pass


class ResearchOrchestrator:
    """
    Orchestrates research workflow with validation and timeout.

    Wraps a SelectorGroupChat team and provides:
    - Global timeout enforcement
    - Research context management
    - Phase transition validation
    - Structured event logging

    Example:
        team = await create_deep_research_team(client)
        orchestrator = ResearchOrchestrator(team)

        # Run with automatic context management
        result = await orchestrator.run("Research topic")

        # Or with explicit context
        with research_context() as ctx:
            result = await orchestrator.run("Research topic")
            print(f"Collected {len(ctx.collected_sources)} sources")
    """

    # Valid phase transitions
    VALID_TRANSITIONS: dict[ResearchPhase, set[ResearchPhase]] = {
        ResearchPhase.PLANNING: {ResearchPhase.SEARCHING},
        ResearchPhase.SEARCHING: {ResearchPhase.READING, ResearchPhase.SYNTHESIZING},
        ResearchPhase.READING: {ResearchPhase.SEARCHING, ResearchPhase.SYNTHESIZING},
        ResearchPhase.SYNTHESIZING: {ResearchPhase.VERIFYING, ResearchPhase.SEARCHING},
        ResearchPhase.VERIFYING: {ResearchPhase.COMPLETE, ResearchPhase.SEARCHING},
        ResearchPhase.COMPLETE: set(),
    }

    def __init__(
        self,
        team: Any,  # SelectorGroupChat
        config: Optional[OrchestratorConfig] = None,
    ):
        """
        Initialize orchestrator.

        Args:
            team: SelectorGroupChat team to orchestrate
            config: Optional configuration overrides
        """
        self.team = team
        self.config = config or OrchestratorConfig()
        self.team_id = str(uuid.uuid4())[:8]
        self._turn_count = 0
        self._total_tokens = 0

    def can_transition(self, from_phase: ResearchPhase, to_phase: ResearchPhase) -> bool:
        """Check if phase transition is valid."""
        return to_phase in self.VALID_TRANSITIONS.get(from_phase, set())

    def validate_transition(
        self,
        ctx: SharedResearchContext,
        to_phase: ResearchPhase,
    ) -> None:
        """
        Validate phase transition based on current state.

        Raises:
            PhaseTransitionError: If transition is invalid
        """
        current = ctx.plan_state.current_phase

        if not self.can_transition(current, to_phase):
            raise PhaseTransitionError(
                f"Invalid transition from {current.value} to {to_phase.value}"
            )

        # Additional validation based on target phase
        if to_phase == ResearchPhase.SYNTHESIZING:
            if not ctx.has_sufficient_sources(self.config.min_sources_for_synthesis):
                raise PhaseTransitionError(
                    f"Need at least {self.config.min_sources_for_synthesis} sources "
                    f"before synthesis, have {len(ctx.collected_sources)}"
                )

    async def run(
        self,
        task: str,
        timeout_s: Optional[float] = None,
    ) -> Any:
        """
        Run research with orchestration and timeout.

        Args:
            task: Research task/query
            timeout_s: Optional timeout override

        Returns:
            TaskResult from team execution

        Raises:
            ResearchTimeoutError: If timeout exceeded
        """
        timeout = timeout_s or self.config.team_timeout_s
        request_id = get_request_id()

        # Log team start
        log_team_event(
            TeamEvent(
                team_id=self.team_id,
                event_type="start",
                request_id=request_id,
            )
        )

        async with TeamTimer() as timer:
            try:
                # Create context if needed and not present
                existing_ctx = get_research_context()
                if existing_ctx is None and self.config.auto_create_context:
                    async with asyncio.timeout(timeout):
                        with research_context() as ctx:
                            result = await self.team.run(task=task)
                            self._log_completion(ctx, timer, request_id, "success")
                            return result
                else:
                    async with asyncio.timeout(timeout):
                        result = await self.team.run(task=task)
                        ctx = get_research_context()
                        self._log_completion(ctx, timer, request_id, "success")
                        return result

            except asyncio.TimeoutError:
                ctx = get_research_context()
                self._log_completion(ctx, timer, request_id, "timeout")
                raise ResearchTimeoutError(
                    f"Research exceeded {timeout}s timeout. "
                    f"Collected {len(ctx.collected_sources) if ctx else 0} sources."
                )
            except Exception as e:
                ctx = get_research_context()
                log_team_event(
                    TeamEvent(
                        team_id=self.team_id,
                        event_type="error",
                        duration_ms=timer.duration_ms,
                        result_status="error",
                        sources_collected=len(ctx.collected_sources) if ctx else 0,
                        error=str(e),
                        request_id=request_id,
                    )
                )
                raise

    async def run_stream(
        self,
        task: str,
        timeout_s: Optional[float] = None,
    ) -> AsyncIterator[Any]:
        """
        Run research with streaming output.

        Args:
            task: Research task/query
            timeout_s: Optional timeout override

        Yields:
            Messages from team execution

        Raises:
            ResearchTimeoutError: If timeout exceeded
        """
        timeout = timeout_s or self.config.team_timeout_s
        request_id = get_request_id()

        log_team_event(
            TeamEvent(
                team_id=self.team_id,
                event_type="start",
                request_id=request_id,
            )
        )

        async with TeamTimer() as timer:
            try:
                existing_ctx = get_research_context()
                if existing_ctx is None and self.config.auto_create_context:
                    with research_context() as ctx:
                        async with asyncio.timeout(timeout):
                            async for message in self.team.run_stream(task=task):
                                yield message
                        self._log_completion(ctx, timer, request_id, "success")
                else:
                    async with asyncio.timeout(timeout):
                        async for message in self.team.run_stream(task=task):
                            yield message
                    ctx = get_research_context()
                    self._log_completion(ctx, timer, request_id, "success")

            except asyncio.TimeoutError:
                ctx = get_research_context()
                self._log_completion(ctx, timer, request_id, "timeout")
                raise ResearchTimeoutError(
                    f"Research exceeded {timeout}s timeout. "
                    f"Collected {len(ctx.collected_sources) if ctx else 0} sources."
                )

    def _log_completion(
        self,
        ctx: Optional[SharedResearchContext],
        timer: TeamTimer,
        request_id: Optional[str],
        status: str,
    ) -> None:
        """Log team completion event."""
        sources = len(ctx.collected_sources) if ctx else 0
        metadata = ctx.get_stats() if ctx else {}

        log_team_event(
            TeamEvent(
                team_id=self.team_id,
                event_type="complete" if status == "success" else status,
                duration_ms=timer.duration_ms,
                result_status=status,
                sources_collected=sources,
                request_id=request_id,
                metadata=metadata,
            )
        )

        logger.info(
            "research_complete team_id=%s status=%s sources=%d ms=%.1f request_id=%s",
            self.team_id,
            status,
            sources,
            timer.duration_ms,
            request_id,
        )
