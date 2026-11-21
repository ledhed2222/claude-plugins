import os
import tempfile
import unittest

from ankimcp_client import Client
from apply_stage import apply_plan, check_items
from test_add_cards import addon
from test_ankimcp_client import fake_server


class ApplyStageTests(unittest.IsolatedAsyncioTestCase):
    def test_tags_only_on_rewrite(self):
        check_items([{"rewrite": 1, "fields": {"Front": "Q?"}, "tags": ["rescued"]}])
        with self.assertRaises(SystemExit):
            check_items([{"keep": 1, "tags": ["rescued"]}])

    async def test_rewrite_tags_are_added(self):
        plan = {"deck": "AI Engineering::01 Classification metrics",
                "items": [{"rewrite": 7, "fields": {"Front": "Q?"}, "tags": ["rescued"]}, {"rewrite": 8, "fields": {"Front": "R?"}}]}
        calls = []
        server = await fake_server(addon(calls, []), [])
        with tempfile.TemporaryDirectory() as tmp:
            async with server:
                async with Client(port=server.sockets[0].getsockname()[1]) as anki:
                    await apply_plan(anki, os.path.join(tmp, "plan.json"), plan)
        self.assertEqual([a for n, a in calls if n == "tag_add"], [{"note_ids": [7], "tags": "rescued"}])


if __name__ == "__main__":
    unittest.main()
