import io
import os
import tarfile
import tempfile
import unittest

from fetch_font import extract, slug


class FontTests(unittest.TestCase):
    def test_slug(self):
        self.assertEqual(slug("Source Sans 3"), "source-sans-3")
        self.assertEqual(slug("IBM Plex Mono"), "ibm-plex-mono")
        self.assertEqual(slug("  "), "")

    def test_extract(self):
        with tempfile.TemporaryDirectory() as d:
            tgz = os.path.join(d, "p.tgz")
            with tarfile.open(tgz, "w:gz") as t:
                data = b"wOF2data"
                info = tarfile.TarInfo("package/files/x-latin-400-normal.woff2")
                info.size = len(data)
                t.addfile(info, io.BytesIO(data))
            dest = os.path.join(d, "out.woff2")
            extract(tgz, "package/files/x-latin-400-normal.woff2", dest)
            self.assertEqual(open(dest, "rb").read(), b"wOF2data")
            with self.assertRaises(KeyError):
                extract(tgz, "package/files/x-latin-700-normal.woff2", dest)


if __name__ == "__main__":
    unittest.main()
