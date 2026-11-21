"""The scripts against the fixtures the eval cases use, so the two can't drift apart."""
import json
import re
import unittest
from pathlib import Path

from charter import edit, lint as lint_charter, stages
from lint_cards import lint as lint_card, parse_cards

EVALS = Path(__file__).resolve().parents[3] / "evals"


def case_text(case, path="prompt.md"):
    return (EVALS / case / path).read_text()


def mock_charter(case, deck):
    """The description an agent mock returns for deck, from its quoted JSON reply."""
    text = case_text(case, "mocks/anki/get_deck_description.md")
    for line in text.splitlines():
        if line.startswith("{") and f'"name": "{deck}"' in line:
            return json.loads(line)["description"]
    raise AssertionError(f"no {deck} charter in {case}")


def errors(findings):
    return [m for s, m in findings if s == "error"]


class InboxFixtureTests(unittest.TestCase):
    def test_charter_from_inbox(self):
        cards = parse_cards(case_text("charter-from-inbox"))
        self.assertEqual([n for n, _ in cards], [2])
        card = cards[0][1]
        self.assertEqual(card["model"], "Cloze")
        # queued without a src:: tag: the add step must add one before add_cards accepts it
        self.assertEqual(errors(lint_card(card, prefix="es")), ["tags: missing src:: tag"])

    def test_queued_charter_lints_clean(self):
        block = re.search(r"```json\s*\n(\{\"charter\".*?)```", case_text("charter-from-inbox"), re.S).group(1)
        charter = json.loads(block)["charter"]
        self.assertEqual(lint_charter(charter["description"], subdecks=charter["stages"]), [])


class CharterFixtureTests(unittest.TestCase):
    def test_spanish_charter_dash_stages(self):
        text = mock_charter("charter-change-minimal", "Spanish")
        self.assertEqual([n for n, _ in stages(text)], ["01", "02", "03"])
        findings = lint_charter(text, subdecks=["01 Present tense", "02 Past tenses", "03 Subjunctive"])
        # the fixture has no Assumes: line; every other check passes
        self.assertEqual(findings, [("error", "no 'Assumes:' line")])

    def test_charter_change_minimal(self):
        old = mock_charter("charter-change-minimal", "Spanish")
        scope = old.split("## Scope\n")[1].split("\n\n")[0]
        new_scope = scope.replace(", and colloquial and regional slang (Spain and Latin America)", "")
        new = edit(old, "Scope", new_scope + "\n\n")
        changed = [(a, b) for a, b in zip(old.splitlines(), new.splitlines()) if a != b]
        self.assertEqual(len(old.splitlines()), len(new.splitlines()))
        self.assertEqual(changed, [(scope, new_scope)])

    def test_ai_engineering_stages_on_one_line(self):
        text = mock_charter("charter-lean", "AI Engineering")
        warns = [m for s, m in lint_charter(text) if s == "warn"]
        self.assertEqual(len([m for m in warns if "one-line description" in m]), 5)


if __name__ == "__main__":
    unittest.main()
