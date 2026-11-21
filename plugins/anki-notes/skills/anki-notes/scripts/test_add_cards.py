import unittest

from add_cards import add_cards, check
from ankimcp_client import AnkiError, Client
from find_dupes import close_matches
from test_ankimcp_client import fake_server, tool_result

_TAGS = ["aie::evals::cost", "type::contrast", "src::eval-cost"]


def _card(front, stage="02 Eval basics", **kw):
    return dict({"deck": "AI Engineering", "stage": stage, "model": "Basic",
                 "fields": {"Front": front, "Back": "<b>Inference.</b>"}, "tags": _TAGS}, **kw)


def _addon(calls, add_status):
    """Replies like the add-on: add_notes results by index, notes_info cards, reposition count."""
    def replies(msg):
        if msg.get("method") != "tools/call":
            return {"jsonrpc": "2.0", "id": msg.get("id"), "result": {}} if "id" in msg else None
        name, args = msg["params"]["name"], msg["params"]["arguments"]
        calls.append((name, args))
        if name == "add_notes":
            results = []
            for i, _ in enumerate(args["notes"]):
                status = add_status.pop(0)
                r = {"index": i, "status": status}
                if status == "created":
                    r["note_id"] = 100 + len(calls) * 10 + i
                elif status == "skipped":
                    r["reason"] = "duplicate"
                else:
                    r["error"] = "Unknown fields for this model: Foo"
                results.append(r)
            payload = {"created": sum(r["status"] == "created" for r in results), "results": results}
        elif name == "notes_info":
            payload = {"notes": [{"noteId": n, "cards": [n * 10]} for n in args["notes"]]}
        elif name == "card_reposition":
            payload = {"repositioned": len(args["card_ids"])}
        elif name == "sync":
            payload = {"job_id": "j"} if "job_id" not in args else {"status": "conflict" if "resolve" not in args else "cancelled"}
        else:
            payload = {}
        return dict(tool_result(payload), jsonrpc="2.0", id=msg["id"])
    return replies


class AddCardsTests(unittest.IsolatedAsyncioTestCase):
    def test_check_refuses_batch(self):
        cards = [(1, _card("Which eval step costs more: inference or scoring?")),
                 (2, _card("Which eval step costs more: inference or scoring?", stage=None)),
                 (3, {"unparsed": "{"})]
        errors = check(cards)
        self.assertEqual(errors, ["#3: not valid JSON", "#2: no stage chosen"])

    async def test_report_groups_and_first(self):
        cards = [(2, _card("Which eval step costs more: inference or scoring?")),
                 (3, _card("Which costs more to rerun: inference or scoring?", stage="01 Classification metrics", first=True)),
                 (5, _card("Which is cached: inference outputs or scores?")),
                 (6, _card("Which part is slower: inference or scoring?"))]
        calls = []
        server = await fake_server(_addon(calls, ["created", "skipped", "failed", "created"]), [])
        report = {"added": [], "duplicate": [], "failed": {}}
        async with server:
            async with Client(port=server.sockets[0].getsockname()[1]) as anki:
                await add_cards(anki, cards, report)
        adds = [a for n, a in calls if n == "add_notes"]
        self.assertEqual([a["deck_name"] for a in adds], ["AI Engineering::02 Eval basics", "AI Engineering::01 Classification metrics"])
        self.assertEqual(len(adds[0]["notes"]), 3)
        self.assertEqual(report["added"], [2, 3])
        self.assertEqual(report["duplicate"], [5])
        self.assertIn(6, report["failed"])
        repo = [a for n, a in calls if n == "card_reposition"]
        self.assertEqual(len(repo), 1)
        self.assertTrue(repo[0]["shift_existing"])
        self.assertEqual(len(repo[0]["card_ids"]), 1)

    async def test_sync_conflict_is_cancelled(self):
        calls = []
        server = await fake_server(_addon(calls, []), [])
        async with server:
            async with Client(port=server.sockets[0].getsockname()[1]) as anki:
                with self.assertRaises(AnkiError):
                    await anki.sync(poll=0)
        self.assertEqual(calls[-1], ("sync", {"job_id": "j", "resolve": "cancel"}))


class FindDupesTests(unittest.TestCase):
    def test_close_matches(self):
        existing = [(1, "What is a confusion matrix?"), (2, "What does <b>recall</b> measure?"),
                    (3, "Which eval step costs more: inference or scoring?")]
        m = close_matches("Which eval step is more expensive: inference or scoring?", existing)
        self.assertEqual(m[0][1], 3)
        self.assertNotIn(1, [x[1] for x in m])
        self.assertEqual(close_matches("Grounding is a {{c1::noun}}", existing), [])


if __name__ == "__main__":
    unittest.main()
