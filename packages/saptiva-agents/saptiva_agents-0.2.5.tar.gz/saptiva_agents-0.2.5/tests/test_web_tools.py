import os
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from saptiva_agents.tools._web_fetch import WebReadTool
from saptiva_agents.tools._web_search import WebSearchTool


def _make_response(status: int, json_data=None, text_data: str = "", url: str = "https://example.com"):
    resp = AsyncMock()
    resp.status = status
    resp.headers = {"Content-Type": "text/html"}
    resp.url = url
    if json_data is not None:
        resp.json = AsyncMock(return_value=json_data)
    resp.text = AsyncMock(return_value=text_data)
    return resp


def _make_cm(resp):
    return AsyncMock(__aenter__=AsyncMock(return_value=resp), __aexit__=AsyncMock(return_value=None))


def _make_session(get_side_effect=None, request_side_effect=None):
    session = MagicMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    if get_side_effect is not None:
        session.get = MagicMock(side_effect=get_side_effect)
    if request_side_effect is not None:
        session.request = MagicMock(side_effect=request_side_effect)
    return session


class TestWebSearchTool(unittest.IsolatedAsyncioTestCase):
    @patch("saptiva_agents.tools._web_search.aiohttp.ClientSession")
    async def test_web_search_success_and_dedupe(self, mock_session_class):
        data = {
            "results": [
                {"title": "A", "url": "http://a", "content": "sa", "engine": "x"},
                {"title": "B", "url": "http://b", "content": "sb", "engine": "x"},
                {"title": "A2", "url": "http://a", "content": "dup", "engine": "x"},
            ]
        }
        resp_ok = _make_response(200, json_data=data)
        session = _make_session(request_side_effect=[_make_cm(resp_ok)])
        mock_session_class.return_value = session

        tool = WebSearchTool(provider="searxng", base_url="https://searx.local")
        out = await tool._arun("test", num_results=5)
        self.assertTrue(out["success"])
        self.assertEqual(len(out["results"]), 2)

    @patch("saptiva_agents.tools._web_search.aiohttp.ClientSession")
    async def test_web_search_tavily_success(self, mock_session_class):
        data = {
            "results": [
                {"title": "A", "url": "http://a", "content": "sa", "score": 0.9},
            ]
        }
        resp_ok = _make_response(200, json_data=data)
        session = _make_session(request_side_effect=[_make_cm(resp_ok)])
        mock_session_class.return_value = session

        tool = WebSearchTool(provider="tavily", api_key="k")
        out = await tool._arun("test", num_results=3)
        self.assertTrue(out["success"])
        self.assertEqual(out["provider"], "tavily")
        self.assertEqual(out["results"][0]["source"], "tavily")

    async def test_web_search_missing_base_url(self):
        with patch.dict(os.environ, {"SAPTIVA_SEARCH_BASE_URL": "", "SEARXNG_BASE_URL": ""}):
            tool = WebSearchTool(provider="searxng", base_url=None)
            out = await tool._arun("test")
            self.assertFalse(out["success"])

    async def test_web_search_unsupported_provider(self):
        tool = WebSearchTool(provider="other", base_url="x")
        out = await tool._arun("test")
        self.assertFalse(out["success"])
        self.assertIn("no soportado", out["error"])

    @patch("saptiva_agents.tools._web_search.aiohttp.ClientSession")
    async def test_web_search_http_error(self, mock_session_class):
        resp_bad = _make_response(500, text_data="fail")
        session = _make_session(request_side_effect=[_make_cm(resp_bad)])
        mock_session_class.return_value = session

        tool = WebSearchTool(provider="searxng", base_url="https://searx.local", max_retries=0)
        out = await tool._arun("test")
        self.assertFalse(out["success"])

    @patch("saptiva_agents.tools._web_search.asyncio.sleep", new_callable=AsyncMock)
    @patch("saptiva_agents.tools._web_search.aiohttp.ClientSession")
    async def test_web_search_retries_then_success(self, mock_session_class, mock_sleep):
        data_ok = {"results": [{"title": "A", "url": "http://a", "content": "sa", "engine": "x"}]}
        resp_bad = _make_response(500, text_data="fail")
        resp_ok = _make_response(200, json_data=data_ok)
        session = _make_session(request_side_effect=[_make_cm(resp_bad), _make_cm(resp_ok)])
        mock_session_class.return_value = session

        tool = WebSearchTool(
            provider="searxng",
            base_url="https://searx.local",
            max_retries=1,
            backoff_base_s=0.0,
        )
        out = await tool._arun("test", num_results=1)
        self.assertTrue(out["success"])
        self.assertEqual(session.request.call_count, 2)
        self.assertTrue(mock_sleep.called)

    @patch("saptiva_agents.tools._web_search.aiohttp.ClientSession")
    async def test_web_search_cache_hit(self, mock_session_class):
        data = {"results": [{"title": "A", "url": "http://a", "content": "sa", "engine": "x"}]}
        resp_ok = _make_response(200, json_data=data)
        session = _make_session(request_side_effect=[_make_cm(resp_ok)])
        mock_session_class.return_value = session

        tool = WebSearchTool(provider="searxng", base_url="https://searx.local", cache_ttl_s=60.0)
        out1 = await tool._arun("test", num_results=1)
        out2 = await tool._arun("test", num_results=1)
        self.assertTrue(out1["success"])
        self.assertTrue(out2.get("cached"))
        self.assertEqual(session.request.call_count, 1)


class TestWebReadTool(unittest.IsolatedAsyncioTestCase):
    @patch("saptiva_agents.tools._web_fetch.aiohttp.ClientSession")
    async def test_read_page_success_and_cleaning(self, mock_session_class):
        html = "<html><head><title>Hola</title><style>.x{}</style></head><body><h1>T</h1><script>1</script>Hi</body></html>"
        resp_ok = _make_response(200, text_data=html)
        session = _make_session(get_side_effect=[_make_cm(resp_ok)])
        mock_session_class.return_value = session

        tool = WebReadTool()
        out = await tool._arun("https://example.com")
        self.assertTrue(out["success"])
        self.assertEqual(out["title"], "Hola")
        self.assertIn("Hi", out["text"])
        self.assertNotIn("script", out["text"])

    async def test_read_page_invalid_url(self):
        tool = WebReadTool()
        out = await tool._arun("")
        self.assertFalse(out["success"])

    @patch("saptiva_agents.tools._web_fetch.aiohttp.ClientSession")
    async def test_read_page_http_error(self, mock_session_class):
        resp_bad = _make_response(404, text_data="nope")
        session = _make_session(get_side_effect=[_make_cm(resp_bad)])
        mock_session_class.return_value = session

        tool = WebReadTool(max_retries=0)
        out = await tool._arun("https://example.com")
        self.assertFalse(out["success"])

    @patch("saptiva_agents.tools._web_fetch.asyncio.sleep", new_callable=AsyncMock)
    @patch("saptiva_agents.tools._web_fetch.aiohttp.ClientSession")
    async def test_read_page_retries_then_success(self, mock_session_class, mock_sleep):
        html = "<html><body>ok</body></html>"
        resp_bad = _make_response(500, text_data="fail")
        resp_ok = _make_response(200, text_data=html)
        session = _make_session(get_side_effect=[_make_cm(resp_bad), _make_cm(resp_ok)])
        mock_session_class.return_value = session

        tool = WebReadTool(max_retries=1, backoff_base_s=0.0)
        out = await tool._arun("https://example.com")
        self.assertTrue(out["success"])
        self.assertEqual(session.get.call_count, 2)
        self.assertTrue(mock_sleep.called)
