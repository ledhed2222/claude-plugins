import unittest

from format_mix import mix, note_format
from both_servers import deck_notes, load, raw, run_script
from replies import notes
from replies import LOCAL, REMOTE


def _note(model="Basic", kind="type::definition", **fields):
    return {"id": 1, "model": model, "tags": ["aie::evals::cost", kind], "fields": dict(fields)}


class FormatMixTests(unittest.TestCase):
    def test_format(self):
        self.assertEqual(note_format(_note(Front="What is recall?")), "Basic type::definition")
        self.assertEqual(note_format(_note("AI Engineering · Cloze", "type::formula")), "Cloze type::formula")
        self.assertEqual(note_format(_note(Front='<img src="roc.png">')), "Basic type::definition +media")
        self.assertEqual(note_format(_note("Reconocimiento", "src::x", Audio="[sound:hola.mp3]")), "Reconocimiento type::- +media")

    def test_mix_orders_by_share(self):
        notes = [_note()] * 9 + [_note(kind="type::application")]
        self.assertEqual(mix(notes), [("Basic type::definition", 0.9), ("Basic type::application", 0.1)])




class FormatMixContract:
    """The fixture deck read through format_mix.py's CLI, from each server's saved replies."""
    server = None

    def test_cli_reports_the_mix(self):
        files = {"r1.json": raw(self.server, "deck_notes")}
        r = run_script("format_mix.py", *files, files=files)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(r.stdout.splitlines()[-1], "4 notes; most common is Basic type::- at 25%, within the 85% target")

    def test_formats(self):
        self.assertEqual(sorted(note_format(n) for n in deck_notes(self.server)),
                         ["Basic type::-", "Basic type::contrast +media", "Basic type::definition", "Cloze type::-"])


class LocalFormatMix(FormatMixContract, unittest.TestCase):
    server = LOCAL


class RemoteFormatMix(FormatMixContract, unittest.TestCase):
    server = REMOTE

    def test_summary_pages_name_their_note_types(self):
        """Without include_fields: each item names its type, but media past the first field is missed."""
        rows = notes([load(REMOTE, "search")])
        self.assertEqual(sorted(note_format(n) for n in rows),
                         ["Basic type::-", "Basic type::contrast", "Basic type::definition", "Cloze type::-"])

    def test_older_summary_pages_take_names_from_a_note_types_reply(self):
        from replies import note_type_names
        self.assertEqual({n["model"] for n in notes([load(REMOTE, "search_without_names")])}, {""})
        rows = notes([load(REMOTE, "search_without_names")], note_type_names([load(REMOTE, "note_types")]))
        self.assertEqual(sorted(note_format(n) for n in rows),
                         ["Basic type::-", "Basic type::contrast", "Basic type::definition", "Cloze type::-"])

    def test_recorded_full_page_sees_media_in_the_back(self):
        self.assertIn("Basic type::application +media", [note_format(n) for n in notes([load(REMOTE, "search_full")])])


if __name__ == "__main__":
    unittest.main()
