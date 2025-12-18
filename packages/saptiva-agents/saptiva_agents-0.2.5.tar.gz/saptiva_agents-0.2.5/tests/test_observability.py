import unittest

from saptiva_agents.core import get_request_id, request_id_context


class TestRequestIdContext(unittest.TestCase):
    def test_request_id_context_sets_and_resets(self):
        self.assertIsNone(get_request_id())
        with request_id_context("req-1"):
            self.assertEqual(get_request_id(), "req-1")
        self.assertIsNone(get_request_id())

    def test_request_id_context_noop_on_empty(self):
        with request_id_context(None):
            self.assertIsNone(get_request_id())

