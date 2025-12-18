import unittest

from starlette.exceptions import HTTPException

from saptiva_agents import SYSTEM_PROMPT, DEFAULT_MODEL_INFO, DEFAULT_EMBED_MODELS
from saptiva_agents._utils import (
    get_messages,
    get_messages_with_image_urls,
    extract_image_values,
    get_tools,
    resolve_model_class,
    get_model_info,
    get_text_model_list,
    get_multimodal_model_list,
)
from saptiva_agents.models.models import Message


class TestUtilsMessages(unittest.TestCase):
    def test_get_messages_success_and_default_system(self):
        user = Message(role="user", content="hola")
        system = Message(role="system", content="sys")
        u, s = get_messages([system, user])
        self.assertEqual(u.content, "hola")
        self.assertEqual(s.content, "sys")

        u2, s2 = get_messages([user])
        self.assertEqual(u2.role, "user")
        self.assertEqual(s2.role, "system")
        self.assertEqual(s2.content, SYSTEM_PROMPT)

    def test_get_messages_raises_without_user(self):
        with self.assertRaises(HTTPException):
            get_messages([Message(role="system", content="sys")])

    def test_get_messages_with_image_urls_validation(self):
        user = Message(
            role="user",
            content=[{"text": "hola"}, {"type": "image_url", "image_url": {"url": "http://x"}}],
        )
        u, s = get_messages_with_image_urls([user])
        self.assertEqual(u.role, "user")
        self.assertEqual(s.content, SYSTEM_PROMPT)

        bad_user = Message(role="user", content="not-a-list")
        with self.assertRaises(HTTPException):
            get_messages_with_image_urls([bad_user])


class TestUtilsImages(unittest.TestCase):
    def test_extract_image_values(self):
        values = extract_image_values(
            [
                {"type": "image_url", "image_url": {"url": "http://a"}},
                {"type": "image_path", "image_path": {"path": "/tmp/x.png"}},
            ]
        )
        self.assertEqual(values, ["http://a", "/tmp/x.png"])

        with self.assertRaises(HTTPException):
            extract_image_values([{"type": "text", "text": "hi"}])


class TestUtilsToolsAndModels(unittest.TestCase):
    def test_get_tools_and_unknown_tool(self):
        tools = get_tools(["get_weather"])
        self.assertEqual(len(tools), 1)
        self.assertTrue(callable(tools[0]))

        with self.assertRaises(HTTPException):
            get_tools(["no_existe"])

    def test_model_info_resolution(self):
        self.assertEqual(resolve_model_class("qwen3-it:30b"), "qwen3-it")

        info = get_model_info("Saptiva Turbo")
        self.assertIn("function_calling", info)

        # Unknown model returns default
        default_info = get_model_info("Unknown Model")
        self.assertEqual(default_info, DEFAULT_MODEL_INFO)

        # Embed models raise explicit KeyError
        with self.assertRaises(KeyError):
            get_model_info(DEFAULT_EMBED_MODELS[0])

    def test_model_lists(self):
        self.assertTrue(len(get_text_model_list()) > 0)
        self.assertTrue(len(get_multimodal_model_list()) > 0)

