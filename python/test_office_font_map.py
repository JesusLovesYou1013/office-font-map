"""python3 -B -m unittest discover -s python   (standard library only)"""
import json, os, unittest
from office_font_map import FontMap, Option, CORPUS

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)


class Map(unittest.TestCase):
    fm = FontMap.load()

    def test_size_of_table(self):
        self.assertEqual(len(self.fm.entries), 396)
        self.assertTrue(all(e.options for e in self.fm.entries.values()))

    def test_metric_clones_first(self):
        for office, free in [("Calibri", "Carlito"), ("Cambria", "Caladea"), ("Arial", "Liberation Sans"),
                             ("Times New Roman", "Liberation Serif"), ("Courier New", "Liberation Mono")]:
            first = self.fm.options(office)[0]
            self.assertEqual(first.family, free)
            self.assertTrue(first.metric)

    def test_case_insensitive(self):
        self.assertEqual(self.fm.options("calibri")[0].family, "Carlito")

    def test_choose_first_installed(self):
        self.assertEqual(self.fm.choose("Calibri", {"open sans"}).family, "Open Sans")
        self.assertIsNone(self.fm.choose("Calibri", set()))

    def test_metric_keeps_size(self):
        carlito = self.fm.options("Calibri")[0]
        self.assertEqual(self.fm.shown_size(11, carlito), 11)
        self.assertEqual(self.fm.office_size(11, carlito, original=11), 11)

    def test_scaled_round_trip(self):
        o = Option("Test", metric=False, size=0.87)
        shown = self.fm.shown_size(24, o)
        self.assertAlmostEqual(shown, 20.88)
        self.assertEqual(self.fm.office_size(shown, o, original=24), 24)     # untouched: exact
        self.assertEqual(self.fm.office_size(30, o, original=24), 34.5)      # edited: half points
        self.assertEqual(self.fm.office_size(0.1, o), 1.0)

    def test_office_for(self):
        self.assertEqual(self.fm.office_for("Carlito"), "Calibri")
        self.assertEqual(self.fm.office_for("Open Sans"), "")

    def test_fallback(self):
        e = self.fm.entry("Calibri")
        same = self.fm.fallback("Calibri", "X", e.advance[0])
        self.assertEqual(same.size, 1.0)
        wide = self.fm.fallback("Calibri", "X", e.advance[0] * 1.2, ascent=.9, descent=.2)
        self.assertAlmostEqual(wide.size, round(1 / 1.2, 3))
        self.assertAlmostEqual(wide.width, 1.0, places=2)
        self.assertGreater(wide.line, 0)
        self.assertIsNone(self.fm.fallback("Not A Font", "X", 0.5))

    def test_corpus_length(self):
        self.assertEqual(len(CORPUS), 719)


class Sources(unittest.TestCase):
    def test_every_downloadable_match_is_pinned(self):
        with open(os.path.join(ROOT, "data", "font-sources.json")) as f:
            src = json.load(f)
        self.assertEqual(len(src["commit"]), 40)
        for fam, e in src["families"].items():
            self.assertTrue(e["files"], fam)
            for f in e["files"]:
                self.assertEqual(len(f["sha256"]), 64)
                self.assertGreater(f["size"], 0)


if __name__ == "__main__":
    unittest.main()
