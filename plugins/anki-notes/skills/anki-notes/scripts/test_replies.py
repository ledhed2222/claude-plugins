"""replies.py reads both servers' replies into the same values (fixtures: testdata/, see both_servers.py)."""
import unittest

from both_servers import OPERATIONS, SERVERS, deck_notes, load
from replies import (LOCAL, REMOTE, ReplyError, card_ids, decks, description, error_code, first_field, key, notes, server_of,
                     templates, unwrap)

# the fixture collection both servers' replies describe
_DECKS = ["AI Engineering", "AI Engineering::01 Classification metrics", "Default"]
_SEARCH = [(1795478372709, "What is <b>recall</b>?"), (1795478391691, "Which eval step costs more: inference or scoring?"),
           (1795478391692, "Precision {{c1::rises}}, recall {{c2::falls}}"), (1795478708394, "What does a binary classifier do?")]
_DECK_NOTES = [(1795478372709, "Basic", ["to-delete"]), (1795478391691, "Basic", ["ai::evals", "type::contrast"]),
               (1795478391692, "Cloze", ["ai::metrics"]), (1795478708394, "Basic", ["aie::metrics::basics", "src::metrics", "type::definition"])]
_TEMPLATES = {"Card 1": {"Front": "{{Front}}", "Back": "{{FrontSide}}\n\n<hr id=answer>\n\n{{Back}}"}}
_CARDS = {1795478372709: [1795478372709], 1795478391691: [1795478391691], 1795478391692: [1795478391692, 1795478391693],
          1795478708394: [1795478708394]}


class UnwrapTests(unittest.TestCase):
    def test_bare_payload_passes_through(self):
        self.assertEqual(unwrap({"decks": []}), {"decks": []})

    def test_mcp_tool_result(self):
        self.assertEqual(unwrap({"content": [{"type": "text", "text": '{"a": 1}'}], "isError": False}), {"a": 1})
        self.assertEqual(unwrap({"content": [], "structuredContent": {"a": 2}}), {"a": 2})
        self.assertEqual(unwrap({"jsonrpc": "2.0", "id": 1, "result": {"content": [{"type": "text", "text": "{}"}]}}), {})

    def test_key_is_stable_distinct_and_short(self):
        self.assertEqual(key("add", "D", {"Front": "Q"}), key("add", "D", {"Front": "Q"}))
        self.assertNotEqual(key("add", "D", {"Front": "Q"}), key("add", "D", {"Front": "R"}))
        self.assertLessEqual(len(key("x")), 128)  # anki-sync-mcp's idempotency_key limit


class ReadsContract:
    server = None

    def test_server_is_told_apart_by_reply_shape(self):
        for op in ("search", "decks", "notes_full", "card_ids"):
            self.assertEqual(server_of(load(self.server, op)), self.server, op)

    def test_decks(self):
        found = decks([load(self.server, "decks")])
        self.assertEqual(sorted(found), _DECKS)
        self.assertTrue(all(isinstance(i, int) for i in found.values()))

    def test_charter(self):
        self.assertEqual(description(load(self.server, "charter")), ("AI Engineering", "Charter text"))

    def test_search_first_fields(self):
        self.assertEqual([(n["id"], first_field(n)) for n in notes([load(self.server, "search")])], _SEARCH)

    def test_deck_notes_models_and_tags(self):
        self.assertEqual([(n["id"], n["model"], n["tags"]) for n in deck_notes(self.server)], _DECK_NOTES)

    def test_full_note(self):
        [row] = notes([load(self.server, "notes_full")])
        self.assertEqual((row["id"], row["model"], row["fields"]), (1795478372709, "Basic", {"Front": "What is <b>recall</b>?", "Back": "x"}))

    def test_templates(self):
        self.assertEqual(templates(load(self.server, "templates")), _TEMPLATES)

    def test_card_ids(self):
        self.assertEqual(card_ids([load(self.server, "card_ids")]), _CARDS)

    def test_unreachable_is_an_error(self):
        with self.assertRaises(ReplyError):
            load(self.server, "unreachable")


class LocalReads(ReadsContract, unittest.TestCase):
    server = LOCAL

    def test_errors_have_no_remote_code(self):
        with self.assertRaises(ReplyError) as e:
            load(LOCAL, "unreachable")
        self.assertEqual(error_code(e.exception), (None, {}))

    def test_duplicate_is_a_skipped_result(self):
        self.assertEqual(load(LOCAL, "add_duplicate")["results"][0]["reason"], "duplicate")


class RemoteReads(ReadsContract, unittest.TestCase):
    server = REMOTE

    def test_full_search_items_read_like_notes_get(self):
        """include_fields: each item is exactly anki_notes_get's note, so they normalize the same."""
        [full] = [n for n in notes([load(REMOTE, "deck_notes")]) if n["id"] == 1795478372709]
        self.assertEqual(full["model"], "Basic")
        recorded = notes([load(REMOTE, "search_full")])
        self.assertEqual([list(n["fields"]) for n in recorded], [["Front", "Back"], ["Front", "Back"], ["Text", "Back Extra"]])
        self.assertEqual([n["model"] for n in recorded], ["Basic", "Basic", "Cloze"])

    def test_trimmed_page_says_where_the_next_one_starts(self):
        """A page cut to fit the response limit returns limit = its item count, so offset + limit is the next page."""
        page = load(REMOTE, "search_trimmed")
        self.assertTrue(page["has_more"])
        self.assertEqual(page["limit"], len(page["items"]))
        self.assertLess(page["offset"] + page["limit"], page["total"])

    def test_batch_duplicate_is_a_result_naming_the_note(self):
        [res] = load(REMOTE, "add_duplicate")["result"]["notes"]
        self.assertEqual((res["status"], res["duplicate_of"]), ("duplicate", 1795478708394))

    def test_single_create_duplicate_is_a_tool_error(self):
        with self.assertRaisesRegex(ReplyError, "DUPLICATE_NOTE"):
            load(REMOTE, "note_duplicate")

    def test_batch_card_ids_skip_duplicates(self):
        receipt = load(REMOTE, "add_mixed")
        created = receipt["result"]["notes"][0]
        self.assertEqual(card_ids([receipt]), {created["note_id"]: created["card_ids"]})

    def test_error_codes(self):
        for op, code in (("note_duplicate", "DUPLICATE_NOTE"), ("note_type_manual_change", "MANUAL_CHANGE_REQUIRED"),
                         ("auth_error", "AUTHENTICATION_FAILED"), ("media_sync_in_progress", "MEDIA_SYNC_IN_PROGRESS")):
            with self.assertRaises(ReplyError) as e:
                load(REMOTE, op)
            self.assertEqual(error_code(e.exception)[0], code, op)

    def test_media_sync_in_progress_carries_counts(self):
        with self.assertRaises(ReplyError) as e:
            load(REMOTE, "media_sync_in_progress")
        media = error_code(e.exception)[1]["media_sync"]
        self.assertTrue(media["in_progress"])
        self.assertIn("175", media["added"])  # Anki's progress text: "Added: <up>↑ <down>↓"

    def test_manual_change_carries_steps(self):
        with self.assertRaises(ReplyError) as e:
            load(REMOTE, "note_type_manual_change")
        self.assertTrue(error_code(e.exception)[1]["steps"])

    def test_css_only_update_receipt(self):
        """Recorded: a preview and update sending only css (anki-sync-mcp#33)."""
        preview, update = load(REMOTE, "note_type_preview"), load(REMOTE, "note_type_updated")
        self.assertFalse(preview["impact"]["full_sync_required"])
        self.assertTrue(preview["confirmation_token"])
        self.assertEqual(update["result"]["id"], preview["impact"]["note_type_id"])

    def test_create_receipt_carries_card_ids(self):
        created = load(REMOTE, "note_created")["result"]
        self.assertEqual(card_ids([load(REMOTE, "note_created")]), {created["note_id"]: created["card_ids"]})


class CrossServerTests(unittest.TestCase):
    """Every shared operation that a script reads normalizes to the same value on both servers."""

    def test_normalized_reads_match(self):
        readers = {"decks": lambda p: sorted(decks([p])), "charter": description, "templates": templates,
                   "card_ids": lambda p: card_ids([p]), "search": lambda p: [(n["id"], first_field(n)) for n in notes([p])],
                   "notes_full": lambda p: [(n["id"], n["model"], n["fields"]) for n in notes([p])]}
        self.assertLessEqual(set(readers), set(OPERATIONS["shared"]))
        for op, read in readers.items():
            local, remote = (read(load(s, op)) for s in SERVERS)
            self.assertEqual(local, remote, op)
        self.assertEqual(*(sorted((n["id"], n["model"], n["tags"]) for n in deck_notes(s)) for s in SERVERS))


if __name__ == "__main__":
    unittest.main()
