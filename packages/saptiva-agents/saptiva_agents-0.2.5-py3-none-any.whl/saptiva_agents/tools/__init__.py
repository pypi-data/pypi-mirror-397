from autogen_core.tools import ToolSchema

from saptiva_agents.tools._agent import AgentTool
from saptiva_agents.tools._base import BaseTool, BaseToolWithState, Tool
from saptiva_agents.tools._function_tool import FunctionTool
from saptiva_agents.tools._saptiva_tool import (
    SaptivaTool,
    ToolInput,
    ToolOutput,
    create_saptiva_tool,
)
from saptiva_agents.tools._wikipedia import (
    WikipediaSearchTool,
    wikipedia_search_native,
)
from saptiva_agents.tools._web_search import (
    WebSearchTool,
    web_search,
)
from saptiva_agents.tools._web_fetch import (
    WebReadTool,
    read_page,
)
from saptiva_agents.tools.tools import (
    get_weather,
    wikipedia_search,
    upload_csv,
    saptiva_bot_query,
    obtener_texto_en_documento,
    get_verify_sat,
    consultar_curp_get,
    consultar_curp_post,
    consultar_cfdi,
)


__all__ = [
    # AutoGen base classes
    "FunctionTool",
    "Tool",
    "BaseTool",
    "BaseToolWithState",
    "ToolSchema",
    "AgentTool",
    # Saptiva native tool system (replaces LangChain)
    "SaptivaTool",
    "ToolInput",
    "ToolOutput",
    "create_saptiva_tool",
    # Wikipedia tools
    "WikipediaSearchTool",
    "wikipedia_search_native",
    "wikipedia_search",
    # Web search / fetch tools
    "WebSearchTool",
    "web_search",
    "WebReadTool",
    "read_page",
    # Saptiva service tools
    "get_weather",
    "get_verify_sat",
    "upload_csv",
    "saptiva_bot_query",
    "obtener_texto_en_documento",
    "consultar_curp_get",
    "consultar_curp_post",
    "consultar_cfdi",
]
