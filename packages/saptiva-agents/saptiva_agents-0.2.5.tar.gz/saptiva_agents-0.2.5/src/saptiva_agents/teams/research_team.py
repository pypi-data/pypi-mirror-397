"""
Deep Research Team (v2) - robust multi-agent research pattern.

Implements a Plan‑Execute‑Verify workflow using standard market‑proven patterns:
- Supervisor/Planner (Plan)
- WebSearcher + WebReader (Execute)
- Synthesizer (Synthesize)
- Critic/Verifier (Verify)

The team is built on AutoGen SelectorGroupChat for dynamic speaker selection.

Usage with orchestration:
    from saptiva_agents.teams import create_deep_research_team, DeepResearchTeamConfig

    config = DeepResearchTeamConfig(
        team_timeout_s=300,
        use_global_cache=True,
        use_global_rate_limiter=True,
    )
    team, orchestrator = await create_deep_research_team(client, config)

    # Run with automatic timeout and context management
    result = await orchestrator.run("Research quantum computing")
"""

from __future__ import annotations

import logging
from typing import Any, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

from saptiva_agents import (
    DEFAULT_LANG,
    SAPTIVA_CORTEX,
    SAPTIVA_OPS,
    SAPTIVA_TURBO,
)
from saptiva_agents.agents import AssistantAgent
from saptiva_agents.base import SaptivaAIChatCompletionClient
from saptiva_agents.conditions import TextMentionTermination
from saptiva_agents.core import ROOT_LOGGER_NAME
from saptiva_agents.teams._group_chat import SelectorGroupChat
from saptiva_agents.teams._research_orchestrator import (
    OrchestratorConfig,
    ResearchOrchestrator,
)
from saptiva_agents.tools._web_fetch import WebReadTool
from saptiva_agents.tools._web_search import WebSearchTool


logger = logging.getLogger(ROOT_LOGGER_NAME)


class DeepResearchTeamConfig(BaseModel):
    """Configuration for the Deep Research Team."""

    planner_model: str = Field(default=SAPTIVA_CORTEX, description="Model for supervisor/planner")
    searcher_model: str = Field(default=SAPTIVA_TURBO, description="Model for web searcher")
    reader_model: str = Field(default=SAPTIVA_OPS, description="Model for web reader/extractor")
    synthesizer_model: str = Field(default=SAPTIVA_CORTEX, description="Model for synthesizer")
    critic_model: str = Field(default=SAPTIVA_OPS, description="Model for critic/verifier")

    max_turns: int = Field(default=12, ge=3, le=50, description="Max turns for the team")
    max_results_per_query: int = Field(default=5, ge=1, le=20, description="Search results per query")
    min_sources: int = Field(default=3, ge=1, le=10, description="Minimum distinct sources before final synthesis")
    lang: str = Field(default=DEFAULT_LANG, description="Language for search/reading")
    safe_search: bool = Field(default=True, description="Enable safe search")
    search_provider: str = Field(
        default="searxng",
        description="Search provider to use: 'searxng' (self-hosted) or 'tavily' (SaaS).",
    )
    search_base_url: Optional[str] = Field(
        default=None,
        description="Base URL for search provider (SearXNG) or custom Tavily endpoint.",
    )
    search_api_key: Optional[str] = Field(default=None, description="API key for the chosen provider")

    # Network robustness (search)
    search_timeout_s: float = Field(default=10.0, ge=1.0, le=60.0, description="HTTP timeout for search")
    search_max_retries: int = Field(default=2, ge=0, le=10, description="Retries for search on 429/5xx")
    search_backoff_base_s: float = Field(default=0.4, ge=0.0, le=10.0, description="Base backoff for search")
    search_backoff_max_s: float = Field(default=4.0, ge=0.0, le=60.0, description="Max backoff for search")
    search_min_interval_s: float = Field(default=0.0, ge=0.0, le=10.0, description="Min seconds between searches")

    # Network robustness (read)
    read_timeout_s: float = Field(default=15.0, ge=1.0, le=120.0, description="HTTP timeout for page reads")
    read_max_chars: int = Field(default=6000, ge=500, le=50000, description="Max chars per page")
    read_extractor: str = Field(
        default="simple",
        description="Page extractor: 'simple' (regex) or 'trafilatura' (if installed).",
    )
    read_max_retries: int = Field(default=2, ge=0, le=10, description="Retries for page reads on 429/5xx")
    read_backoff_base_s: float = Field(default=0.4, ge=0.0, le=10.0, description="Base backoff for page reads")
    read_backoff_max_s: float = Field(default=4.0, ge=0.0, le=60.0, description="Max backoff for page reads")
    read_min_interval_s: float = Field(default=0.0, ge=0.0, le=10.0, description="Min seconds between reads")

    # In-memory cache shared by tools inside a team
    cache_ttl_s: float = Field(default=300.0, ge=0.0, le=3600.0, description="Cache TTL for search/read")
    cache_max_entries: int = Field(default=128, ge=0, le=2048, description="Max cache entries per tool")

    # Global singletons (P1 improvement)
    use_global_cache: bool = Field(
        default=False,
        description="Use global singleton cache instead of per-tool instances",
    )
    use_global_rate_limiter: bool = Field(
        default=False,
        description="Use global singleton rate limiter with per-domain semaphores",
    )

    # Orchestration (P0/P2 improvement)
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
    enable_orchestration: bool = Field(
        default=True,
        description="Wrap team with ResearchOrchestrator for timeout and context management",
    )

    model_config = ConfigDict(extra="forbid")


async def create_deep_research_team(
    model_client: SaptivaAIChatCompletionClient,
    config: Optional[DeepResearchTeamConfig] = None,
) -> Union[SelectorGroupChat, tuple[SelectorGroupChat, ResearchOrchestrator]]:
    """
    Create a robust Deep Research Team.

    Args:
        model_client: Base model client (used only to inherit API key/base url).
        config: Optional DeepResearchTeamConfig overrides.

    Returns:
        If enable_orchestration=False: SelectorGroupChat team
        If enable_orchestration=True: tuple of (team, orchestrator)

    Example:
        # With orchestration (default)
        team, orchestrator = await create_deep_research_team(client)
        result = await orchestrator.run("Research topic")

        # Without orchestration
        config = DeepResearchTeamConfig(enable_orchestration=False)
        team = await create_deep_research_team(client, config)
        result = await team.run(task="Research topic")
    """
    config = config or DeepResearchTeamConfig()

    # Derive base kwargs from provided client when possible.
    base_kwargs: dict = {}
    if hasattr(model_client, "extra_kwargs") and isinstance(model_client.extra_kwargs, dict):
        base_kwargs = dict(model_client.extra_kwargs)
        # We recompute model/model_info per client.
        base_kwargs.pop("model", None)
        base_kwargs.pop("model_info", None)

    def _client_for(model_name: str) -> SaptivaAIChatCompletionClient:
        kwargs = dict(base_kwargs)
        kwargs["model"] = model_name
        # Avoid parallel tool calls when agents call tools sequentially.
        kwargs.setdefault("parallel_tool_calls", False)
        return SaptivaAIChatCompletionClient(**kwargs)

    planner_client = _client_for(config.planner_model)
    searcher_client = _client_for(config.searcher_model)
    reader_client = _client_for(config.reader_model)
    synthesizer_client = _client_for(config.synthesizer_model)
    critic_client = _client_for(config.critic_model)

    planner_prompt = f"""
Eres LeadResearcher y Supervisor de un equipo de investigación.
Tu objetivo es responder preguntas complejas con evidencia verificable.

Dispones de agentes especialistas:
- WebSearcher: ejecuta búsquedas web y devuelve URLs relevantes.
- WebReader: lee URLs y extrae notas con citas textuales.
- Synthesizer: redacta la respuesta final con referencias.
- Critic: revisa cobertura del plan y detecta huecos/alucinaciones.

Proceso estricto:
1. Genera un plan en JSON con subpreguntas y criterios de suficiencia.
2. Pide a WebSearcher queries concretas.
3. Selecciona URLs, pide a WebReader leerlas y traer notas con citas.
4. Cuando tengas al menos {config.min_sources} fuentes distintas, pide a Synthesizer un borrador.
5. Pide a Critic verificar borrador vs plan y evidencia.
Reglas de robustez:
- Si una llamada a web_search o read_page devuelve success=false (p.ej. HTTP 403/429), NO insistas en la misma URL.
  Descarta esa fuente y busca alternativas. Prioriza dominios sin bloqueo (blogs técnicos, docs oficiales, papers).
- Evita ciclos: no repitas la misma query/URL más de una vez salvo que el plan lo requiera.
6. Si Critic detecta huecos, repite búsqueda/lectura.
7. Devuelve respuesta final con citas numeradas [1], [2] y termina con "TERMINATE".
"""

    lead_researcher = AssistantAgent(
        name="LeadResearcher",
        description="Supervisor que planifica, coordina y entrega la respuesta final.",
        model_client=planner_client,
        system_message=planner_prompt,
    )

    search_tool = WebSearchTool(
        provider=config.search_provider,
        base_url=config.search_base_url,
        api_key=config.search_api_key,
        timeout_s=config.search_timeout_s,
        safe_search=config.safe_search,
        lang=config.lang,
        max_retries=config.search_max_retries,
        backoff_base_s=config.search_backoff_base_s,
        backoff_max_s=config.search_backoff_max_s,
        min_interval_s=config.search_min_interval_s,
        cache_ttl_s=config.cache_ttl_s,
        cache_max_entries=config.cache_max_entries,
        # Global singletons integration
        use_global_cache=config.use_global_cache,
        use_global_rate_limiter=config.use_global_rate_limiter,
    )

    async def _web_search(query: str, num_results: int = config.max_results_per_query):
        return await search_tool(
            query=query,
            num_results=num_results,
            lang=config.lang,
            safe_search=config.safe_search,
        )

    web_searcher = AssistantAgent(
        name="WebSearcher",
        description="Especialista en búsqueda web; solo usa web_search.",
        model_client=searcher_client,
        tools=[_web_search],
        system_message=(
            "Eres WebSearcher. Ejecuta búsquedas web usando la herramienta web_search. "
            "Devuelve resultados estructurados y no inventes URLs."
        ),
    )

    read_tool = WebReadTool(
        timeout_s=config.read_timeout_s,
        max_chars=config.read_max_chars,
        extractor=config.read_extractor,
        max_retries=config.read_max_retries,
        backoff_base_s=config.read_backoff_base_s,
        backoff_max_s=config.read_backoff_max_s,
        min_interval_s=config.read_min_interval_s,
        cache_ttl_s=config.cache_ttl_s,
        cache_max_entries=config.cache_max_entries,
        # Global singletons integration
        use_global_cache=config.use_global_cache,
        use_global_rate_limiter=config.use_global_rate_limiter,
    )

    async def _read_page(url: str):
        return await read_tool(url=url, max_chars=config.read_max_chars, extractor=config.read_extractor)

    web_reader = AssistantAgent(
        name="WebReader",
        description="Lee páginas web y extrae notas con citas.",
        model_client=reader_client,
        tools=[_read_page],
        system_message=(
            "Eres WebReader. Usa read_page para leer URLs. "
            "Si success=false, devuelve un JSON con url y error, y sugiere otra fuente. "
            "Si success=true, devuelve notas en JSON con campos: url, quote, note."
        ),
    )

    synthesizer = AssistantAgent(
        name="Synthesizer",
        description="Sintetiza notas en una respuesta coherente con citas.",
        model_client=synthesizer_client,
        system_message=(
            "Eres Synthesizer. Recibes notas con citas y redactas una respuesta clara, "
            "incluyendo referencias [n] vinculadas a las URLs proporcionadas."
        ),
    )

    critic = AssistantAgent(
        name="Critic",
        description="Audita la respuesta contra plan y evidencia.",
        model_client=critic_client,
        system_message=(
            "Eres Critic. Verifica que el borrador cubra el plan y esté soportado por citas. "
            "Si faltan fuentes o hay contradicciones, devuelve una lista de gaps y nuevas queries. "
            "Si todo es suficiente, responde solo 'OK'."
        ),
    )

    termination = TextMentionTermination("TERMINATE", sources=["LeadResearcher"])

    team = SelectorGroupChat(
        participants=[lead_researcher, web_searcher, web_reader, synthesizer, critic],
        model_client=planner_client,
        termination_condition=termination,
        max_turns=config.max_turns,
    )

    logger.info(
        "DeepResearchTeam v2 initialized max_turns=%d provider=%s extractor=%s "
        "cache_ttl_s=%.0f global_cache=%s global_rate_limiter=%s orchestration=%s",
        config.max_turns,
        config.search_provider,
        config.read_extractor,
        config.cache_ttl_s,
        config.use_global_cache,
        config.use_global_rate_limiter,
        config.enable_orchestration,
    )

    if not config.enable_orchestration:
        return team

    # Create orchestrator with timeout and context management
    orchestrator_config = OrchestratorConfig(
        team_timeout_s=config.team_timeout_s,
        min_sources_for_synthesis=config.min_sources_for_synthesis,
        max_iterations=config.max_iterations,
    )
    orchestrator = ResearchOrchestrator(team=team, config=orchestrator_config)

    return team, orchestrator
