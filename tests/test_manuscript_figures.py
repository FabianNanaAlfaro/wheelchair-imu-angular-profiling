from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT / "scripts"))

import generate_manuscript_figures as figures  # noqa: E402
import reproduce_manuscript_outputs as reproduction  # noqa: E402
from manuscript_variables import PARTICIPANTS, VARIABLE_FIELDS, VARIABLE_LABELS  # noqa: E402


EXPECTED_SPEARMAN = np.asarray(
    [
        [1.00000, -0.17576, 0.07879, 0.23636, 0.45455],
        [-0.17576, 1.00000, 0.21212, -0.06667, 0.15152],
        [0.07879, 0.21212, 1.00000, -0.22424, -0.07879],
        [0.23636, -0.06667, -0.22424, 1.00000, 0.62424],
        [0.45455, 0.15152, -0.07879, 0.62424, 1.00000],
    ],
    dtype=float,
)


class ManuscriptFigureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.excursions, cls.cycles = reproduction.load_inputs(reproduction.DEFAULT_INPUT_DIR)
        cls.values = np.asarray(
            [[float(row[field]) for field in VARIABLE_FIELDS] for row in cls.excursions],
            dtype=float,
        )

    def test_canonical_order_drives_labels_and_columns(self) -> None:
        self.assertEqual(tuple(VARIABLE_FIELDS), tuple(reproduction.EXCURSION_FIELDS[1:]))
        self.assertEqual(tuple(VARIABLE_LABELS), tuple(variable.label for variable in figures.VARIABLES))
        self.assertEqual(list(PARTICIPANTS), [row["participant_id"] for row in self.excursions])

    def test_figure_5_values_and_medians(self) -> None:
        self.assertEqual(self.values.shape, (10, 5))
        expected_medians = [
            figures.rounded_report_value(value)
            for value in (36.50, 13.34, 46.05, 46.93, 20.75)
        ]
        self.assertTrue(np.allclose(np.round(self.values, 2), self.values, atol=0.005))
        observed_medians = [
            figures.rounded_report_value(value)
            for value in np.median(self.values, axis=0)
        ]
        self.assertEqual(observed_medians, expected_medians)

    def test_figure_6_matrix_is_computed_in_canonical_order(self) -> None:
        matrix = figures.compute_spearman_matrix(self.values)
        self.assertEqual(matrix.shape, (5, 5))
        self.assertTrue(np.allclose(matrix, matrix.T, atol=1e-12))
        self.assertTrue(np.allclose(np.diag(matrix), np.ones(5), atol=1e-12))
        self.assertTrue(np.allclose(matrix, EXPECTED_SPEARMAN, atol=1e-5))
        target_order, target, tolerance = figures.load_regression_target()
        self.assertEqual(target_order, VARIABLE_FIELDS)
        self.assertTrue(np.allclose(target, EXPECTED_SPEARMAN, atol=tolerance))

    def test_figure_generator_outputs_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output_dir = root / "outputs"
            asset_dir = root / "assets"
            manifest = figures.run(
                input_dir=reproduction.DEFAULT_INPUT_DIR,
                output_dir=output_dir,
                asset_dir=asset_dir,
                check=True,
                publish_assets=True,
            )
            expected_figures = {
                "figure_5_excursions.png",
                "figure_5_excursions.pdf",
                "figure_5_excursions.svg",
                "figure_6_spearman.png",
                "figure_6_spearman.pdf",
                "figure_6_spearman.svg",
            }
            self.assertEqual({path.name for path in output_dir.iterdir() if path.name != "figure_manifest.json"}, expected_figures)
            self.assertEqual({path.name for path in asset_dir.iterdir()}, expected_figures)
            self.assertEqual(manifest["participants"], 10)
            self.assertEqual([item["field"] for item in manifest["variable_order"]], list(VARIABLE_FIELDS))
            self.assertFalse(manifest["profile_figures_generated"])
            self.assertFalse(manifest["retained_cycle_data_available"])
            self.assertEqual(set(manifest["figures"]), {"figure_5", "figure_6"})
            self.assertEqual(set(manifest["unsupported_figures"]), {"figure_2", "figure_3", "figure_4"})

    def test_figure_generation_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = root / "first"
            second = root / "second"
            figures.run(reproduction.DEFAULT_INPUT_DIR, first, root / "assets_first", check=True)
            figures.run(reproduction.DEFAULT_INPUT_DIR, second, root / "assets_second", check=True)
            for name in (
                "figure_5_excursions.png",
                "figure_5_excursions.pdf",
                "figure_5_excursions.svg",
                "figure_6_spearman.png",
                "figure_6_spearman.pdf",
                "figure_6_spearman.svg",
            ):
                self.assertEqual((first / name).read_bytes(), (second / name).read_bytes(), name)

    def test_manifest_contains_no_private_filesystem_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output_dir = Path(directory)
            figures.run(reproduction.DEFAULT_INPUT_DIR, output_dir, output_dir / "assets", check=True)
            manifest_text = (output_dir / "figure_manifest.json").read_text(encoding="utf-8")
            manifest = json.loads(manifest_text)
            self.assertNotIn("C:\\Users", manifest_text)
            self.assertNotIn("Desktop", manifest_text)
            self.assertEqual(manifest["input_files"].keys(), {"data/manuscript/participant_level_excursions.csv"})


if __name__ == "__main__":
    unittest.main()
