import unittest

from render_note import check

BASIC = {"Card 1": {"Front": "{{Front}}", "Back": "{{FrontSide}}<hr id=answer>{{Back}}"}}
CLOZE = {"Cloze": {"Front": "{{cloze:Text}}", "Back": "{{cloze:Text}}<br />{{Extra}}"}}
WORD = {"Palabra": "se dio cuenta", "Frase": "Ella se dio cuenta del error.", "Pista": "realized", "Fuente": ""}


def errors(templates, note):
    return [m for s, m in check(templates, note)[0] if s == "error"]


class EvalCaseTests(unittest.TestCase):
    """nt-no-leak: no front shows its answer; a hidden-answer back doesn't reuse {{FrontSide}}."""

    def test_basic_is_clean(self):
        self.assertEqual(errors(BASIC, {"Front": "Which eval step costs more: inference or scoring?", "Back": "Inference"}), [])

    def test_cloze_cards(self):
        findings, shown = check(CLOZE, {"Text": "precision {{c1::rises}}, recall {{c2::falls}}", "Extra": ""})
        self.assertEqual([s for s in findings if s[0] == "error"], [])
        self.assertEqual([label for label, _, _ in shown], ["Cloze c1", "Cloze c2"])
        self.assertEqual(shown[0][1], "precision [...], recall falls")

    def test_cloze_leak(self):
        note = {"Text": "Recall: share of true positives found. {{c1::Recall}} drops when gold labels are wrong.", "Extra": ""}
        self.assertTrue(any("front shows its answer" in m for m in errors(CLOZE, note)))

    def test_production_front_leaks_sentence(self):
        produce = {"Producción": {"Front": "{{Frase}}<br />{{Pista}}", "Back": "{{FrontSide}}<hr id=answer>{{Palabra}}"}}
        self.assertTrue(any("front shows its answer 'se dio cuenta'" in x for x in errors(produce, WORD)))

    def test_scripted_front_with_frontside_back(self):
        produce = {"Producción": {"Front": "{{Frase}}<script>(function(){})()</script>{{Pista}}",
                                  "Back": "{{FrontSide}}<hr id=answer>{{Palabra}}"}}
        self.assertTrue(any("FrontSide" in x for x in errors(produce, WORD)))

    def test_production_fresh_back(self):
        produce = {"Producción": {
            "Front": "<div id=s>{{Frase}}</div><script>(function(){/* blank {{Palabra}} */})()</script>{{Pista}}",
            "Back": "{{Frase}}<hr id=answer><b>{{Palabra}}</b>{{#Fuente}}<small>{{Fuente}}</small>{{/Fuente}}"}}
        findings, shown = check(produce, WORD)
        self.assertTrue(any("JavaScript" in m for s, m in findings if s == "warn"))
        self.assertNotIn("Fuente", shown[0][2])

    def test_empty_optional_section(self):
        t = {"Card 1": {"Front": "{{Front}}{{#Hint}} ({{Hint}}){{/Hint}}", "Back": "{{Back}}"}}
        _, shown = check(t, {"Front": "Q?", "Back": "A", "Hint": ""})
        self.assertEqual(shown[0][1], "Q?")


if __name__ == "__main__":
    unittest.main()
