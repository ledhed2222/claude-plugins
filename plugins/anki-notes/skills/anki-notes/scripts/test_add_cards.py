"""add_cards.py on both servers, through its CLI, with every planned call checked against the server's real tool schema."""
import json
import unittest

from add_cards import check, follow_up, outcomes
from both_servers import check_call, load, plan_lines, raw, run_script
from find_dupes import close_matches
from replies import LOCAL, REMOTE, decks, note_type_names

_STAGE = "01 Classification metrics"
_TAGS = ["aie::metrics::errors", "type::application", "src::metrics"]


def _card(front, **kw):
    return dict({"deck": "AI Engineering", "stage": _STAGE, "model": "Basic",
                 "fields": {"Front": front, "Back": "<b>A false positive.</b>"}, "tags": _TAGS}, **kw)


_CARDS = [_card("A spam filter flags a real email as spam. Which kind of error is this: a false positive or a false negative?"),
          _card("A fraud model blocks a legitimate payment. Which kind of error is this: a false positive or a false negative?", first=True)]


class AddCardsContract:
    server = None

    # --- per-server hooks -------------------------------------------------

    def plan_args(self):
        return ["--decks", "decks.json", "--note-types", "note_types.json"] if self.server == REMOTE else []

    def files(self, cards=_CARDS):
        return {"cards.json": cards, "decks.json": raw(self.server, "decks"), "note_types.json": raw(self.server, "note_types")}

    def add_replies(self, statuses):
        """Saved replies to the plan's add calls, one status per card (all cards share one stage and type)."""
        if "unreachable" in statuses:
            return [raw(self.server, "unreachable")]
        if self.server == REMOTE:  # one batch receipt with a result per card
            created, dup = load(REMOTE, "add_created")["result"]["notes"][0], load(REMOTE, "add_duplicate")["result"]["notes"][0]
            receipt = raw(REMOTE, "add_created")
            receipt["result"] = {"notes": [created if s == "created" else dup for s in statuses],
                                 "created": statuses.count("created"), "duplicates": statuses.count("duplicate")}
            return [receipt]
        created, dup = load(LOCAL, "add_created")["results"][0], load(LOCAL, "add_duplicate")["results"][0]
        return [{"results": [dict(created if s == "created" else dup, index=i) for i, s in enumerate(statuses)]}]

    # --- helpers ----------------------------------------------------------

    def plan(self, cards=_CARDS):
        r = run_script("add_cards.py", "plan", "cards.json", "--server", self.server, *self.plan_args(), files=self.files(cards))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        calls = plan_lines(r.stdout)
        self.assertCallsValid(calls)
        return calls

    def order(self, statuses, *extra, files=None):
        replies = {f"r{i}.json": rep for i, rep in enumerate(self.add_replies(statuses))}
        r = run_script("add_cards.py", "order", "cards.json", "--server", self.server, *replies, *extra,
                       files=dict(self.files(), **replies, **(files or {})))
        report = json.loads(r.stdout.strip().splitlines()[-1])
        self.assertCallsValid(report["calls"])
        return r, report

    def assertCallsValid(self, calls):
        problems = [p for c in calls for p in check_call(self.server, c)]
        self.assertEqual(problems, [], f"{self.server} calls don't match the server's tool schemas")

    # --- the contract -----------------------------------------------------

    def test_plan_adds_every_card_into_its_stage(self):
        calls = self.plan()
        if self.server == LOCAL:
            self.assertEqual([c["tool"] for c in calls], ["add_notes"])
            self.assertEqual(calls[0]["args"]["deck_name"], f"AI Engineering::{_STAGE}")
            self.assertEqual([n["fields"] for n in calls[0]["args"]["notes"]], [c["fields"] for c in _CARDS])
        else:
            deck_id = decks([load(REMOTE, "decks")])[f"AI Engineering::{_STAGE}"]
            basic = {v: k for k, v in note_type_names([load(REMOTE, "note_types")]).items()}["Basic"]
            self.assertEqual([c["tool"] for c in calls], ["anki_notes_create_batch"])
            self.assertTrue(calls[0]["args"]["skip_duplicates"])
            notes = calls[0]["args"]["notes"]
            self.assertEqual({(n["deck_id"], n["note_type_id"]) for n in notes}, {(deck_id, basic)})
            self.assertEqual([n["fields"] for n in notes], [c["fields"] for c in _CARDS])

    def test_replanning_gives_the_same_calls(self):
        self.assertEqual(self.plan(), self.plan())  # on remote, the same idempotency keys

    def test_plan_refuses_lint_errors_and_missing_stages(self):
        bad = [_card("Q?", tags=["type::application"]), _card("Which costs more: A or B?", stage=None)]
        r = run_script("add_cards.py", "plan", "cards.json", "--server", self.server, *self.plan_args(), files=self.files(bad))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("#1: tags", r.stderr)
        self.assertIn("#2: no stage chosen", r.stderr)

    def test_order_reports_added_and_duplicate_then_places_and_syncs(self):
        r, report = self.order(["duplicate", "created"])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual((report["added"], report["duplicate"], report["failed"]), ([2], [1], {}))
        tools = [c["tool"] for c in report["calls"]]
        if self.server == LOCAL:  # card ids come from notes_info first
            self.assertEqual(tools, ["notes_info"])
            r, report = self.order(["duplicate", "created"], "--cards", "cards_reply.json",
                                   files={"cards_reply.json": raw(LOCAL, "card_ids")})
            self.assertEqual([c["tool"] for c in report["calls"]], ["card_reposition", "sync"])
        else:  # the server synced each write itself, so the receipt says remote_synced and no sync is planned
            self.assertEqual(tools, ["anki_cards_reposition"])
        self.assertEqual(report["calls"][0]["args"]["card_ids"], [1795478708394])

    def test_unreachable_fails_every_card_and_plans_nothing(self):
        r, report = self.order(["unreachable", "unreachable"])
        self.assertEqual(r.returncode, 1)
        self.assertEqual(sorted(map(int, report["failed"])), [1, 2])
        self.assertEqual((report["added"], report["calls"]), ([], []))

    def test_nothing_added_means_no_sync(self):
        _, report = self.order(["duplicate", "duplicate"])
        self.assertEqual(report["calls"], [])


class LocalAddCards(AddCardsContract, unittest.TestCase):
    server = LOCAL

    def test_one_add_per_stage_and_type(self):
        cards = _CARDS + [_card("Which is cheaper to rerun: inference or scoring?", stage="02 Eval basics")]
        self.assertEqual([c["args"]["deck_name"] for c in self.plan(cards)],
                         [f"AI Engineering::{_STAGE}", "AI Engineering::02 Eval basics"])


class RemoteAddCards(AddCardsContract, unittest.TestCase):
    server = REMOTE

    def test_missing_stage_deck_is_created_first(self):
        cards = [_card("Which is cheaper to rerun: inference or scoring?", stage="02 Eval basics")]
        r = run_script("add_cards.py", "plan", "cards.json", "--server", REMOTE, *self.plan_args(), files=self.files(cards))
        self.assertNotEqual(r.returncode, 0)
        calls = plan_lines(r.stdout)
        self.assertCallsValid(calls)
        self.assertEqual(calls[0]["args"]["name"], "AI Engineering::02 Eval basics")

    def test_unknown_note_type_is_refused(self):
        r = run_script("add_cards.py", "plan", "cards.json", "--server", REMOTE, *self.plan_args(),
                       files=self.files([_card("Which costs more: A or B?", model="Mine")]))
        self.assertIn("note types not in Anki: Mine", r.stderr)

    def test_sync_only_when_a_receipt_says_unsynced(self):
        receipt = self.add_replies(["created", "created"])[0]
        self.assertTrue(receipt["remote_synced"])
        results = outcomes([(1, _CARDS[0]), (2, _CARDS[1])], REMOTE, [receipt])
        self.assertNotIn("anki_sync", [c["tool"] for c in follow_up([(1, _CARDS[0])], REMOTE, results, [receipt])])
        unsynced = dict(receipt, remote_synced=False)
        self.assertEqual(follow_up([(1, _CARDS[0])], REMOTE, results, [unsynced])[-1]["tool"], "anki_sync")

    def test_duplicates_name_the_note_they_repeat(self):
        _, report = self.order(["duplicate", "created"])
        self.assertEqual(report["duplicate_of"], {"1": 1795478708394})

    def test_a_batch_per_50_cards_each_with_its_own_key(self):
        cards = [_card(f"Which costs more to rerun, step {i}: inference or scoring?") for i in range(120)]
        calls = self.plan(cards)
        self.assertEqual([len(c["args"]["notes"]) for c in calls], [50, 50, 20])
        self.assertEqual(len({c["args"]["idempotency_key"] for c in calls}), 3)

    def test_results_map_back_across_batches(self):
        cards = [(i + 1, _card(f"Which costs more to rerun, step {i}: inference or scoring?")) for i in range(51)]
        first, dup = load(REMOTE, "add_created")["result"]["notes"][0], load(REMOTE, "add_duplicate")["result"]["notes"][0]
        batch1 = {"result": {"notes": [dict(first, note_id=1000 + i) for i in range(50)]}}
        batch2 = {"result": {"notes": [dup]}}
        results = outcomes(cards, REMOTE, [batch1, batch2])
        self.assertEqual((results[1], results[50], results[51]), (("added", 1000), ("added", 1049), ("duplicate", 1795478708394)))

    def test_a_short_reply_fails_its_batch(self):
        cards = [(1, _CARDS[0]), (2, _CARDS[1])]
        results = outcomes(cards, REMOTE, [load(REMOTE, "add_created")])
        self.assertEqual({results[1][0], results[2][0]}, {"failed"})

    def test_a_refused_batch_of_one_duplicate_is_a_duplicate(self):
        """A batch sent by hand without skip_duplicates, as recorded from a deployed server."""
        refused = {"r.json": raw(REMOTE, "batch_duplicate_error")}
        one = run_script("add_cards.py", "order", "cards.json", "--server", REMOTE, "r.json",
                         files=dict(self.files(_CARDS[:1]), **refused))
        self.assertEqual(json.loads(one.stdout.strip().splitlines()[-1])["duplicate"], [1], one.stdout + one.stderr)
        both = run_script("add_cards.py", "order", "cards.json", "--server", REMOTE, "r.json", files=dict(self.files(), **refused))
        report = json.loads(both.stdout.strip().splitlines()[-1])
        self.assertEqual(sorted(report["failed"]), ["1", "2"])
        self.assertIn("skip_duplicates", report["failed"]["1"])

    def test_full_sync_required_says_the_cards_are_on_the_server(self):
        r = run_script("add_cards.py", "order", "cards.json", "--server", REMOTE, "r.json",
                       files=dict(self.files(), **{"r.json": raw(REMOTE, "full_sync_required")}))
        report = json.loads(r.stdout.strip().splitlines()[-1])
        self.assertEqual(sorted(report["failed"]), ["1", "2"])
        self.assertIn("saved on the server but not synced", report["failed"]["1"])
        self.assertEqual(report["calls"], [])

    def test_recorded_mixed_batch(self):
        """The receipt recorded from a live anki-sync-mcp: one created, one duplicate of a note it already held."""
        receipt = load(REMOTE, "add_mixed")
        results = outcomes([(1, _CARDS[0]), (2, _CARDS[1])], REMOTE, [receipt])
        self.assertEqual([r[0] for r in (results[1], results[2])], ["added", "duplicate"])
        self.assertEqual(results[2][1], receipt["result"]["notes"][1]["duplicate_of"])


class CheckTests(unittest.TestCase):
    def test_check_refuses_missing_stage(self):
        self.assertEqual(check([(1, _card("Which costs more: A or B?", stage=None))]), ["#1: no stage chosen"])


class FindDupesTests(unittest.TestCase):
    def test_close_matches(self):
        existing = [(1, "What is a confusion matrix?"), (2, "What does <b>recall</b> measure?"),
                    (3, "Which eval step costs more: inference or scoring?")]
        m = close_matches("Which eval step is more expensive: inference or scoring?", existing)
        self.assertEqual(m[0][1], 3)
        self.assertNotIn(1, [x[1] for x in m])
        self.assertEqual(close_matches("Grounding is a {{c1::noun}}", existing), [])

    def test_image_file_names_count(self):
        """Anki's duplicate check keeps media file names, so two maps with one question aren't the same field."""
        q = "<br />Which Sherry Triangle town is marked on this map?"
        m = close_matches('<img src="map-a.svg">' + q, [(1, '<img src="map-b.svg">' + q)])
        self.assertTrue(m and m[0][0] < 1.0)
        self.assertEqual(close_matches('<img src="map-a.svg">' + q, [(1, '<img src="map-a.svg">' + q)])[0][0], 1.0)


class FindDupesContract:
    server = None

    def test_cli_lists_the_deck_note_and_flags_an_exact_repeat(self):
        drafts = [_card("What does a binary classifier do?"), _card("Which eval step is more expensive: inference or scoring?")]
        r = run_script("find_dupes.py", "cards.json", "search.json", files={"cards.json": drafts, "search.json": raw(self.server, "search")})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("1.00 note 1795478708394: What does a binary classifier do?", r.stdout)
        self.assertIn("note 1795478391691: Which eval step costs more", r.stdout)

    def test_cli_compares_drafts_with_each_other(self):
        drafts = [_card("Which soil gives the finest Palomino?"), _card("Which soil gives the finest Palomino?")]
        r = run_script("find_dupes.py", "cards.json", "search.json", files={"cards.json": drafts, "search.json": raw(self.server, "search")})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("1.00 draft #1: Which soil gives the finest Palomino?", r.stdout)

    def test_cli_refuses_an_error_reply(self):
        r = run_script("find_dupes.py", "cards.json", "search.json", files={"cards.json": _CARDS, "search.json": raw(self.server, "unreachable")})
        self.assertIn("a saved reply is an error", r.stderr)


class LocalFindDupes(FindDupesContract, unittest.TestCase):
    server = LOCAL


class RemoteFindDupes(FindDupesContract, unittest.TestCase):
    server = REMOTE


if __name__ == "__main__":
    unittest.main()
