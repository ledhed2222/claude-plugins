import unittest

from charter import edit, lint, prefix, stages

from both_servers import check_call, load, raw, run_script
from replies import LOCAL, REMOTE, ReplyError, description, error_code

_GOOD = """## Scope
Spanish for living in Madrid: everyday conversation and reading. In: present and past tenses, ser vs estar, common verbs.

Assumes: English grammar terms (subject, verb, tense).

## Out of scope
Regional slang (nowhere: looked up). Spanish literature (nowhere).

## Adding
Ask: propose cards and wait for a yes.

## Stages
- `01 Sounds and spelling`: pronunciation and accents.
- `02 Present tense`: regular and common irregular verbs.

## Conventions
- Overrides: ask both directions for vocabulary.
- Tags: `es::<area>::<topic>`.
"""

_MESSI = _GOOD.replace("Ask: propose", "Maybe propose").replace("Assumes:", "Knows:")


def _msgs(text, **kw):
    return [m for _, m in lint(text, **kw)]


class CharterLintTests(unittest.TestCase):
    def test_good(self):
        self.assertEqual(lint(_GOOD), [])
        self.assertEqual(prefix(_GOOD), "es")
        self.assertEqual(stages(_GOOD), [("01", "Sounds and spelling"), ("02", "Present tense")])

    def test_adding_and_assumes(self):
        m = _msgs(_MESSI)
        self.assertTrue(any("Automatic or Ask" in x for x in m))
        self.assertTrue(any("Assumes" in x for x in m))

    def test_missing_section(self):
        self.assertTrue(any("## Out of scope" in x for x in _msgs(_GOOD.replace("## Out of scope", "## Excluded"))))

    def test_prefix_taken(self):
        self.assertTrue(any("already used" in x for x in _msgs(_GOOD, other_prefixes=["es"])))

    def test_subdecks(self):
        m = _msgs(_GOOD, subdecks=["01 Sounds and spelling", "03 Past tense"])
        self.assertIn("stage 02 Present tense has no subdeck", m)
        self.assertIn("subdeck 03 Past tense is not a stage", m)

    def test_stage_numbers(self):
        self.assertTrue(any("not 01..n" in x for x in _msgs(_GOOD.replace("`02 Present", "`03 Present"))))
        self.assertEqual(_msgs(_GOOD.replace("`02 Present", "`00 Present")), [])


class EvalCaseTests(unittest.TestCase):
    """Eval cases from the formulation PR that a script can grade without an LLM."""

    def test_charter_lean(self):
        bloated = _GOOD.replace("## Conventions\n", "## Conventions\n" + "- Keep backs to one fact and keep them short.\n" * 30)
        self.assertTrue(any("words" in x for x in _msgs(bloated)))
        one_line = _GOOD.replace("- `01 Sounds and spelling`: pronunciation and accents.\n- `02 Present tense`: regular and common irregular verbs.",
                                "`01 Sounds and spelling` → `02 Present tense`.")
        m = _msgs(one_line)
        self.assertIn("stage 01 Sounds and spelling has no one-line description", m)
        self.assertIn("stage 02 Present tense has no one-line description", m)

    def test_charter_change_minimal(self):
        new = edit(_GOOD, "Out of scope", "Regional slang and voseo (nowhere: looked up). Spanish literature (nowhere).\n\n")
        old_lines, new_lines = _GOOD.splitlines(), new.splitlines()
        self.assertEqual(len(old_lines), len(new_lines))
        changed = [i for i, (a, b) in enumerate(zip(old_lines, new_lines)) if a != b]
        self.assertEqual(changed, [old_lines.index("Regional slang (nowhere: looked up). Spanish literature (nowhere).")])
        self.assertEqual(lint(new), [])

    def test_edit_last_section(self):
        new = edit(_GOOD, "Conventions", "- Tags: `es::<area>::<topic>`.")
        self.assertTrue(new.startswith(_GOOD.split("## Conventions")[0]))
        self.assertTrue(new.endswith("## Conventions\n- Tags: `es::<area>::<topic>`.\n"))


class CharterLintContract:
    """lint reads either server's saved deck list and charters (fixtures: testdata/, see both_servers.py)."""
    server = None

    def lint(self, *flags, files):
        return run_script("charter.py", "lint", *flags, files=files)

    def test_subdecks_and_taken_prefix(self):
        other = dict(load(self.server, "charter"), description="## Conventions\n- Tags: `es::x`")
        r = self.lint("charter.md", "--deck", "AI Engineering", "--decks", "decks.json", "--others", "other.json",
                      files={"charter.md": _GOOD, "decks.json": raw(self.server, "decks"), "other.json": other})
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("tag prefix es:: is already used", r.stdout)
        self.assertIn("subdeck 01 Classification metrics is not a stage", r.stdout)

    def test_charter_from_a_saved_reply(self):
        saved = dict(load(self.server, "charter"), description=_GOOD)
        r = self.lint("saved.json", files={"saved.json": saved})
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_error_reply_is_refused(self):
        r = self.lint("charter.md", "--others", "other.json", files={"charter.md": _GOOD, "other.json": raw(self.server, "unreachable")})
        self.assertIn("a saved reply is an error", r.stderr)


class CharterCallsContract:
    """Reading and saving a charter, as SKILL.md's tools table says, checked against each server's real schema."""
    server = None

    def calls(self):
        if self.server == LOCAL:
            return [{"tool": "get_deck_description", "args": {"deck_name": "AI Engineering"}},
                    {"tool": "update_deck_description", "args": {"deck_name": "AI Engineering", "description": _GOOD, "is_markdown": True}}]
        deck_id = load(REMOTE, "charter")["id"]  # a read by name returns the id the save needs
        return [{"tool": "anki_decks_get", "args": {"name": "AI Engineering"}},
                {"tool": "anki_decks_update", "args": {"deck_id": deck_id, "description": _GOOD, "idempotency_key": "k"}}]

    def test_calls_match_the_schema(self):
        self.assertEqual([p for c in self.calls() for p in check_call(self.server, c)], [])

    def test_read_gives_the_charter(self):
        name, text = description(load(self.server, "charter"))
        self.assertEqual((name, text), ("AI Engineering", "Charter text"))


class LocalCharterCalls(CharterCallsContract, unittest.TestCase):
    server = LOCAL


class RemoteCharterCalls(CharterCallsContract, unittest.TestCase):
    server = REMOTE

    def test_unknown_name_is_not_found(self):
        with self.assertRaises(ReplyError) as e:
            load(REMOTE, "deck_not_found")
        self.assertEqual(error_code(e.exception)[0], "NOT_FOUND")


class LocalCharterLint(CharterLintContract, unittest.TestCase):
    server = LOCAL


class RemoteCharterLint(CharterLintContract, unittest.TestCase):
    server = REMOTE


if __name__ == "__main__":
    unittest.main()
