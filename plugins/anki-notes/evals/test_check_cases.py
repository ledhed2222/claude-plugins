import tempfile
import unittest
from pathlib import Path

from check_cases import check_case, check_shape, replies

GOOD = """---
description: A case.
plugins: ["../..", "../../../ankimcp"]
env:
  EVAL_SKIP_INBOX_HOOK: "1"
allowed_tools: [Skill, mcp__plugin_ankimcp_anki__list_decks, mcp__plugin_ankimcp_anki__add_notes]
---
Teach me F1.
"""
JUDGE = "---\ntype: llm\nfocus: trace\n---\nPASS if ...\n"
CALLS = "---\ntype: tool_used\ntool: mcp__plugin_ankimcp_anki__add_notes\n---\n"


def case(prompt, graders, mocks=()):
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


SHARED = {"list_decks", "add_notes"}


class CheckCaseTests(unittest.TestCase):
    def test_good_case(self):
        self.assertEqual(check_case(case(GOOD, [JUDGE, CALLS]), SHARED, SHARED), [])

    def test_missing_env_and_plugins(self):
        bad = GOOD.replace('  EVAL_SKIP_INBOX_HOOK: "1"\n', '  OTHER: "1"\n').replace('"../../../ankimcp"', '"../ankimcp"')
        problems = check_case(case(bad, [CALLS]), SHARED, SHARED)
        self.assertEqual(len(problems), 2)

    def test_unmocked_tool_would_reach_anki(self):
        problems = check_case(case(GOOD, [CALLS]), {"list_decks"}, SHARED)
        self.assertEqual(problems, ["add_notes is allowed but has no mock: a call would reach a real Anki"])

    def test_guide_cases_need_read(self):
        charter = GOOD.replace("description: A case.", "description: A case.\ntags: [charter]")
        self.assertEqual(len(check_case(case(charter, [CALLS]), SHARED, SHARED)), 1)
        self.assertEqual(check_case(case(charter.replace("[Skill,", "[Skill, Read,"), [CALLS]), SHARED, SHARED), [])

    def test_trace_judge_needs_call_grader(self):
        self.assertEqual(len(check_case(case(GOOD, [JUDGE]), SHARED, SHARED)), 1)
        regex = "---\ntype: regex\ntarget: mock_calls\npattern: x\n---\n"
        self.assertEqual(check_case(case(GOOD, [JUDGE, regex]), SHARED, SHARED), [])


class ShapeTests(unittest.TestCase):
    def test_agent_mock_lines_and_templates(self):
        root = case(GOOD, [], mocks=[("add_notes", '---\ntype: agent\n---\nReply like:\n\n{"created": 1, "results": [{"index": 0}]}\n'),
                                     ("create_deck", '{"deckName": "{{input.deck_name}}"}')])
        shape = {"keys": ["created", "results"], "items": {"results": ["index", "status"]}}
        (label, reply), = replies(root / "mocks" / "anki" / "add_notes.md")
        self.assertEqual(check_shape("m", reply, shape), ["m: results[0] lacks 'status'"])
        (_, deck), = replies(root / "mocks" / "anki" / "create_deck.md")
        self.assertEqual(deck, {"deckName": "x"})


if __name__ == "__main__":
    unittest.main()
