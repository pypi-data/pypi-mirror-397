"""
Pydantic models for research plan validation and workflow orchestration.

These models provide JSON schema validation for research plans generated
by the LeadResearcher agent, ensuring structured and predictable output.

Usage:
    from saptiva_agents.core import ResearchPlan, validate_research_plan

    plan_json = {"query": "...", "subquestions": [...]}
    result = validate_research_plan(plan_json)
    if result.valid:
        plan = result.plan
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field, model_validator


class ResearchPlanSubquestion(BaseModel):
    """A subquestion in the research plan."""

    question: str = Field(..., min_length=10, description="The subquestion to answer")
    keywords: list[str] = Field(default_factory=list, description="Search keywords for this subquestion")
    priority: int = Field(default=1, ge=1, le=5, description="Priority level 1-5 (1 = highest)")
    answered: bool = Field(default=False, description="Whether this subquestion has been answered")
    sources_required: int = Field(default=1, ge=1, le=5, description="Minimum sources needed")


class SufficiencyCriterion(BaseModel):
    """Criterion for determining research sufficiency."""

    description: str = Field(..., min_length=5, description="Description of the criterion")
    min_sources: int = Field(default=1, ge=1, description="Minimum sources to satisfy criterion")
    met: bool = Field(default=False, description="Whether criterion has been met")


class ResearchPlan(BaseModel):
    """
    Research plan with JSON schema validation.

    The LeadResearcher agent must produce valid JSON matching this schema.
    This enables programmatic validation instead of relying solely on prompts.

    Example JSON:
        {
            "query": "What are the latest advances in quantum computing?",
            "subquestions": [
                {
                    "question": "What are the main approaches to quantum computing?",
                    "keywords": ["quantum computing", "approaches", "superconducting", "ion trap"],
                    "priority": 1
                },
                {
                    "question": "What recent breakthroughs have been announced?",
                    "keywords": ["quantum computing", "breakthrough", "2024", "Google", "IBM"],
                    "priority": 2
                }
            ],
            "min_total_sources": 5
        }
    """

    query: str = Field(..., min_length=5, description="Original research query")
    subquestions: list[ResearchPlanSubquestion] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Subquestions to answer for comprehensive coverage",
    )
    sufficiency_criteria: list[SufficiencyCriterion] = Field(
        default_factory=list,
        description="Criteria for determining when research is complete",
    )
    min_total_sources: int = Field(default=3, ge=1, le=20, description="Minimum total sources required")
    max_search_iterations: int = Field(default=5, ge=1, le=10, description="Maximum search iterations allowed")
    language: str = Field(default="es", description="Language for research and output")

    @model_validator(mode="after")
    def validate_plan(self) -> "ResearchPlan":
        """Auto-generate default sufficiency criterion if none provided."""
        if not self.sufficiency_criteria:
            self.sufficiency_criteria = [
                SufficiencyCriterion(
                    description=f"Collect at least {self.min_total_sources} sources",
                    min_sources=self.min_total_sources,
                )
            ]
        return self

    def get_unanswered_subquestions(self) -> list[ResearchPlanSubquestion]:
        """Get subquestions that haven't been answered yet."""
        return [sq for sq in self.subquestions if not sq.answered]

    def get_next_subquestion(self) -> Optional[ResearchPlanSubquestion]:
        """Get next unanswered subquestion by priority."""
        unanswered = self.get_unanswered_subquestions()
        if not unanswered:
            return None
        return min(unanswered, key=lambda sq: sq.priority)

    def mark_subquestion_answered(self, index: int) -> None:
        """Mark a subquestion as answered by index."""
        if 0 <= index < len(self.subquestions):
            self.subquestions[index].answered = True

    def is_complete(self, sources_collected: int) -> bool:
        """Check if research plan is complete."""
        # All subquestions answered
        all_answered = all(sq.answered for sq in self.subquestions)
        # Minimum sources met
        sources_met = sources_collected >= self.min_total_sources
        return all_answered and sources_met

    def to_prompt_context(self) -> str:
        """Generate context string for agent prompts."""
        lines = [
            f"Query: {self.query}",
            f"Subquestions ({len(self.get_unanswered_subquestions())} pending):",
        ]
        for i, sq in enumerate(self.subquestions):
            status = "[DONE]" if sq.answered else "[PENDING]"
            lines.append(f"  {i+1}. {status} {sq.question}")
        return "\n".join(lines)


class PlanValidationResult(BaseModel):
    """Result of plan validation."""

    valid: bool = Field(..., description="Whether the plan JSON is valid")
    plan: Optional[ResearchPlan] = Field(default=None, description="Parsed plan if valid")
    errors: list[str] = Field(default_factory=list, description="Validation errors if invalid")


def validate_research_plan(plan_json: dict[str, Any]) -> PlanValidationResult:
    """
    Validate JSON dict against ResearchPlan schema.

    Args:
        plan_json: Dictionary to validate

    Returns:
        PlanValidationResult with valid flag, parsed plan, and any errors

    Example:
        result = validate_research_plan({"query": "test", "subquestions": [...]})
        if result.valid:
            print(f"Plan has {len(result.plan.subquestions)} subquestions")
        else:
            print(f"Errors: {result.errors}")
    """
    try:
        plan = ResearchPlan.model_validate(plan_json)
        return PlanValidationResult(valid=True, plan=plan)
    except Exception as e:
        error_msg = str(e)
        # Extract more readable error message from Pydantic
        if hasattr(e, "errors"):
            errors = [f"{err.get('loc', '')}: {err.get('msg', '')}" for err in e.errors()]
        else:
            errors = [error_msg]
        return PlanValidationResult(valid=False, errors=errors)


def extract_plan_from_text(text: str) -> Optional[dict[str, Any]]:
    """
    Attempt to extract JSON plan from agent text response.

    Looks for JSON blocks in markdown or raw JSON.

    Args:
        text: Agent response text

    Returns:
        Parsed JSON dict or None if not found
    """
    import json
    import re

    # Try to find JSON in markdown code block
    json_block_pattern = r"```(?:json)?\s*(\{.*?\})\s*```"
    match = re.search(json_block_pattern, text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # Try to find raw JSON object
    json_pattern = r"\{[^{}]*\"query\"[^{}]*\"subquestions\"[^{}]*\}"
    match = re.search(json_pattern, text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    # Try parsing entire text as JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    return None
