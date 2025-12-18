import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from starlette.exceptions import HTTPException

from saptiva_agents import (
    DEFAULT_LANG,
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_P,
    SAPTIVA_BASE_URL,
    SAPTIVA_LEGACY,
    SAPTIVA_MULTIMODAL,
    SAPTIVA_OPS,
    SAPTIVA_OCR,
)
from saptiva_agents.base._classes import (
    SaptivaAIBase,
    SaptivaAIChatCompletionClient,
    SaptivaAgentsFramework,
)
from saptiva_agents.models.models import Message, RequestData


class TestSaptivaClients(unittest.TestCase):
    def test_base_requires_api_key(self):
        with self.assertRaises(HTTPException):
            SaptivaAIBase(model="x")

    @patch("saptiva_agents.base._classes.OpenAIChatCompletionClient.__init__", return_value=None)
    def test_base_sets_defaults(self, mock_init):
        SaptivaAIBase(api_key="k", model="m")
        kwargs = mock_init.call_args.kwargs
        self.assertEqual(kwargs["lang"], DEFAULT_LANG)
        self.assertEqual(kwargs["temperature"], DEFAULT_TEMPERATURE)
        self.assertEqual(kwargs["top_p"], DEFAULT_TOP_P)

    @patch("saptiva_agents.base._classes.SaptivaAIBase.__init__", return_value=None)
    def test_chat_client_defaults(self, mock_base_init):
        SaptivaAIChatCompletionClient(api_key="k", model=SAPTIVA_LEGACY)
        kwargs = mock_base_init.call_args.kwargs
        self.assertEqual(kwargs["base_url"], SAPTIVA_BASE_URL)
        self.assertIn("guard", kwargs["extra_body"])


class TestFrameworkLogic(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.data = RequestData(
            messages=[Message(role="user", content="hi")],
            model=SAPTIVA_OPS,
            tools=[],
        )
        self.framework = SaptivaAgentsFramework(self.data)

    def test_get_saptiva_client_routing(self):
        with patch.object(self.framework, "_get_saptiva_chat_completion_client", return_value="ops") as mock_get:
            self.framework.multimodal = False
            self.framework.model = SAPTIVA_OPS
            self.assertEqual(self.framework._get_saptiva_client(), "ops")
            mock_get.assert_called_with(model=SAPTIVA_OPS)

        with patch.object(self.framework, "_get_saptiva_chat_completion_client", return_value="legacy"):
            self.framework.multimodal = False
            self.framework.model = SAPTIVA_LEGACY
            self.assertEqual(self.framework._get_saptiva_client(), "legacy")

        with patch.object(self.framework, "_get_saptiva_chat_completion_client", return_value="mm"):
            self.framework.multimodal = True
            self.framework.model = SAPTIVA_MULTIMODAL
            self.assertEqual(self.framework._get_saptiva_client(), "mm")

        self.framework.multimodal = True
        self.framework.model = SAPTIVA_OCR
        self.assertIsNone(self.framework._get_saptiva_client())

    def test_get_saptiva_multimodal_client_sets_model(self):
        self.framework.model = SAPTIVA_OCR
        with patch.object(self.framework, "_get_saptiva_client", return_value="mm") as mock_get:
            out = self.framework._get_saptiva_multimodal_client()
            self.assertTrue(self.framework.multimodal)
            self.assertEqual(out, "mm")
            mock_get.assert_called_once()

        self.framework.model = "Unknown"
        with patch.object(self.framework, "_get_saptiva_client", return_value="forced"):
            out = self.framework._get_saptiva_multimodal_client()
            self.assertEqual(self.framework.model, SAPTIVA_MULTIMODAL)
            self.assertEqual(out, "forced")

    @patch("saptiva_agents.base._classes.get_messages")
    async def test_run_happy_path(self, mock_get_messages):
        user = Message(role="user", content="hola")
        system = Message(role="system", content="sys")
        mock_get_messages.return_value = (user, system)

        self.framework._get_saptiva_client = MagicMock(return_value="client")
        self.framework._get_assistant_agent_model = MagicMock(return_value=MagicMock(tools=[]))
        self.framework._get_agent = MagicMock(return_value=MagicMock())
        self.framework._get_agent_response = AsyncMock(return_value="ok")

        out = await self.framework.run()
        self.assertEqual(out, "ok")

    @patch("saptiva_agents.base._classes.get_messages_with_image_urls")
    @patch("saptiva_agents.base._classes.extract_image_values", return_value=["x"])
    async def test_run_multimodal_happy_path(self, mock_extract, mock_get_msgs):
        user = Message(role="user", content=[{"text": "hola"}, {"type": "image_path"}])
        system = Message(role="system", content="sys")
        mock_get_msgs.return_value = (user, system)

        self.framework._get_saptiva_multimodal_client = MagicMock(return_value="client")
        self.framework._get_assistant_agent_model = MagicMock(return_value=MagicMock(tools=[]))
        self.framework._get_agent = MagicMock(return_value=MagicMock())
        self.framework._get_agent_response = AsyncMock(return_value="ok-mm")

        out = await self.framework.run_multimodal()
        self.assertEqual(out, "ok-mm")

    @patch("saptiva_agents.base._classes.MultiModalMessage")
    @patch("saptiva_agents.base._classes.Image.from_pil", return_value="img")
    @patch("saptiva_agents.base._classes.PILImage.open", return_value=MagicMock())
    @patch("saptiva_agents.base._classes.requests.get")
    async def test_generate_image_message_url_branch(
        self, mock_get, _mock_open, _mock_from_pil, mock_mm_message
    ):
        mock_get.return_value = MagicMock(status_code=200, content=b"fake")
        self.framework.user_message = Message(role="user", content=[{"text": "hola"}])
        messages = await self.framework._generate_image_message(["http://x"])
        self.assertEqual(len(messages), 1)
        mock_mm_message.assert_called_once()

    @patch("saptiva_agents.base._classes.MultiModalMessage")
    @patch("saptiva_agents.base._classes.Image.from_file", return_value="img")
    async def test_generate_image_message_path_and_missing(
        self, _mock_from_file, mock_mm_message
    ):
        self.framework.user_message = Message(role="user", content=[{"text": "hola"}])
        with patch("saptiva_agents.base._classes.os.path.exists", return_value=True):
            messages = await self.framework._generate_image_message(["/tmp/x.png"])
            self.assertEqual(len(messages), 1)
            mock_mm_message.assert_called()

        with patch("saptiva_agents.base._classes.os.path.exists", return_value=False):
            with self.assertRaises(HTTPException):
                await self.framework._generate_image_message(["/tmp/nope.png"])

    async def test_get_agent_response_uses_text_message(self):
        self.framework.user_message = Message(role="user", content="hola")
        self.framework.agent = MagicMock()
        self.framework.agent.on_messages = AsyncMock(
            return_value=MagicMock(chat_message=MagicMock(content="resp"))
        )
        out = await self.framework._get_agent_response()
        self.assertEqual(out, "resp")
