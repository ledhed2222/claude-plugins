import unittest

from lint_cards import lint, parse_cards

_TAGS = ["aie::evals::recall", "type::definition", "src::test"]


def _basic(front, back, tags=_TAGS):
    return {"model": "Basic", "fields": {"Front": front, "Back": back}, "tags": tags}


def _msgs(card, **kw):
    return [m for _, m in lint(card, **kw)]


class LintTests(unittest.TestCase):
    def test_clean_card(self):
        self.assertEqual(lint(_basic("Which eval step costs more: inference or scoring?", "<b>Inference.</b>")), [])

    def test_yes_no(self):
        self.assertTrue(any("yes/no" in m for m in _msgs(_basic("Does temperature 0 make outputs identical?", "No."))))

    def test_whole_set_and_example(self):
        self.assertTrue(any("whole set" in m for m in _msgs(_basic("Name the four cells of a confusion matrix.", "TP, FP, FN, TN"))))
        self.assertTrue(any("whole set" in m for m in _msgs(_basic("Give an example of a ranking metric.", "NDCG"))))

    def test_answer_in_question(self):
        self.assertTrue(any("answer word" in m for m in _msgs(_basic("Why does a harmonic mean punish imbalance?", "A harmonic mean is dominated by the smaller value."))))

    def test_why_example_line_is_not_the_answer(self):
        long_extra = "<br /><br /><small><b>Why/Example:</b> " + "word " * 40 + "</small>"
        self.assertEqual([m for m in _msgs(_basic("Which costs more: inference or scoring?", "<b>Inference.</b>" + long_extra)) if "words" in m], [])

    def test_long_back(self):
        self.assertTrue(any("words" in m for m in _msgs(_basic("What is X?", "word " * 30))))

    def test_cloze(self):
        ok = {"model": "Cloze", "fields": {"Text": "precision {{c1::rises}}, recall {{c2::falls}}", "Extra": ""}, "tags": _TAGS}
        self.assertEqual(lint(ok), [])
        bad = {"model": "Cloze", "fields": {"Text": "precision {{c1::rises}}, recall {{c3::falls}}", "Extra": ""}, "tags": _TAGS}
        self.assertTrue(any("not 1..n" in m for m in _msgs(bad)))
        none = {"model": "Cloze", "fields": {"Text": "no blanks", "Extra": ""}, "tags": _TAGS}
        self.assertTrue(any("no {{c1" in m for m in _msgs(none)))
        themed = dict(ok, model="AI Engineering · Cloze")
        self.assertEqual(lint(themed), [])

    def test_tags(self):
        self.assertTrue(any("type::" in m for m in _msgs(_basic("Q?", "A.", tags=["src::x"]))))
        self.assertTrue(any("src::" in m for m in _msgs(_basic("Q?", "A.", tags=["type::formula"]))))
        self.assertTrue(any("es::" in m for m in _msgs(_basic("Q?", "A.", tags=_TAGS), prefix="es")))

    def test_empty_and_void_tags(self):
        self.assertTrue(any("empty" in m for m in _msgs(_basic("", "A."))))
        self.assertTrue(any("void" in m for m in _msgs(_basic("Q?", "A.<br>B."))))

    def test_skip(self):
        card = _basic("Does temperature 0 make outputs identical?", "No.")
        self.assertEqual([m for m in _msgs(card, skip=("yes-no",)) if "yes/no" in m], [])


class EvalCaseTests(unittest.TestCase):
    """Eval cases from the formulation PR that a script can grade without an LLM."""

    def test_no_giveaway(self):
        leak = _basic("Why is the harmonic mean used for F1 instead of the arithmetic mean?",
                     "<b>The harmonic mean</b> is pulled toward the lower of precision and recall.")
        self.assertTrue(any(m.startswith("answer-in-question") for m in _msgs(leak)))
        fixed = _basic("F1 combines precision and recall. Why is it pulled down hard when one of them is low?",
                      "<b>It uses a harmonic mean.</b>")
        self.assertEqual(lint(fixed), [])

    def test_closed_list(self):
        whole = _basic("Name all four cells of a confusion matrix.", "TP, FP, FN, TN")
        self.assertTrue(any(m.startswith("whole-set") for m in _msgs(whole)))
        ordered = {"model": "Cloze", "tags": _TAGS, "fields": {"Extra": "", "Text":
                   "Confusion matrix cells: {{c1::true positive}}, {{c2::false positive}}, {{c3::false negative}}, {{c4::true negative}}"}}
        self.assertEqual(lint(ordered), [])

    def test_json_list(self):
        self.assertEqual(parse_cards('[{"a": 1}]'), [(1, {"a": 1})])


if __name__ == "__main__":
    unittest.main()
