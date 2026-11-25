import tempfile
import unittest
from pathlib import Path

from check_cases import check_case, check_shape, replies

_GOOD = """---
description: A case.
plugins: ["../.."]
allowed_tools: [Skill, mcp__plugin_anki-notes_anki__list_decks, mcp__plugin_anki-notes_anki__add_notes]
---
Teach me F1.
"""
_JUDGE = "---\ntype: llm\nfocus: trace\n---\nPASS if ...\n"
_CALLS = "---\ntype: tool_used\ntool: mcp__plugin_anki-notes_anki__add_notes\n---\n"


def _case(prompt, graders, mocks=()):
    root = Path(tempfile.mkdtemp())
    (root / "graders").mkdir()
    (root / "prompt.md").write_text(prompt)
    for i, g in enumerate(graders):
        (root / "graders" / f"g{i}.md").write_text(g)
    if mocks:
        (root / "mocks" / "anki").mkdir(parents=True)
        for name, text in mocks:
            (root / "mocks" / "anki" / f"{name}.md").write_text(text)
    return root


_SHARED = {"list_decks", "add_notes"}


class CheckCaseTests(unittest.TestCase):
    def test_good_case(self):
        self.assertEqual(check_case(_case(_GOOD, [_JUDGE, _CALLS]), _SHARED, _SHARED), [])

    def test_llm_focus_must_be_known(self):
        bad = "---\ntype: llm\nfocus: reply\n---\nPASS if ...\n"
        self.assertEqual(check_case(_case(_GOOD, [bad, _CALLS]), _SHARED, _SHARED),
                         ["an llm grader's focus must be last_message or trace, not reply"])

    def test_wrong_plugins(self):
        bad = _GOOD.replace('["../.."]', '["../..", "../ankimcp"]')
        self.assertEqual(len(check_case(_case(bad, [_CALLS]), _SHARED, _SHARED)), 1)

    def test_one_server_per_case(self):
        mixed = _GOOD.replace("]\n---", ", mcp__plugin_anki-notes_anki__anki_decks_list]\n---", 1)
        known = _SHARED | {"anki_decks_list"}
        self.assertEqual(check_case(_case(mixed, [_CALLS]), known, known),
                         ["allowed_tools mixes the local and remote servers' tools"])

    def test_unmocked_tool_would_reach_anki(self):
        problems = check_case(_case(_GOOD, [_CALLS]), {"list_decks"}, _SHARED)
        self.assertEqual(problems, ["add_notes is allowed but has no mock: a call would reach a real Anki"])

    def test_guide_cases_need_read(self):
        charter = _GOOD.replace("description: A case.", "description: A case.\ntags: [charter]")
        self.assertEqual(len(check_case(_case(charter, [_CALLS]), _SHARED, _SHARED)), 1)
        self.assertEqual(check_case(_case(charter.replace("[Skill,", "[Skill, Read,"), [_CALLS]), _SHARED, _SHARED), [])

    def test_trace_judge_needs_call_grader(self):
        self.assertEqual(len(check_case(_case(_GOOD, [_JUDGE]), _SHARED, _SHARED)), 1)
        regex = "---\ntype: regex\ntarget: mock_calls\npattern: x\n---\n"
        self.assertEqual(check_case(_case(_GOOD, [_JUDGE, regex]), _SHARED, _SHARED), [])


class ShapeTests(unittest.TestCase):
    def test_agent_mock_lines_and_templates(self):
        root = _case(_GOOD, [], mocks=[("add_notes", '---\ntype: agent\n---\nReply like:\n\n{"created": 1, "results": [{"index": 0}]}\n'),
                                     ("create_deck", '{"deckName": "{{input.deck_name}}"}')])
        shape = {"keys": ["created", "results"], "items": {"results": ["index", "status"]}}
        (label, reply), = replies(root / "mocks" / "anki" / "add_notes.md")
        self.assertEqual(check_shape("m", reply, shape), ["m: results[0] lacks 'status'"])
        (_, deck), = replies(root / "mocks" / "anki" / "create_deck.md")
        self.assertEqual(deck, {"deckName": "x"})


if __name__ == "__main__":
    unittest.main()
