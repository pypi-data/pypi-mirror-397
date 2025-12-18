"""
Wikipedia Search Tool - Native implementation without LangChain.

This module provides Wikipedia search functionality using:
- Native aiohttp for async HTTP requests
- Pydantic for input/output validation
- Direct Wikipedia API integration

Replaces the legacy langchain_community.tools.WikipediaQueryRun
"""

import urllib.parse
from typing import Optional
from pydantic import BaseModel, Field

import aiohttp

from saptiva_agents import DEFAULT_LANG, CONTENT_CHARS_MAX
from saptiva_agents.tools._saptiva_tool import SaptivaTool, ToolOutput

# User-Agent header required by Wikipedia API
WIKIPEDIA_HEADERS = {
    "User-Agent": "SaptivaAgents/0.2.5 (https://saptiva.com; contact@saptiva.com) aiohttp"
}


class WikipediaSearchInput(BaseModel):
    """Input schema for Wikipedia search."""
    query: str = Field(..., description="The search query for Wikipedia")
    lang: str = Field(default=DEFAULT_LANG, description="Wikipedia language code (e.g., 'es', 'en')")
    max_chars: int = Field(default=CONTENT_CHARS_MAX, description="Maximum characters to return")


class WikipediaSearchOutput(ToolOutput):
    """Output schema for Wikipedia search results."""
    title: Optional[str] = Field(default=None, description="Article title")
    summary: Optional[str] = Field(default=None, description="Article summary/extract")
    url: Optional[str] = Field(default=None, description="Wikipedia article URL")


class WikipediaSearchTool(SaptivaTool[str]):
    """
    Native Wikipedia search tool using Wikipedia REST API.

    This replaces the LangChain WikipediaQueryRun with a native implementation
    that provides better async support and Pydantic validation.

    Example:
        tool = WikipediaSearchTool()
        result = await tool("Python programming language")
    """

    name: str = "WikipediaSearchTool"
    description: str = "Busca información en Wikipedia sobre un tema específico. Retorna título y resumen del artículo."

    def __init__(self, lang: str = DEFAULT_LANG, max_chars: int = CONTENT_CHARS_MAX):
        self.lang = lang
        self.max_chars = max_chars

    async def _arun(self, query: str) -> str:
        """
        Execute Wikipedia search asynchronously.

        Args:
            query: The search term to look up on Wikipedia

        Returns:
            str: Formatted result with title and summary, or error message
        """
        try:
            # Use Wikipedia REST API for summary
            encoded_query = urllib.parse.quote(query)
            url = f"https://{self.lang}.wikipedia.org/api/rest_v1/page/summary/{encoded_query}"

            async with aiohttp.ClientSession(headers=WIKIPEDIA_HEADERS) as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        title = data.get("title", "")
                        extract = data.get("extract", "")

                        # Truncate if needed
                        if len(extract) > self.max_chars:
                            extract = extract[:self.max_chars] + "..."

                        return f"Título: {title}\nResumen: {extract}"

                    elif response.status == 404:
                        # Try search API as fallback
                        return await self._search_fallback(query)

                    else:
                        return f"Error al consultar Wikipedia: código {response.status}"

        except aiohttp.ClientError as e:
            return f"Error de conexión con Wikipedia: {str(e)}"
        except Exception as e:
            return f"Error inesperado: {str(e)}"

    async def _search_fallback(self, query: str) -> str:
        """
        Fallback search using Wikipedia search API when direct lookup fails.
        """
        try:
            search_url = (
                f"https://{self.lang}.wikipedia.org/w/api.php?"
                f"action=query&list=search&srsearch={urllib.parse.quote(query)}"
                f"&format=json&srlimit=3"
            )

            async with aiohttp.ClientSession(headers=WIKIPEDIA_HEADERS) as session:
                async with session.get(search_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = data.get("query", {}).get("search", [])

                        if results:
                            # Get the first result's page
                            first_title = results[0].get("title", "")
                            return await self._get_page_summary(first_title)
                        else:
                            return "No se encontró información en Wikipedia para esa consulta."
                    else:
                        return "No se encontró información en Wikipedia para esa consulta."

        except Exception as e:
            return f"Error en búsqueda alternativa: {str(e)}"

    async def _get_page_summary(self, title: str) -> str:
        """Get summary for a specific Wikipedia page title."""
        try:
            encoded_title = urllib.parse.quote(title)
            url = f"https://{self.lang}.wikipedia.org/api/rest_v1/page/summary/{encoded_title}"

            async with aiohttp.ClientSession(headers=WIKIPEDIA_HEADERS) as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        title = data.get("title", "")
                        extract = data.get("extract", "")

                        if len(extract) > self.max_chars:
                            extract = extract[:self.max_chars] + "..."

                        return f"Título: {title}\nResumen: {extract}"
                    else:
                        return "No se pudo obtener el resumen del artículo."

        except Exception as e:
            return f"Error obteniendo resumen: {str(e)}"


# Convenience function for direct use (matches existing wikipedia_search signature)
async def wikipedia_search_native(query: str, lang: str = DEFAULT_LANG, max_chars: int = CONTENT_CHARS_MAX) -> str:
    """
    Native Wikipedia search function.

    This is a drop-in replacement for the legacy wikipedia_search function
    with additional features like fallback search.

    Args:
        query: Search term
        lang: Wikipedia language code
        max_chars: Maximum characters to return

    Returns:
        str: Search result or error message
    """
    tool = WikipediaSearchTool(lang=lang, max_chars=max_chars)
    return await tool._arun(query)
