import io
import json
import os
import tarfile
import tempfile
import unittest

from fetch_font import FontError, _extract, _info, plan_files, slug

INFO = {"family": "Lit Serif", "category": "serif", "subsets": ["cyrillic", "latin"], "weights": [400, 700],
        "styles": ["italic", "normal"], "unicode": {"latin": "U+0000-00FF", "cyrillic": "U+0400-045F"}}


def make_tgz(d, members):
    path = os.path.join(d, "p.tgz")
    with tarfile.open(path, "w:gz") as t:
        for name, data in members.items():
            info = tarfile.TarInfo(name)
            info.size = len(data)
            t.addfile(info, io.BytesIO(data))
    return path


class FontTests(unittest.TestCase):
    def test_slug(self):
        self.assertEqual(slug("Source Sans 3"), "source-sans-3")
        self.assertEqual(slug("IBM Plex Mono"), "ibm-plex-mono")

    def test_plan_cyrillic_bold_italic(self):
        files = plan_files(INFO, ["latin", "cyrillic"], [400, 700], True)
        self.assertEqual(len(files), 8)
        names = {f["filename"] for f in files}
        self.assertIn("_lit-serif-cyrillic-700-italic.woff2", names)
        self.assertIn("_lit-serif-latin-400.woff2", names)
        self.assertIsNone(files[0]["url"])  # no package.json version, so no pinned url
        cyr = next(f for f in files if f["subset"] == "cyrillic")
        self.assertEqual(cyr["unicode_range"], "U+0400-045F")

    def test_plan_refuses_missing_subset_weight_italic(self):
        with self.assertRaisesRegex(FontError, "lacks greek"):
            plan_files(INFO, ["greek"], [400], False)
        with self.assertRaisesRegex(FontError, "weight"):
            plan_files(INFO, ["latin"], [300], False)
        with self.assertRaisesRegex(FontError, "italic"):
            plan_files(dict(INFO, styles=["normal"]), ["latin"], [400], True)

    def test_info_and_extract_from_package(self):
        with tempfile.TemporaryDirectory() as d:
            meta = {"family": "Lit Serif", "category": "serif", "subsets": ["latin"], "weights": [400], "styles": ["normal"]}
            tgz = make_tgz(d, {"package/package.json": json.dumps({"name": "@fontsource/lit-serif", "version": "5.2.8"}).encode(),
                               "package/metadata.json": json.dumps(meta).encode(),
                               "package/unicode.json": json.dumps({"latin": "U+0000-00FF"}).encode(),
                               "package/files/lit-serif-latin-400-normal.woff2": b"wOF2"})
            info = _info(tgz)
            self.assertEqual((info["category"], info["unicode"]["latin"]), ("serif", "U+0000-00FF"))
            files = plan_files(info, ["latin"], [400], False)
            self.assertEqual(files[0]["url"], "https://cdn.jsdelivr.net/npm/@fontsource/lit-serif@5.2.8/files/lit-serif-latin-400-normal.woff2")
            _extract(tgz, files, d)
            self.assertEqual(open(os.path.join(d, "_lit-serif-latin-400.woff2"), "rb").read(), b"wOF2")


if __name__ == "__main__":
    unittest.main()
