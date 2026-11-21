import unittest

from charter import edit, lint, prefix, stages

GOOD = """## Scope
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

MESSI = GOOD.replace("Ask: propose", "Maybe propose").replace("Assumes:", "Knows:")


def msgs(text, **kw):
    return [m for _, m in lint(text, **kw)]


class CharterLintTests(unittest.TestCase):
    def test_good(self):
        self.assertEqual(lint(GOOD), [])
        self.assertEqual(prefix(GOOD), "es")
        self.assertEqual(stages(GOOD), [("01", "Sounds and spelling"), ("02", "Present tense")])

    def test_adding_and_assumes(self):
        m = msgs(MESSI)
        self.assertTrue(any("Automatic or Ask" in x for x in m))
        self.assertTrue(any("Assumes" in x for x in m))

    def test_missing_section(self):
        self.assertTrue(any("## Out of scope" in x for x in msgs(GOOD.replace("## Out of scope", "## Excluded"))))

    def test_prefix_taken(self):
        self.assertTrue(any("already used" in x for x in msgs(GOOD, other_prefixes=["es"])))

    def test_subdecks(self):
        m = msgs(GOOD, subdecks=["01 Sounds and spelling", "03 Past tense"])
        self.assertIn("stage 02 Present tense has no subdeck", m)
        self.assertIn("subdeck 03 Past tense is not a stage", m)

    def test_stage_numbers(self):
        self.assertTrue(any("not 01..n" in x for x in msgs(GOOD.replace("`02 Present", "`03 Present"))))
        self.assertEqual(msgs(GOOD.replace("`02 Present", "`00 Present")), [])


class EvalCaseTests(unittest.TestCase):
    """Eval cases from the formulation PR that a script can grade without an LLM."""

    def test_charter_lean(self):
        bloated = GOOD.replace("## Conventions\n", "## Conventions\n" + "- Keep backs to one fact and keep them short.\n" * 30)
        self.assertTrue(any("words" in x for x in msgs(bloated)))
        one_line = GOOD.replace("- `01 Sounds and spelling`: pronunciation and accents.\n- `02 Present tense`: regular and common irregular verbs.",
                                "`01 Sounds and spelling` → `02 Present tense`.")
        m = msgs(one_line)
        self.assertIn("stage 01 Sounds and spelling has no one-line description", m)
        self.assertIn("stage 02 Present tense has no one-line description", m)

    def test_charter_change_minimal(self):
        new = edit(GOOD, "Out of scope", "Regional slang and voseo (nowhere: looked up). Spanish literature (nowhere).\n\n")
        old_lines, new_lines = GOOD.splitlines(), new.splitlines()
        self.assertEqual(len(old_lines), len(new_lines))
        changed = [i for i, (a, b) in enumerate(zip(old_lines, new_lines)) if a != b]
        self.assertEqual(changed, [old_lines.index("Regional slang (nowhere: looked up). Spanish literature (nowhere).")])
        self.assertEqual(lint(new), [])

    def test_edit_last_section(self):
        new = edit(GOOD, "Conventions", "- Tags: `es::<area>::<topic>`.")
        self.assertTrue(new.startswith(GOOD.split("## Conventions")[0]))
        self.assertTrue(new.endswith("## Conventions\n- Tags: `es::<area>::<topic>`.\n"))


if __name__ == "__main__":
    unittest.main()
