import unittest

from both_servers import raw, run_script
from render_note import check
from replies import LOCAL, REMOTE

_BASIC = {"Card 1": {"Front": "{{Front}}", "Back": "{{FrontSide}}<hr id=answer>{{Back}}"}}
_CLOZE = {"Cloze": {"Front": "{{cloze:Text}}", "Back": "{{cloze:Text}}<br />{{Extra}}"}}
_WORD = {"Palabra": "se dio cuenta", "Frase": "Ella se dio cuenta del error.", "Pista": "realized", "Fuente": ""}


def _errors(templates, note):
    return [m for s, m in check(templates, note)[0] if s == "error"]


class EvalCaseTests(unittest.TestCase):
    """nt-no-leak: no front shows its answer; a hidden-answer back doesn't reuse {{FrontSide}}."""

    def test_basic_is_clean(self):
        self.assertEqual(_errors(_BASIC, {"Front": "Which eval step costs more: inference or scoring?", "Back": "Inference"}), [])

    def test_cloze_cards(self):
        findings, shown = check(_CLOZE, {"Text": "precision {{c1::rises}}, recall {{c2::falls}}", "Extra": ""})
        self.assertEqual([s for s in findings if s[0] == "error"], [])
        self.assertEqual([label for label, _, _ in shown], ["Cloze c1", "Cloze c2"])
        self.assertEqual(shown[0][1], "precision [...], recall falls")

    def test_cloze_leak(self):
        note = {"Text": "Recall: share of true positives found. {{c1::Recall}} drops when gold labels are wrong.", "Extra": ""}
        self.assertTrue(any("front shows its answer" in m for m in _errors(_CLOZE, note)))

    def test_production_front_leaks_sentence(self):
        produce = {"Producción": {"Front": "{{Frase}}<br />{{Pista}}", "Back": "{{FrontSide}}<hr id=answer>{{Palabra}}"}}
        self.assertTrue(any("front shows its answer 'se dio cuenta'" in x for x in _errors(produce, _WORD)))

    def test_scripted_front_with_frontside_back(self):
        produce = {"Producción": {"Front": "{{Frase}}<script>(function(){})()</script>{{Pista}}",
                                  "Back": "{{FrontSide}}<hr id=answer>{{Palabra}}"}}
        self.assertTrue(any("FrontSide" in x for x in _errors(produce, _WORD)))

    def test_production_fresh_back(self):
        produce = {"Producción": {
            "Front": "<div id=s>{{Frase}}</div><script>(function(){/* blank {{Palabra}} */})()</script>{{Pista}}",
            "Back": "{{Frase}}<hr id=answer><b>{{Palabra}}</b>{{#Fuente}}<small>{{Fuente}}</small>{{/Fuente}}"}}
        findings, shown = check(produce, _WORD)
        self.assertTrue(any("JavaScript" in m for s, m in findings if s == "warn"))
        self.assertNotIn("Fuente", shown[0][2])

    def test_empty_optional_section(self):
        t = {"Card 1": {"Front": "{{Front}}{{#Hint}} ({{Hint}}){{/Hint}}", "Back": "{{Back}}"}}
        _, shown = check(t, {"Front": "Q?", "Back": "A", "Hint": ""})
        self.assertEqual(shown[0][1], "Q?")


class FeedbackFieldTests(unittest.TestCase):
    def test_feedback_never_in_a_template(self):
        note = {"Front": "Which tier is bottled?", "Back": "The solera", "Feedback": "too vague"}
        self.assertEqual(_errors(_BASIC, note), [])
        shown = {"Card 1": {"Front": "{{Front}}", "Back": "{{FrontSide}}<hr id=answer>{{Back}}<br>{{Feedback}}"}}
        self.assertTrue(any("Feedback" in m for m in _errors(shown, note)))

    def test_missing_feedback_is_a_warning(self):
        findings = check(_BASIC, {"Front": "Which tier is bottled?", "Back": "The solera"})[0]
        self.assertIn("warn", [s for s, m in findings if "Feedback" in m])


class RenderSavedTemplatesContract:
    """render_note.py --templates with each server's saved note-type reply."""
    server = None

    def test_cli_renders_basic(self):
        r = run_script("render_note.py", "note.json", "--templates", "t.json",
                       files={"note.json": {"Front": "Which eval step costs more: inference or scoring?", "Back": "Inference"},
                              "t.json": raw(self.server, "templates")})
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("front: Which eval step costs more: inference or scoring?", r.stdout)


class LocalRenderSavedTemplates(RenderSavedTemplatesContract, unittest.TestCase):
    server = LOCAL


class RemoteRenderSavedTemplates(RenderSavedTemplatesContract, unittest.TestCase):
    server = REMOTE


if __name__ == "__main__":
    unittest.main()
