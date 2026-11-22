import unittest

from format_mix import mix, note_format


def _note(model="Basic", kind="type::definition", **fields):
    return {"modelName": model, "tags": ["aie::evals::cost", kind], "fields": {k: {"value": v} for k, v in fields.items()}}


class FormatMixTests(unittest.TestCase):
    def test_format(self):
        self.assertEqual(note_format(_note(Front="What is recall?")), "Basic type::definition")
        self.assertEqual(note_format(_note("AI Engineering · Cloze", "type::formula")), "Cloze type::formula")
        self.assertEqual(note_format(_note(Front='<img src="roc.png">')), "Basic type::definition +media")
        self.assertEqual(note_format(_note("Reconocimiento", "src::x", Audio="[sound:hola.mp3]")), "Reconocimiento type::- +media")

    def test_mix_orders_by_share(self):
        notes = [_note()] * 9 + [_note(kind="type::application")]
        self.assertEqual(mix(notes), [("Basic type::definition", 0.9), ("Basic type::application", 0.1)])


if __name__ == "__main__":
    unittest.main()
