from __future__ import annotations

import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from wheelchair_pipeline.signal import butterworth_lowpass  # noqa: E402
from wheelchair_pipeline.synthetic import write_synthetic_trial  # noqa: E402
from wheelchair_pipeline.workflow import PipelineConfig, run_pipeline  # noqa: E402
from wheelchair_pipeline.phases import normalize_phase  # noqa: E402


class PublicPipelineTests(unittest.TestCase):
    def test_demo_runs_end_to_end_with_expected_shapes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path = root / "imu_trial.csv"
            output_path = root / "outputs"
            time = write_synthetic_trial(input_path)
            result = run_pipeline(
                input_path,
                output_path,
                PipelineConfig(
                    neutral_window=(0.2, 1.0),
                    analysis_window=(1.0, 2.5),
                    phases=(("propulsion", 0.0, 2.0), ("recovery", 2.0, 3.99)),
                ),
                write_plot=False,
            )

            self.assertEqual(result.samples, time.size)
            self.assertEqual(result.samples, 400)
            self.assertTrue(result.axis_used.endswith(":X"))
            self.assertAlmostEqual(result.sampling_hz, 100.0, places=6)

            with (output_path / "phase_normalized.csv").open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 200)
            self.assertEqual(rows[0]["phase"], "propulsion")
            self.assertEqual(rows[100]["phase"], "recovery")
            self.assertTrue(all(np.isfinite(float(row["angle_deg"])) for row in rows))

            manifest = json.loads((output_path / "pipeline_manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["parameters"]["phase_points"], 100)
            self.assertEqual(manifest["derived"]["axis_used"], result.axis_used)

    def test_filter_rejects_cutoff_at_or_above_nyquist(self) -> None:
        time = np.arange(0.0, 1.0, 0.01)
        values = np.sin(2 * np.pi * 2 * time)
        with self.assertRaises(ValueError):
            butterworth_lowpass(values, time, cutoff_hz=50.0, order=4)

    def test_phase_boundaries_are_interpolated(self) -> None:
        time = np.arange(0.0, 1.01, 0.1)
        values = 10.0 * time
        normalized = normalize_phase(time, {"angle_deg": values}, 0.15, 0.85, points=3)
        np.testing.assert_allclose(normalized["angle_deg"], [1.5, 5.0, 8.5])


if __name__ == "__main__":
    unittest.main()
