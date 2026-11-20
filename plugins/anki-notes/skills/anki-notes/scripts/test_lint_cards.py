import unittest

from lint_cards import lint

TAGS = ["aie::evals::recall", "type::definition", "src::test"]


def basic(front, back, tags=TAGS):
    return {"model": "Basic", "fields": {"Front": front, "Back": back}, "tags": tags}


def msgs(card, **kw):
    return [m for _, m in lint(card, **kw)]


class LintTests(unittest.TestCase):
    def test_clean_card(self):
        self.assertEqual(lint(basic("Which eval step costs more: inference or scoring?", "<b>Inference.</b>")), [])

    def test_yes_no(self):
        self.assertTrue(any("yes/no" in m for m in msgs(basic("Does temperature 0 make outputs identical?", "No."))))

    def test_whole_set_and_example(self):
        self.assertTrue(any("whole set" in m for m in msgs(basic("Name the four cells of a confusion matrix.", "TP, FP, FN, TN"))))
        self.assertTrue(any("whole set" in m for m in msgs(basic("Give an example of a ranking metric.", "NDCG"))))

    def test_answer_in_question(self):
        self.assertTrue(any("answer word" in m for m in msgs(basic("Why does a harmonic mean punish imbalance?", "A harmonic mean is dominated by the smaller value."))))

    def test_why_example_line_is_not_the_answer(self):
        long_extra = "<br><br><small><b>Why/Example:</b> " + "word " * 40 + "</small>"
        self.assertEqual([m for m in msgs(basic("Which costs more: inference or scoring?", "<b>Inference.</b>" + long_extra)) if "words" in m], [])

    def test_long_back(self):
        self.assertTrue(any("words" in m for m in msgs(basic("What is X?", "word " * 30))))

    def test_cloze(self):
        ok = {"model": "Cloze", "fields": {"Text": "precision {{c1::rises}}, recall {{c2::falls}}", "Extra": ""}, "tags": TAGS}
        self.assertEqual(lint(ok), [])
        bad = {"model": "Cloze", "fields": {"Text": "precision {{c1::rises}}, recall {{c3::falls}}", "Extra": ""}, "tags": TAGS}
        self.assertTrue(any("not 1..n" in m for m in msgs(bad)))
        none = {"model": "Cloze", "fields": {"Text": "no blanks", "Extra": ""}, "tags": TAGS}
        self.assertTrue(any("no {{c1" in m for m in msgs(none)))

    def test_tags(self):
        self.assertTrue(any("type::" in m for m in msgs(basic("Q?", "A.", tags=["src::x"]))))
        self.assertTrue(any("src::" in m for m in msgs(basic("Q?", "A.", tags=["type::formula"]))))
        self.assertTrue(any("es::" in m for m in msgs(basic("Q?", "A.", tags=TAGS), prefix="es")))

    def test_empty_and_void_tags(self):
        self.assertTrue(any("empty" in m for m in msgs(basic("", "A."))))
        self.assertTrue(any("void" in m for m in msgs(basic("Q?", "A.<br>B."))))


if __name__ == "__main__":
    unittest.main()
