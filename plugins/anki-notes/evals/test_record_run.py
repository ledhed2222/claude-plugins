import unittest

from record_run import check, diff, entry


def run(started, scores, commit="abc"):
    return {"started": started, "commit": commit, "claude": "2", "cost_usd": 1.0, "partial": False,
            "arms": "with", "runs_per_case": 3, "scores": scores, "note": ""}


class RecordRunTests(unittest.TestCase):
    def test_entry_from_result(self):
        result = {"startedAt": "2026-11-21T00:00:00Z", "claudeVersion": "2.1", "costUsd": 1.234, "partial": True,
                  "cases": [{"name": "a", "runsPerCase": 3, "aggregates": {"score": 0.6666666},
                             "arms": {"with": [{}], "without": []}}]}
        e = entry(result, "abc", "n")
        self.assertEqual((e["scores"], e["arms"], e["cost_usd"], e["partial"]), ({"a": 0.6667}, "with", 1.23, True))
        self.assertEqual(check([e]), [])

    def test_diff_uses_latest_score_per_case(self):
        history = [run("1", {"a": 0.5, "b": 1.0}, "old"), run("2", {"a": 1.0}, "rerun")]
        lines = diff(run("3", {"a": 1.0, "b": 0.5, "c": 1.0}), history)
        self.assertEqual(lines[0], "overall on 2 shared cases: 1.000 -> 0.750; passing 2 -> 1")
        self.assertIn("(was old)", lines[1])
        self.assertTrue(lines[1].lstrip().startswith("b "))
        self.assertIn("c", lines[2])

    def test_check(self):
        bad = run("2", {"a": 2})
        bad.pop("note")
        problems = check([bad, run("1", {})])
        self.assertTrue(any("note" in p for p in problems))
        self.assertTrue(any("0 to 1" in p for p in problems))
        self.assertTrue(any("order" in p for p in problems))


if __name__ == "__main__":
    unittest.main()
