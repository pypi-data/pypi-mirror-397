from typing import Dict

from autogen_core.models import ModelInfo, ModelFamily

from saptiva_agents.tools import (
    get_weather,
    wikipedia_search,
    wikipedia_search_native,
    WikipediaSearchTool,
    WebSearchTool,
    web_search,
    WebReadTool,
    read_page,
    upload_csv,
    saptiva_bot_query,
    obtener_texto_en_documento,
    get_verify_sat,
    consultar_curp_get,
    consultar_curp_post,
    consultar_cfdi
)

# OFFICIAL TOOLING OPTIONS - All native Python/Pydantic based (no LangChain)
TOOLS = {
    # Wikipedia search tools (native implementations)
    WikipediaSearchTool.__name__: WikipediaSearchTool,  # Class-based tool with fallback search
    wikipedia_search.__name__: wikipedia_search,         # Simple async function
    wikipedia_search_native.__name__: wikipedia_search_native,  # Enhanced native function
    # Web search / page read tools
    WebSearchTool.__name__: WebSearchTool,
    web_search.__name__: web_search,
    WebReadTool.__name__: WebReadTool,
    read_page.__name__: read_page,
    # Utility tools
    get_weather.__name__: get_weather,
    # Saptiva service tools
    upload_csv.__name__: upload_csv,
    saptiva_bot_query.__name__: saptiva_bot_query,
    obtener_texto_en_documento.__name__: obtener_texto_en_documento,
    get_verify_sat.__name__: get_verify_sat,
    consultar_curp_get.__name__: consultar_curp_get,
    consultar_curp_post.__name__: consultar_curp_post,
    consultar_cfdi.__name__: consultar_cfdi,
}

MODEL_INFO: Dict[str, ModelInfo] = {
    # qwen3-it
    "Saptiva Turbo": {
        "vision": False,
        "function_calling": True,
        "json_output": True,
        "family": ModelFamily.UNKNOWN,
        "structured_output": True,
        "multiple_system_messages": True
    },
    # gemma3
    "Saptiva Multimodal": {
        "vision": True,
        "function_calling": True,
        "json_output": True,
        "family": ModelFamily.UNKNOWN,
        "structured_output": True,
        "multiple_system_messages": True
    },
    # deepseek-coder
    "Saptiva Coder": {
        "vision": False,
        "function_calling": False,
        "json_output": True,
        "family": ModelFamily.UNKNOWN,
        "structured_output": True,
        "multiple_system_messages": True
    },
    # llama3.3
    "Saptiva Legacy": {
        "vision": False,
        "function_calling": True,
        "json_output": True,
        "family": ModelFamily.UNKNOWN,
        "structured_output": True,
        "multiple_system_messages": True
    },
    # GPT-OSS 20B
    "Saptiva Ops": {
        "vision": False,
        "function_calling": True,
        "json_output": True,
        "family": ModelFamily.UNKNOWN,
        "structured_output": True,
        "multiple_system_messages": True
    },
    # qwen3-tk
    "Saptiva Cortex": {
        "vision": False,
        "function_calling": True,
        "json_output": True,
        "family": ModelFamily.UNKNOWN,
        "structured_output": True,
        "multiple_system_messages": True
    },
    # llama-guard
    "Saptiva Guard": {
        "vision": False,
        "function_calling": True,
        "json_output": True,
        "family": ModelFamily.UNKNOWN,
        "structured_output": True,
        "multiple_system_messages": True
    },
    # Nanonets
    "Saptiva OCR": {
        "vision": True,
        "function_calling": False,
        "json_output": True,
        "family": ModelFamily.UNKNOWN,
        "structured_output": True,
        "multiple_system_messages": True
    },
    "GPT-OSS 120B": {
        "vision": False,
        "function_calling": True,
        "json_output": True,
        "family": ModelFamily.UNKNOWN,
        "structured_output": True,
        "multiple_system_messages": True
    },
    "GPT-OSS 20B": {
        "vision": False,
        "function_calling": True,
        "json_output": True,
        "family": ModelFamily.UNKNOWN,
        "structured_output": True,
        "multiple_system_messages": True
    },
    "gemma2": {
        "vision": False,
        "function_calling": False,
        "json_output": True,
        "family": ModelFamily.UNKNOWN,
        "structured_output": True,
        "multiple_system_messages": True
    },
    "gemma3": {
        "vision": True,
        "function_calling": True,
        "json_output": True,
        "family": ModelFamily.UNKNOWN,
        "structured_output": True,
        "multiple_system_messages": True
    },
    "deepseek-coder-v2": {
        "vision": False,
        "function_calling": False,
        "json_output": True,
        "family": ModelFamily.UNKNOWN,
        "structured_output": True,
        "multiple_system_messages": True
    },
    "llama3.3": {
        "vision": False,
        "function_calling": True,
        "json_output": True,
        "family": ModelFamily.UNKNOWN,
        "structured_output": True,
        "multiple_system_messages": True
    },
    "qwen2.5": {
        "vision": False,
        "function_calling": True,
        "json_output": True,
        "family": ModelFamily.UNKNOWN,
        "structured_output": True,
        "multiple_system_messages": True
    },
    "qwen3-it": {
        "vision": False,
        "function_calling": True,
        "json_output": True,
        "family": ModelFamily.UNKNOWN,
        "structured_output": True,
        "multiple_system_messages": True
    },
    "qwen3-tk": {
        "vision": False,
        "function_calling": True,
        "json_output": True,
        "family": ModelFamily.UNKNOWN,
        "structured_output": True,
        "multiple_system_messages": True
    },
    "qwen3": {
        "vision": False,
        "function_calling": True,
        "json_output": True,
        "family": ModelFamily.UNKNOWN,
        "structured_output": True,
        "multiple_system_messages": True
    },
    "llama-guard3": {
        "vision": False,
        "function_calling": True,
        "json_output": True,
        "family": ModelFamily.UNKNOWN,
        "structured_output": True,
        "multiple_system_messages": True
    },
    "Nanonets-OCR-s": {
        "vision": True,
        "function_calling": False,
        "json_output": True,
        "family": ModelFamily.UNKNOWN,
        "structured_output": True,
        "multiple_system_messages": True
    },
    "gpt-oss": {
        "vision": False,
        "function_calling": True,
        "json_output": True,
        "family": ModelFamily.UNKNOWN,
        "structured_output": True,
        "multiple_system_messages": True
    },
}
