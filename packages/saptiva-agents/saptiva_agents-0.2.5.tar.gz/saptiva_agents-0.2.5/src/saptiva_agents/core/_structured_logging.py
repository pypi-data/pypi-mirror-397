"""
Structured logging for agent turns and team events.

Provides consistent logging format for observability and debugging
of multi-agent research workflows.

Usage:
    from saptiva_agents.core import log_agent_turn, log_team_event, AgentTurnEvent

    event = AgentTurnEvent(
        team_id="abc123",
        agent_name="WebSearcher",
        turn_number=3,
        phase="searching",
    )
    log_agent_turn(event)
"""

from __future__ import annotations

import logging
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Optional

from saptiva_agents._constants import EVENT_LOGGER_NAME
from saptiva_agents.core._observability import get_request_id

event_logger = logging.getLogger(EVENT_LOGGER_NAME)


@dataclass
class AgentTurnEvent:
    """
    Structured event for agent turn logging.

    Captures all relevant information about a single agent turn
    in a multi-agent conversation.
    """

    team_id: str
    """Unique identifier for the team/session."""

    agent_name: str
    """Name of the agent that took this turn."""

    turn_number: int
    """Sequential turn number in the conversation."""

    phase: str
    """Current research phase (planning, searching, etc.)."""

    input_tokens: int = 0
    """Tokens in the input prompt."""

    output_tokens: int = 0
    """Tokens in the agent response."""

    duration_ms: float = 0.0
    """Time taken for this turn in milliseconds."""

    tool_calls: list[str] = field(default_factory=list)
    """List of tools called during this turn."""

    decision_reason: Optional[str] = None
    """Reason for selecting this agent (from SelectorGroupChat)."""

    request_id: Optional[str] = field(default=None)
    """Request ID from context."""

    error: Optional[str] = None
    """Error message if turn failed."""

    def __post_init__(self):
        if self.request_id is None:
            self.request_id = get_request_id()


@dataclass
class TeamEvent:
    """
    Structured event for team-level events.

    Captures team lifecycle events like start, complete, error, timeout.
    """

    team_id: str
    """Unique identifier for the team/session."""

    event_type: str
    """Event type: 'start', 'complete', 'error', 'timeout'."""

    total_turns: int = 0
    """Total turns taken by the team."""

    total_tokens: int = 0
    """Total tokens consumed by the team."""

    duration_ms: float = 0.0
    """Total duration in milliseconds."""

    result_status: Optional[str] = None
    """Result status: 'success', 'timeout', 'error'."""

    sources_collected: int = 0
    """Number of sources collected (for research teams)."""

    error: Optional[str] = None
    """Error message if team failed."""

    request_id: Optional[str] = field(default=None)
    """Request ID from context."""

    metadata: dict[str, Any] = field(default_factory=dict)
    """Additional metadata."""

    def __post_init__(self):
        if self.request_id is None:
            self.request_id = get_request_id()


@dataclass
class ToolCallEvent:
    """
    Structured event for tool call logging.

    Captures details about individual tool invocations.
    """

    team_id: str
    """Team context."""

    agent_name: str
    """Agent that called the tool."""

    tool_name: str
    """Name of the tool called."""

    turn_number: int
    """Turn in which tool was called."""

    duration_ms: float = 0.0
    """Tool execution time."""

    success: bool = True
    """Whether tool call succeeded."""

    cached: bool = False
    """Whether result was from cache."""

    error: Optional[str] = None
    """Error message if tool failed."""

    request_id: Optional[str] = field(default=None)

    def __post_init__(self):
        if self.request_id is None:
            self.request_id = get_request_id()


def log_agent_turn(event: AgentTurnEvent) -> None:
    """
    Log agent turn event with structured data.

    Args:
        event: Agent turn event to log
    """
    event_logger.info(
        "agent_turn team_id=%s agent=%s turn=%d phase=%s tokens=%d/%d ms=%.1f tools=%s request_id=%s",
        event.team_id,
        event.agent_name,
        event.turn_number,
        event.phase,
        event.input_tokens,
        event.output_tokens,
        event.duration_ms,
        ",".join(event.tool_calls) if event.tool_calls else "none",
        event.request_id,
        extra={"event_type": "agent_turn", "event_data": asdict(event)},
    )


def log_team_event(event: TeamEvent) -> None:
    """
    Log team-level event with structured data.

    Args:
        event: Team event to log
    """
    level = logging.ERROR if event.event_type == "error" else logging.INFO

    event_logger.log(
        level,
        "team_%s team_id=%s turns=%d tokens=%d sources=%d ms=%.1f status=%s request_id=%s",
        event.event_type,
        event.team_id,
        event.total_turns,
        event.total_tokens,
        event.sources_collected,
        event.duration_ms,
        event.result_status or event.event_type,
        event.request_id,
        extra={"event_type": f"team_{event.event_type}", "event_data": asdict(event)},
    )


def log_tool_call(event: ToolCallEvent) -> None:
    """
    Log tool call event with structured data.

    Args:
        event: Tool call event to log
    """
    level = logging.WARNING if not event.success else logging.DEBUG

    event_logger.log(
        level,
        "tool_call team_id=%s agent=%s tool=%s turn=%d ms=%.1f success=%s cached=%s request_id=%s",
        event.team_id,
        event.agent_name,
        event.tool_name,
        event.turn_number,
        event.duration_ms,
        event.success,
        event.cached,
        event.request_id,
        extra={"event_type": "tool_call", "event_data": asdict(event)},
    )


class TurnTimer:
    """
    Context manager for timing agent turns.

    Usage:
        with TurnTimer() as timer:
            result = await agent.run(task)
        print(f"Turn took {timer.duration_ms}ms")
    """

    def __init__(self):
        self._start: float = 0.0
        self.duration_ms: float = 0.0

    def __enter__(self) -> "TurnTimer":
        self._start = time.perf_counter()
        return self

    def __exit__(self, *args) -> None:
        self.duration_ms = (time.perf_counter() - self._start) * 1000


class TeamTimer:
    """
    Context manager for timing team execution.

    Usage:
        with TeamTimer() as timer:
            result = await team.run(task)
        print(f"Team took {timer.duration_ms}ms")
    """

    def __init__(self):
        self._start: float = 0.0
        self.duration_ms: float = 0.0

    def __enter__(self) -> "TeamTimer":
        self._start = time.perf_counter()
        return self

    def __exit__(self, *args) -> None:
        self.duration_ms = (time.perf_counter() - self._start) * 1000

    async def __aenter__(self) -> "TeamTimer":
        self._start = time.perf_counter()
        return self

    async def __aexit__(self, *args) -> None:
        self.duration_ms = (time.perf_counter() - self._start) * 1000
