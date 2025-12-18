import types
import unittest
from unittest.mock import MagicMock, patch

from saptiva_agents.teams.research_team import DeepResearchTeamConfig, create_deep_research_team


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


class TestDeepResearchTeamCreation(unittest.IsolatedAsyncioTestCase):
    @patch("saptiva_agents.teams.research_team.SelectorGroupChat", new=FakeTeam)
    @patch(
        "saptiva_agents.teams.research_team.AssistantAgent",
        side_effect=lambda *args, **kwargs: FakeAgent(**kwargs),
    )
    @patch("saptiva_agents.teams.research_team.SaptivaAIChatCompletionClient")
    async def test_team_structure(self, mock_client_class, _mock_agent):
        mock_client_class.return_value = MagicMock(extra_kwargs={"api_key": "k"})

        base_client = MagicMock(extra_kwargs={"api_key": "k"})
        # Disable orchestration to get just the team (backwards compatibility test)
        config = DeepResearchTeamConfig(
            max_turns=5,
            search_base_url="https://searx.local",
            enable_orchestration=False,
        )

        team = await create_deep_research_team(base_client, config=config)
        self.assertEqual(len(team._participants), 5)
        names = [p.name for p in team._participants]
        self.assertIn("LeadResearcher", names)
        self.assertIn("WebSearcher", names)
        self.assertIn("WebReader", names)
        self.assertIn("Synthesizer", names)
        self.assertIn("Critic", names)
        self.assertEqual(team._max_turns, 5)

