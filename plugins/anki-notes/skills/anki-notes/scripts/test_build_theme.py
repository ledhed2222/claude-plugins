import unittest

from build_theme import check, compare_page, contrast, css, font_faces, models, used_fonts

GOOD = {
    "deck": "Spanish", "mood": "warm",
    "fonts": {"body": None, "accent": {"family": "Fraunces"}},
    "light": {"bg": "#FBF3E8", "text": "#3B2316", "accent": "#A24A26", "rule": "#E8CDB4"},
    "night": {"bg": "#221A15", "text": "#F3E6D8", "accent": "#F0A07A", "rule": "#4A3A30"},
    "motion": False,
}


class ThemeTests(unittest.TestCase):
    def test_contrast_extremes(self):
        self.assertAlmostEqual(contrast("#000000", "#FFFFFF"), 21.0, places=1)
        self.assertAlmostEqual(contrast("#777777", "#777777"), 1.0)

    def test_good_theme_passes(self):
        self.assertEqual(check(GOOD), [])

    def test_low_contrast_fails_in_either_mode(self):
        bad = dict(GOOD, night=dict(GOOD["night"], accent="#3A2A20"))
        self.assertTrue(any("night: accent" in p for p in check(bad)))

    def test_missing_key(self):
        bad = dict(GOOD, light={"bg": "#FFFFFF"})
        self.assertTrue(any("missing" in p for p in check(bad)))

    def test_motion_is_opt_in_and_respects_reduced_motion(self):
        self.assertNotIn("animation", css(GOOD))
        moving = css(dict(GOOD, motion=True))
        self.assertIn("prefers-reduced-motion: no-preference", moving)
        self.assertNotIn("infinite", moving)

    def test_night_mode(self):
        self.assertIn(".card.nightMode", css(GOOD))

    def test_font_faces_carry_unicode_range_weight_style(self):
        files = [{"family": "Literata", "filename": "_literata-cyrillic-700-italic.woff2", "weight": 700,
                  "style": "italic", "unicode_range": "U+0400-045F"}]
        face = font_faces(files)
        self.assertIn('src: url("_literata-cyrillic-700-italic.woff2") format("woff2")', face)
        self.assertIn("font-weight: 700; font-style: italic;", face)
        self.assertIn("unicode-range: U+0400-045F;", face)
        self.assertIn(face, css(GOOD, files))

    def test_used_fonts_defaults(self):
        self.assertEqual(used_fonts(GOOD), [("accent", "Fraunces", [400], False)])
        both = dict(GOOD, fonts={"body": {"family": "Literata", "italic": True}, "accent": None})
        self.assertEqual(used_fonts(both), [("body", "Literata", [400, 700], True)])
        self.assertEqual(used_fonts(dict(GOOD, fonts=None)), [])

    def test_no_inherit_in_font_lists(self):
        # `inherit` is invalid inside a font-family list and silently drops the declaration
        self.assertNotRegex(css(GOOD), r"font-family:[^;]*inherit")
        self.assertIn('font-family: "Fraunces", var(--body-font)', css(GOOD))

    def test_models_keep_stock_fields(self):
        basic, cloze = models(GOOD, "")
        self.assertEqual(basic["in_order_fields"], ["Front", "Back"])
        self.assertEqual(cloze["in_order_fields"], ["Text", "Extra"])
        self.assertTrue(cloze["is_cloze"])
        self.assertEqual(basic["model_name"], "Spanish · Basic")

    def test_no_front_shows_the_answer(self):
        for m in models(GOOD, ""):
            for t in m["card_templates"]:
                self.assertNotIn("{{Back}}", t["Front"])
                self.assertNotIn("{{Extra}}", t["Front"])

    def test_compare_page_frames_each_preview_relative_to_the_page(self):
        page = compare_page("/tmp/themes/compare.html", ["/tmp/themes/literata-paper", "/tmp/themes/lora/"])
        self.assertIn('<h2>literata-paper</h2><iframe src="literata-paper/preview.html">', page)
        self.assertIn('<h2>lora</h2><iframe src="lora/preview.html">', page)


if __name__ == "__main__":
    unittest.main()
