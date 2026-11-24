"""apply_stage.py on both servers: plan, record and place through its CLI, every call checked against the server's tool schema."""
import json
import os
import subprocess
import sys
import tempfile
import unittest

from apply_stage import _check_items
from both_servers import HERE, check_call, load, plan_lines, raw
from replies import LOCAL, REMOTE, decks

_DECK = "AI Engineering::01 Classification metrics"
_NEW_ID = 1795478708394  # the note id in both servers' add_created fixture
_PLAN = {"deck": _DECK, "tags": ["src::metrics"],
         "items": [{"new": {"model": "Basic", "fields": {"Front": "What does a binary classifier do?", "Back": "Sorts inputs into two classes."}}},
                   {"keep": 1795478391691},
                   {"rewrite": 1795478391692, "fields": {"Text": "Precision {{c1::rises}}, recall {{c2::falls}}"}, "tags": ["rescued"]},
                   {"delete": [1795478372709]}]}


class ApplyStageContract:
    server = None
    new_note_reply = None  # the fixture for one new note's add reply

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.plan_path = self.file("plan.json", _PLAN)
        self.ids = ["--decks", self.file("decks.json", raw(self.server, "decks")),
                    "--note-types", self.file("types.json", raw(self.server, "note_types"))] if self.server == REMOTE else []

    def file(self, name, content):
        p = os.path.join(self.tmp.name, name)
        with open(p, "w") as f:
            json.dump(content, f)
        return p

    def run_cmd(self, *args, ok=True):
        r = subprocess.run([sys.executable, "-I", str(HERE / "apply_stage.py"), *args], capture_output=True, text=True)
        if ok:
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return r

    def calls(self, *args):
        calls = plan_lines(self.run_cmd(*args, "--server", self.server).stdout)
        self.assertEqual([p for c in calls for p in check_call(self.server, c)], [], f"{self.server} calls don't match its tool schemas")
        return calls

    def test_plan_writes_each_item(self):
        tools = [c["tool"] for c in self.calls("plan", self.plan_path, *self.ids)]
        if self.server == LOCAL:
            self.assertEqual(tools, ["create_deck", "add_notes", "update_note_fields", "tag_add", "tag_add"])
        else:
            self.assertEqual(tools, ["anki_notes_create", "anki_notes_update_fields", "anki_notes_add_tags", "anki_notes_add_tags"])

    def test_record_then_place_in_study_order(self):
        self.run_cmd("record", self.plan_path, "--server", self.server, self.file("new.json", raw(self.server, self.new_note_reply)))
        with open(self.plan_path + ".applied.json") as f:
            self.assertEqual(json.load(f), {"0": _NEW_ID})
        self.assertNotIn("add_notes", [c["tool"] for c in self.calls("plan", self.plan_path, *self.ids)])
        self.assertNotIn("anki_notes_create", [c["tool"] for c in self.calls("plan", self.plan_path, *self.ids)])

        lookup = self.calls("place", self.plan_path, *self.ids)
        self.assertEqual([c["tool"] for c in lookup], ["notes_info" if self.server == LOCAL else "anki_cards_search"])
        placed = self.calls("place", self.plan_path, *self.ids, "--cards", self.file("cards.json", raw(self.server, "card_ids")), "--sync")
        order = [_NEW_ID, 1795478391691, 1795478391692, 1795478391693]  # new, keep, then the rewrite's two cloze cards
        self.assertEqual([c["args"]["card_ids"] for c in placed[:3]], [order] * 3)
        self.assertEqual(placed[-1]["tool"], "sync" if self.server == LOCAL else "anki_sync")

    def test_place_before_record_is_refused(self):
        r = self.run_cmd("place", self.plan_path, "--server", self.server, *self.ids, ok=False)
        self.assertIn("record first", r.stderr)


class LocalApplyStage(ApplyStageContract, unittest.TestCase):
    server = LOCAL
    new_note_reply = "add_created"

    def test_move_names_the_deck(self):
        self.run_cmd("record", self.plan_path, "--server", LOCAL, self.file("new.json", raw(LOCAL, "add_created")))
        placed = self.calls("place", self.plan_path, "--cards", self.file("cards.json", raw(LOCAL, "card_ids")))
        self.assertEqual(placed[0]["args"]["deck"], _DECK)


class RemoteApplyStage(ApplyStageContract, unittest.TestCase):
    server = REMOTE
    new_note_reply = "note_created"  # apply_stage adds new notes one anki_notes_create at a time

    def test_writes_carry_ids_and_keys(self):
        calls = self.calls("plan", self.plan_path, *self.ids)
        self.assertEqual(calls[0]["args"]["deck_id"], decks([load(REMOTE, "decks")])[_DECK])
        self.assertTrue(all(c["args"].get("idempotency_key") for c in calls))

    def test_missing_deck_is_created_first(self):
        other = self.file("other.json", dict(_PLAN, deck="AI Engineering::02 Eval basics"))
        r = self.run_cmd("plan", other, "--server", REMOTE, *self.ids, ok=False)
        self.assertEqual(plan_lines(r.stdout)[0]["tool"], "anki_decks_create")


class CheckItemsTests(unittest.TestCase):
    def test_tags_only_on_rewrite(self):
        _check_items([{"rewrite": 1, "fields": {"Front": "Q?"}, "tags": ["rescued"]}])
        with self.assertRaises(SystemExit):
            _check_items([{"keep": 1, "tags": ["rescued"]}])


if __name__ == "__main__":
    unittest.main()
