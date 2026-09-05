"""End-to-end public workflow and provenance outputs."""

from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass, fields
from pathlib import Path

import numpy as np

from .io import read_signal_csv
from .metrics import describe_signal, derivatives
from .phases import normalize_phase
from .signal import compute_device_defined_angle


@dataclass(frozen=True)
class PipelineConfig:
    """All analysis choices that affect the public reference output."""

    angle_key: str = "hombro_fe"
    mode: str = "axis_offset"
    cutoff_hz: float = 6.0
    filter_order: int = 4
    neutral_window: tuple[float, float] = (0.2, 1.0)
    analysis_window: tuple[float, float] | None = None
    target_neutral: float = 0.0
    scale: float = 1.0
    offset: float = 0.0
    pair_base: str | None = None
    direct_column: str | None = None
    invert_sign: bool = False
    phases: tuple[tuple[str, float, float], ...] | None = None
    phase_points: int = 100


@dataclass(frozen=True)
class PipelineResult:
    output_dir: Path
    axis_used: str
    sampling_hz: float
    samples: int
    phase_points: int
    output_paths: dict[str, Path]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _config_as_json(config: PipelineConfig, phase_specs: tuple[tuple[str, float, float], ...]) -> dict:
    result = {}
    for item in fields(config):
        value = getattr(config, item.name)
        if isinstance(value, tuple):
            value = list(value)
        result[item.name] = value
    result["phases"] = [list(spec) for spec in phase_specs]
    return result


def _write_processed_csv(path: Path, time: np.ndarray, angle: np.ndarray, velocity: np.ndarray, acceleration: np.ndarray) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["time_s", "angle_deg", "velocity_deg_s", "acceleration_deg_s2"])
        for row in zip(time, angle, velocity, acceleration):
            writer.writerow([f"{float(value):.10g}" for value in row])


def _write_phase_csv(path: Path, phase_rows: list[dict[str, float | str]]) -> None:
    columns = ["phase", "phase_percent", "angle_deg", "velocity_deg_s", "acceleration_deg_s2"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(phase_rows)


def _write_plot(path: Path, time: np.ndarray, angle: np.ndarray, phase_rows: list[dict[str, float | str]]) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 1, figsize=(10, 7), constrained_layout=True)
    axes[0].plot(time, angle, color="#0f766e", linewidth=1.4)
    axes[0].set(xlabel="Time (s)", ylabel="Device-defined angle (deg)", title="Processed synthetic trial")
    axes[0].grid(alpha=0.25)

    for phase in sorted({str(row["phase"]) for row in phase_rows}):
        rows = [row for row in phase_rows if row["phase"] == phase]
        axes[1].plot(
            [float(row["phase_percent"]) for row in rows],
            [float(row["angle_deg"]) for row in rows],
            linewidth=1.5,
            label=phase,
        )
    axes[1].set(xlabel="Phase (%)", ylabel="Angle (deg)", title="Time-normalized phases")
    axes[1].grid(alpha=0.25)
    axes[1].legend(frameon=False)
    fig.savefig(path, dpi=180)
    plt.close(fig)


def run_pipeline(
    input_csv: str | Path,
    output_dir: str | Path,
    config: PipelineConfig | None = None,
    *,
    write_plot: bool = True,
) -> PipelineResult:
    """Run the public pipeline and write inspectable outputs."""

    input_path = Path(input_csv)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    config = config or PipelineConfig()

    table = read_signal_csv(input_path)
    time = table.time_s
    angle_result = compute_device_defined_angle(
        table,
        config.angle_key,
        mode=config.mode,
        cutoff_hz=config.cutoff_hz,
        order=config.filter_order,
        neutral_window=config.neutral_window,
        analysis_window=config.analysis_window,
        target_neutral=config.target_neutral,
        scale=config.scale,
        offset=config.offset,
        pair_base=config.pair_base,
        direct_column=config.direct_column,
        invert_sign=config.invert_sign,
    )
    velocity, acceleration = derivatives(time, angle_result.angle_deg)

    if config.phases is None:
        midpoint = float((time[0] + time[-1]) / 2.0)
        phase_specs = (("propulsion", float(time[0]), midpoint), ("recovery", midpoint, float(time[-1])))
    else:
        phase_specs = config.phases

    phase_rows: list[dict[str, float | str]] = []
    phase_signals = {
        "angle_deg": angle_result.angle_deg,
        "velocity_deg_s": velocity,
        "acceleration_deg_s2": acceleration,
    }
    for phase_name, start, end in phase_specs:
        normalized = normalize_phase(time, phase_signals, start, end, config.phase_points)
        for index in range(config.phase_points):
            phase_rows.append(
                {
                    "phase": phase_name,
                    "phase_percent": float(normalized["phase_percent"][index]),
                    "angle_deg": float(normalized["angle_deg"][index]),
                    "velocity_deg_s": float(normalized["velocity_deg_s"][index]),
                    "acceleration_deg_s2": float(normalized["acceleration_deg_s2"][index]),
                }
            )

    processed_path = out_dir / "processed_signal.csv"
    phase_path = out_dir / "phase_normalized.csv"
    summary_path = out_dir / "summary.json"
    manifest_path = out_dir / "pipeline_manifest.json"
    plot_path = out_dir / "angle_profile.png"
    _write_processed_csv(processed_path, time, angle_result.angle_deg, velocity, acceleration)
    _write_phase_csv(phase_path, phase_rows)

    summary = describe_signal(time, angle_result.angle_deg, velocity, acceleration)
    summary.update({"angle_key": config.angle_key, "axis_used": angle_result.axis_used})
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if write_plot:
        _write_plot(plot_path, time, angle_result.angle_deg, phase_rows)
    else:
        plot_path = None

    manifest = {
        "pipeline_version": "1.1.5",
        "input": {"filename": input_path.name, "sha256": _sha256(input_path)},
        "parameters": _config_as_json(config, phase_specs),
        "derived": {"sampling_hz": angle_result.sampling_hz, "axis_used": angle_result.axis_used},
        "outputs": [processed_path.name, phase_path.name, summary_path.name] + ([plot_path.name] if plot_path else []),
        "privacy": "This run contains no participant identifier; source media remain outside the public repository.",
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    paths = {"processed": processed_path, "phases": phase_path, "summary": summary_path, "manifest": manifest_path}
    if plot_path:
        paths["plot"] = plot_path
    return PipelineResult(out_dir, angle_result.axis_used, angle_result.sampling_hz, time.size, config.phase_points, paths)
