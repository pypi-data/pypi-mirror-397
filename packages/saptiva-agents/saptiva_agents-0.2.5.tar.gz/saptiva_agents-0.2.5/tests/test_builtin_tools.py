import base64
import os
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from saptiva_agents.tools import tools as builtin_tools


def _make_response(status: int, json_data=None, text_data: str = ""):
    resp = AsyncMock()
    resp.status = status
    if json_data is not None:
        resp.json = AsyncMock(return_value=json_data)
    resp.text = AsyncMock(return_value=text_data)
    resp.statusText = text_data
    return resp


def _make_cm(resp):
    return AsyncMock(__aenter__=AsyncMock(return_value=resp), __aexit__=AsyncMock(return_value=None))


def _make_session(get_side_effect=None, post_side_effect=None, headers=None):
    session = MagicMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    if get_side_effect is not None:
        session.get = MagicMock(side_effect=get_side_effect)
    if post_side_effect is not None:
        session.post = MagicMock(side_effect=post_side_effect)
    return session


class TestBasicTools(unittest.IsolatedAsyncioTestCase):
    async def test_get_weather(self):
        result = await builtin_tools.get_weather("Tokyo")
        self.assertIn("Tokyo", result)

    @patch("saptiva_agents.tools.tools.aiohttp.ClientSession")
    async def test_wikipedia_search_paths(self, mock_session_class):
        # 200 OK
        resp_ok = _make_response(200, {"title": "Python", "extract": "Lang"})
        session = _make_session(get_side_effect=[_make_cm(resp_ok)])
        mock_session_class.return_value = session
        out = await builtin_tools.wikipedia_search("Python")
        self.assertIn("Title: Python", out)

        # 404 Not Found
        resp_404 = _make_response(404)
        session = _make_session(get_side_effect=[_make_cm(resp_404)])
        mock_session_class.return_value = session
        out = await builtin_tools.wikipedia_search("nope")
        self.assertIn("No se encontró", out)

        # Other status
        resp_500 = _make_response(500)
        session = _make_session(get_side_effect=[_make_cm(resp_500)])
        mock_session_class.return_value = session
        out = await builtin_tools.wikipedia_search("err")
        self.assertIn("Error al consultar Wikipedia", out)

        # Exception branch
        session = _make_session(get_side_effect=Exception("boom"))
        mock_session_class.return_value = session
        out = await builtin_tools.wikipedia_search("boom")
        self.assertIn("Error:", out)


class TestNetworkTools(unittest.IsolatedAsyncioTestCase):
    @patch("saptiva_agents.tools.tools.aiohttp.ClientSession")
    async def test_upload_csv_success_and_errors(self, mock_session_class):
        content = base64.b64encode(b"a,b\n1,2").decode()

        # Success
        resp_ok = _make_response(200, {"ok": True})
        session = _make_session(post_side_effect=[_make_cm(resp_ok)])
        mock_session_class.return_value = session
        out = await builtin_tools.upload_csv("id", content)
        self.assertEqual(out, {"ok": True})

        # Non-200 raises
        resp_bad = _make_response(500, text_data="fail")
        session = _make_session(post_side_effect=[_make_cm(resp_bad)])
        mock_session_class.return_value = session
        with self.assertRaises(Exception):
            await builtin_tools.upload_csv("id", content)

        # Error field raises
        resp_err = _make_response(200, {"error": "bad"})
        session = _make_session(post_side_effect=[_make_cm(resp_err)])
        mock_session_class.return_value = session
        with self.assertRaises(Exception):
            await builtin_tools.upload_csv("id", content)

    @patch("saptiva_agents.tools.tools.asyncio.sleep", new_callable=AsyncMock)
    @patch("saptiva_agents.tools.tools.aiohttp.ClientSession")
    async def test_consultar_cfdi_success_and_retry_fail(self, mock_session_class, mock_sleep):
        with self.assertRaises(ValueError):
            await builtin_tools.consultar_cfdi("")

        resp_ok = _make_response(200, {"uuid": "123"})
        session = _make_session(post_side_effect=[_make_cm(resp_ok)])
        mock_session_class.return_value = session
        out = await builtin_tools.consultar_cfdi("http://cfdi")
        self.assertEqual(out, {"uuid": "123"})

        # Fail after retries
        resp_fail = _make_response(500)
        post_effects = [_make_cm(resp_fail) for _ in range(10)]
        session = _make_session(post_side_effect=post_effects)
        mock_session_class.return_value = session
        with self.assertRaises(Exception):
            await builtin_tools.consultar_cfdi("http://cfdi")
        self.assertGreaterEqual(mock_sleep.await_count, 1)

    @patch("saptiva_agents.tools.tools.aiohttp.ClientSession")
    async def test_curp_and_sat_tools(self, mock_session_class):
        with self.assertRaises(ValueError):
            await builtin_tools.consultar_curp_post("")
        with self.assertRaises(ValueError):
            await builtin_tools.consultar_curp_get("")
        with self.assertRaises(ValueError):
            await builtin_tools.get_verify_sat("")

        # consultar_curp_post success then json error
        resp_ok = _make_response(200, {"id": "curp"})
        resp_err = _make_response(200, {"error": "bad"})
        session = _make_session(post_side_effect=[_make_cm(resp_ok), _make_cm(resp_err)])
        mock_session_class.return_value = session
        out = await builtin_tools.consultar_curp_post("CURP")
        self.assertEqual(out, {"id": "curp"})
        with self.assertRaises(Exception):
            await builtin_tools.consultar_curp_post("CURP")

        # consultar_curp_get non-200
        resp_non200 = _make_response(404)
        session = _make_session(get_side_effect=[_make_cm(resp_non200)])
        mock_session_class.return_value = session
        with self.assertRaises(Exception):
            await builtin_tools.consultar_curp_get("ID")

        # get_verify_sat success
        resp_sat_ok = _make_response(200, {"sat": True})
        session = _make_session(post_side_effect=[_make_cm(resp_sat_ok)])
        mock_session_class.return_value = session
        out = await builtin_tools.get_verify_sat("http://sat")
        self.assertEqual(out, {"sat": True})

    @patch("saptiva_agents.tools.tools.aiohttp.ClientSession")
    async def test_obtener_texto_en_documento_and_bot_query(self, mock_session_class):
        with self.assertRaises(ValueError):
            await builtin_tools.obtener_texto_en_documento("", "abc")

        os.environ["SAPTIVA_API_KEY"] = "test-key"
        document_b64 = base64.b64encode(b"pdf-bytes").decode()

        # obtener_texto_en_documento success then non-200
        resp_ok = _make_response(200, {"text": "ok"})
        resp_bad = _make_response(500)
        session = _make_session(post_side_effect=[_make_cm(resp_ok), _make_cm(resp_bad)])
        mock_session_class.return_value = session
        out = await builtin_tools.obtener_texto_en_documento("pdf", document_b64)
        self.assertEqual(out, {"text": "ok"})
        with self.assertRaises(Exception):
            await builtin_tools.obtener_texto_en_documento("pdf", document_b64)

        with self.assertRaises(ValueError):
            await builtin_tools.saptiva_bot_query("")

        # saptiva_bot_query success then failure
        resp_bot_ok = _make_response(200, {"answer": "hi"})
        resp_bot_bad = _make_response(500, text_data="bad")
        session = _make_session(post_side_effect=[_make_cm(resp_bot_ok), _make_cm(resp_bot_bad)])
        mock_session_class.return_value = session
        out = await builtin_tools.saptiva_bot_query("hola")
        self.assertEqual(out, {"answer": "hi"})
        with self.assertRaises(Exception):
            await builtin_tools.saptiva_bot_query("hola")
