from __future__ import annotations

import csv
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import reproduce_manuscript_outputs as reproduction  # noqa: E402


EXPECTED_EXCURSIONS = {
    "P1": (36.64, 13.36, 40.29, 26.30, 10.69),
    "P2": (31.07, 5.21, 25.28, 43.52, 11.76),
    "P3": (33.68, 21.21, 45.03, 51.20, 20.05),
    "P4": (43.58, 7.39, 24.83, 74.86, 46.90),
    "P5": (44.23, 13.31, 36.17, 60.85, 21.44),
    "P6": (51.36, 18.98, 53.42, 43.03, 27.18),
    "P7": (33.97, 18.01, 47.07, 48.41, 28.86),
    "P8": (74.52, 11.39, 66.91, 54.97, 22.44),
    "P9": (17.43, 19.55, 59.60, 45.45, 13.78),
    "P10": (36.35, 7.08, 81.43, 43.66, 12.45),
}

EXPECTED_SUMMARY = {
    "shoulder_fe_deg": (40.28, 15.06, 36.50, 17.43, 74.52),
    "shoulder_aa_deg": (13.55, 5.76, 13.34, 5.21, 21.21),
    "elbow_fe_deg": (48.00, 17.95, 46.05, 24.83, 81.43),
    "wrist_fe_deg": (49.23, 12.79, 46.94, 26.30, 74.86),
    "wrist_rud_deg": (21.56, 11.00, 20.75, 10.69, 46.90),
}


class ManuscriptReproductionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.excursions, cls.cycles = reproduction.load_inputs(reproduction.DEFAULT_INPUT_DIR)

    def test_exact_ten_participant_cohort(self) -> None:
        participants = [row["participant_id"] for row in self.excursions]
        self.assertEqual(participants, list(reproduction.PARTICIPANTS))
        self.assertEqual(participants, [f"P{i}" for i in range(1, 11)])
        self.assertEqual([row["participant_id"] for row in self.cycles], participants)

    def test_all_fifty_excursions_match_reference(self) -> None:
        for row in self.excursions:
            observed = tuple(float(row[field]) for field in reproduction.EXCURSION_FIELDS[1:])
            expected = EXPECTED_EXCURSIONS[row["participant_id"]]
            for actual, target in zip(observed, expected):
                self.assertLessEqual(abs(actual - target), 0.01)
            self.assertLess(max(observed), 100.0)

    def test_cohort_summary_matches_table_reference(self) -> None:
        summary = reproduction.build_cohort_summary(self.excursions)
        for row in summary:
            observed = tuple(float(row[field]) for field in ("mean_deg", "sd_deg", "median_deg", "min_deg", "max_deg"))
            expected = EXPECTED_SUMMARY[row["variable"]]
            for actual, target in zip(observed, expected):
                self.assertLessEqual(abs(actual - target), 0.01)

    def test_cycle_traceability_counts_and_totals(self) -> None:
        self.assertTrue(all(int(row["retained_cycles"]) == 8 for row in self.cycles))
        totals = tuple(sum(int(row[field]) for row in self.cycles) for field in ("detected_cycles", "retained_cycles", "not_retained_cycles"))
        self.assertEqual(totals, (187, 80, 107))
        self.assertEqual(totals[0] - totals[1], totals[2])

    def test_reproduction_entry_point_writes_expected_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output_dir = Path(directory)
            self.assertEqual(reproduction.run(reproduction.DEFAULT_INPUT_DIR, output_dir, check=True), 0)
            expected = {
                "participant_level_excursions.csv",
                "cohort_excursion_summary.csv",
                "spearman_excursion_matrix.csv",
                "cycle_traceability_summary.csv",
                "reproduction_manifest.json",
            }
            self.assertEqual({path.name for path in output_dir.iterdir()}, expected)
            with (output_dir / "cycle_traceability_summary.csv").open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(rows[-1]["participant_id"], "TOTAL")
            self.assertEqual(rows[-1]["retained_cycles"], "80")

    def test_documentation_matches_available_scope(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        dataset_readme = (ROOT / "data" / "manuscript" / "README.md").read_text(encoding="utf-8")
        self.assertIn("data/manuscript/", readme)
        self.assertIn("cycle_traceability.csv", dataset_readme)
        self.assertIn("not included", dataset_readme.lower())
        self.assertIn("profile figures", dataset_readme.lower())


if __name__ == "__main__":
    unittest.main()
