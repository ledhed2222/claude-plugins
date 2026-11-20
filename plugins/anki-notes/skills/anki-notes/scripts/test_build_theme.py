import unittest

from build_theme import check, contrast, css, font_file, models, used_fonts

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

    def test_night_mode_and_fonts(self):
        out = css(GOOD)
        self.assertIn(".card.nightMode", out)
        self.assertIn('url("_fraunces.woff2")', out)

    def test_font_file_and_used_fonts(self):
        self.assertEqual(font_file({"family": "Source Sans 3"}), "_source-sans-3.woff2")
        self.assertEqual([f["family"] for f in used_fonts(GOOD)], ["Fraunces"])
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


if __name__ == "__main__":
    unittest.main()
