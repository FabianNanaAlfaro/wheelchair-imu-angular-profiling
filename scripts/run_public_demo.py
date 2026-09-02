"""Run the complete public demo without requiring any private study file."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from wheelchair_pipeline.synthetic import write_synthetic_trial  # noqa: E402
from wheelchair_pipeline.workflow import PipelineConfig, run_pipeline  # noqa: E402


def main() -> int:
    input_path = ROOT / "examples" / "synthetic" / "imu_trial.csv"
    output_path = ROOT / "examples" / "synthetic" / "outputs"
    write_synthetic_trial(input_path)
    config = PipelineConfig(
        angle_key="hombro_fe",
        mode="axis_offset",
        cutoff_hz=6.0,
        filter_order=4,
        neutral_window=(0.2, 1.0),
        analysis_window=(1.0, 2.5),
        phases=(("propulsion", 0.0, 2.0), ("recovery", 2.0, 3.99)),
        phase_points=100,
    )
    result = run_pipeline(input_path, output_path, config)
    print(f"Demo complete: {result.samples} samples at {result.sampling_hz:.3f} Hz")
    print(f"Selected descriptor component: {result.axis_used}")
    print(f"Generated files: {', '.join(sorted(path.name for path in result.output_paths.values()))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
