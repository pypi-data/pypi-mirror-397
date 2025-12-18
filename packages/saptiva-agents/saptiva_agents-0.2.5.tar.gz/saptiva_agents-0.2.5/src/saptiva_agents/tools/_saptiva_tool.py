"""
Saptiva Tool Standard - Native Python + Pydantic based tools.

This module provides a Pydantic-based tool system that integrates seamlessly
with AutoGen v0.4+ FunctionTool system, replacing the legacy LangChain adapters.

Key benefits over LangChain:
- Native Python async/await support
- Pydantic v2 validation with better performance
- Direct integration with AutoGen's type system
- No external framework dependencies
"""

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar, Callable, Awaitable, Optional
from pydantic import BaseModel, Field, ConfigDict

from autogen_core.tools import FunctionTool as AutoGenFunctionTool


# Type variable for tool return types
T = TypeVar("T")


class ToolInput(BaseModel):
    """Base class for tool input validation using Pydantic."""
    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class ToolOutput(BaseModel):
    """Base class for tool output with structured response."""
    success: bool = Field(default=True, description="Whether the tool execution was successful")
    data: Any = Field(default=None, description="The result data from the tool")
    error: Optional[str] = Field(default=None, description="Error message if execution failed")

    model_config = ConfigDict(extra="allow")


class SaptivaTool(ABC, Generic[T]):
    """
    Abstract base class for Saptiva Tools using Pydantic validation.

    This provides a standardized interface for creating tools that:
    - Use Pydantic for input/output validation
    - Support both sync and async execution
    - Integrate with AutoGen v0.4+ FunctionTool system

    Example:
        class MyTool(SaptivaTool[str]):
            name = "my_tool"
            description = "Does something useful"

            async def _arun(self, query: str) -> str:
                return f"Result for: {query}"
    """

    name: str = "saptiva_tool"
    description: str = "A Saptiva tool"

    @abstractmethod
    async def _arun(self, *args, **kwargs) -> T:
        """
        Async implementation of the tool logic.
        Override this method in subclasses.
        """
        pass

    def _run(self, *args, **kwargs) -> T:
        """
        Sync implementation - by default raises NotImplementedError.
        Override if sync execution is needed.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support synchronous execution. "
            "Use the async method instead."
        )

    async def __call__(self, *args, **kwargs) -> T:
        """Allow the tool to be called directly."""
        return await self._arun(*args, **kwargs)

    def to_function_tool(self) -> AutoGenFunctionTool:
        """
        Convert this SaptivaTool to an AutoGen FunctionTool.
        This enables seamless integration with AutoGen agents.
        """
        return AutoGenFunctionTool(
            func=self._arun,
            description=self.description,
            name=self.name
        )


def create_saptiva_tool(
    func: Callable[..., Awaitable[T]],
    name: Optional[str] = None,
    description: Optional[str] = None
) -> AutoGenFunctionTool:
    """
    Factory function to create a Saptiva-compatible tool from an async function.

    This is the recommended way to create tools from existing async functions,
    as it wraps them in AutoGen's FunctionTool with proper type inference.

    Args:
        func: An async function to wrap as a tool
        name: Optional custom name (defaults to function name)
        description: Optional description (defaults to function docstring)

    Returns:
        AutoGenFunctionTool: A tool ready for use with AutoGen agents

    Example:
        async def search_web(query: str) -> str:
            '''Search the web for information.'''
            return f"Results for: {query}"

        tool = create_saptiva_tool(search_web)
    """
    tool_name = name or func.__name__
    tool_description = description or func.__doc__ or f"Tool: {tool_name}"

    return AutoGenFunctionTool(
        func=func,
        description=tool_description,
        name=tool_name
    )
