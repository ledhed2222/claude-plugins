import re
import unittest

from both_servers import check_call
from build_theme import check, compare_page, contrast, css, font_faces, models, remote_media, remote_models, used_fonts
from replies import LOCAL, REMOTE

GOOD = {
    "deck": "Spanish", "mood": "warm",
    "fonts": {"body": None, "accent": {"family": "Fraunces"}},
    "light": {"bg": "#FBF3E8", "text": "#3B2316", "accent": "#A24A26", "rule": "#E8CDB4"},
    "night": {"bg": "#221A15", "text": "#F3E6D8", "accent": "#F0A07A", "rule": "#4A3A30"},
    "motion": False,
}


_FONT = {"filename": "_fraunces-latin-400.woff2",
         "url": "https://cdn.jsdelivr.net/npm/@fontsource/fraunces@5.2.8/files/fraunces-latin-400-normal.woff2"}


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

    def test_stage_dots_imply_no_total(self):
        out = css(GOOD)
        self.assertNotIn("○", out)
        self.assertIn('[data-deck*="::03 "]::before { content: "●●● "; }', out)
        self.assertIn('[data-deck*="::06 "]::before { content: "●●●●●● "; }', out)

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
        self.assertEqual(basic["in_order_fields"], ["Front", "Back", "Feedback"])
        self.assertEqual(cloze["in_order_fields"], ["Text", "Extra", "Feedback"])
        self.assertTrue(cloze["is_cloze"])
        self.assertEqual(basic["model_name"], "Spanish · Basic")

    def test_feedback_is_last_and_in_no_template(self):
        for m in models(GOOD, ""):
            self.assertEqual(m["in_order_fields"][-1], "Feedback")
            for t in m["card_templates"]:
                self.assertNotIn("Feedback", t["Front"] + t["Back"])

    def test_no_front_shows_the_answer(self):
        for m in models(GOOD, ""):
            for t in m["card_templates"]:
                self.assertNotIn("{{Back}}", t["Front"])
                self.assertNotIn("{{Extra}}", t["Front"])

    def test_compare_page_frames_each_preview_relative_to_the_page(self):
        page = compare_page("/tmp/themes/compare.html", ["/tmp/themes/literata-paper", "/tmp/themes/lora/"])
        self.assertIn('<h2>literata-paper</h2><iframe src="literata-paper/preview.html">', page)
        self.assertIn('<h2>lora</h2><iframe src="lora/preview.html">', page)


class ThemeModelsContract:
    """The note types a theme saves, as each server's create calls, checked against its real tool schema."""
    server = None

    def create_calls(self):
        if self.server == LOCAL:
            return [{"tool": "create_model", "args": m} for m in models(GOOD, "body {}")]
        out = []
        for m in remote_models(GOOD, "body {}"):
            out += [{"tool": "anki_note_types_change_preview", "args": dict(m, operation="create")},
                    {"tool": "anki_note_types_create", "args": dict(m, confirmation_token="token")}]
        return out

    def test_both_copies_are_created(self):
        names = [c["args"].get("model_name") or c["args"].get("name") for c in self.create_calls()
                 if c["tool"] in ("create_model", "anki_note_types_create")]
        self.assertEqual(names, ["Spanish · Basic", "Spanish · Cloze"])

    def restyle_calls(self):
        """Applying a rebuilt theme's CSS to both of its note types, as note-types.md says."""
        if self.server == LOCAL:
            return [{"tool": "update_model_styling", "args": {"model_name": m["model_name"], "css": m["css"]}} for m in models(GOOD, "body {}")]
        out = []
        for type_id, m in zip((1795478372492, 1795478372496), remote_models(GOOD, "body {}")):
            args = {"note_type_id": type_id, "css": m["css"]}  # only the CSS: the server leaves the rest as it is
            out += [{"tool": "anki_note_types_change_preview", "args": dict(args, operation="update")},
                    {"tool": "anki_note_types_update", "args": dict(args, confirmation_token="token")}]
        return out

    def test_restyle_calls_match_the_schema(self):
        calls = self.restyle_calls()
        self.assertEqual(len(calls), 2 if self.server == LOCAL else 4)
        self.assertEqual([p for c in calls for p in check_call(self.server, c)], [])

    def media_calls(self):
        """Storing a theme's font files, as media.json (local) or media-remote.json (remote) gives them."""
        if self.server == LOCAL:
            return [{"tool": "store_media_file", "args": {"filename": "_fraunces-latin-400.woff2", "path": "/tmp/t/_fraunces-latin-400.woff2"}}]
        return [{"tool": "anki_media_store", "args": remote_media(_FONT)}]

    def test_media_calls_match_the_schema(self):
        self.assertEqual([p for c in self.media_calls() for p in check_call(self.server, c)], [])

    def test_create_calls_match_the_schema(self):
        calls = self.create_calls()
        self.assertTrue(calls)
        self.assertEqual([p for c in calls for p in check_call(self.server, c)], [])

    def test_basic_copy_keeps_stock_fields_and_templates(self):
        basic = next(c["args"] for c in self.create_calls() if "Basic" in str(c["args"].get("model_name") or c["args"].get("name")))
        local = models(GOOD, "body {}")[0]
        if self.server == LOCAL:
            self.assertEqual(basic, local)
        else:
            self.assertEqual((basic["name"], basic["fields"], basic["css"]), (local["model_name"], local["in_order_fields"], local["css"]))
            self.assertEqual([(t["question_format"], t["answer_format"]) for t in basic["templates"]],
                             [(t["Front"], t["Back"]) for t in local["card_templates"]])


class LocalThemeModels(ThemeModelsContract, unittest.TestCase):
    server = LOCAL


class RemoteThemeModels(ThemeModelsContract, unittest.TestCase):
    server = REMOTE

    def test_media_is_a_pinned_url_keyed_on_it(self):
        args = remote_media(_FONT)
        self.assertEqual(set(args), {"filename", "url", "idempotency_key"})
        self.assertRegex(args["url"], r"^https://cdn\.jsdelivr\.net/npm/@fontsource/fraunces@\d+\.\d+\.\d+/files/")
        other = remote_media(dict(_FONT, url=_FONT["url"].replace("5.2.8", "5.2.9")))
        self.assertNotEqual(args["idempotency_key"], other["idempotency_key"])
        self.assertEqual(args, remote_media(_FONT))

    def test_cloze_copy_is_created_as_cloze(self):
        kinds = {m["name"]: m["kind"] for m in remote_models(GOOD, "")}
        self.assertEqual(kinds, {"Spanish · Basic": "standard", "Spanish · Cloze": "cloze"})

    def test_cloze_copy_has_one_cloze_template(self):
        """anki-sync-mcp refuses a cloze type without exactly one template using {{cloze:<field>}}."""
        cloze = next(m for m in remote_models(GOOD, "") if m["kind"] == "cloze")
        self.assertEqual(len(cloze["templates"]), 1)
        # the literal form only (anki-sync-mcp#30): a filter chain like {{text:cloze:Text}} is refused
        named = re.findall(r"\{\{cloze:([^}:]+)\}\}", cloze["templates"][0]["question_format"])
        self.assertTrue(named)
        self.assertTrue(set(named) <= set(cloze["fields"]))
        self.assertNotRegex(cloze["templates"][0]["question_format"], r"\{\{[^}]*:cloze:")


if __name__ == "__main__":
    unittest.main()
