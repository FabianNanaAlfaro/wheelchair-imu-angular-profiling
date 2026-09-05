"""Generate supported manuscript figures from public numerical inputs."""

from __future__ import annotations

import argparse
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import spearmanr

import reproduce_manuscript_outputs as reproduction
from manuscript_variables import PARTICIPANTS, VARIABLE_FIELDS, VARIABLE_LABELS, VARIABLES


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_DIR = ROOT / "data" / "manuscript"
DEFAULT_OUTPUT_DIR = ROOT / "outputs" / "manuscript_figures"
DEFAULT_ASSET_DIR = ROOT / "assets" / "manuscript"
REGRESSION_TARGET = ROOT / "tests" / "fixtures" / "manuscript_spearman_reference.json"
PLOTTING_SCRIPT_VERSION = "1.0.0"
FIGURE_FORMATS = ("png", "pdf", "svg")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--asset-dir", type=Path, default=DEFAULT_ASSET_DIR)
    parser.add_argument("--check", action="store_true", help="validate values and required outputs")
    parser.add_argument(
        "--publish-assets",
        action="store_true",
        help="also write stable publication copies under assets/manuscript",
    )
    return parser.parse_args()


def configure_matplotlib() -> None:
    """Set a deterministic, publication-safe plotting style."""

    plt.rcParams.update(
        {
            "figure.dpi": 150,
            "savefig.dpi": 300,
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.titlesize": 12,
            "axes.labelsize": 10,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "axes.linewidth": 0.8,
            "axes.edgecolor": "#374151",
            "axes.labelcolor": "#111827",
            "xtick.color": "#374151",
            "ytick.color": "#374151",
            "grid.color": "#d1d5db",
            "grid.linewidth": 0.6,
            "grid.alpha": 0.7,
            "svg.hashsalt": "wheelchair-imu-manuscript",
        }
    )


def load_values(input_dir: Path, check: bool) -> tuple[list[dict[str, str]], list[dict[str, str]], np.ndarray, list[dict[str, object]]]:
    excursions, cycles = reproduction.load_inputs(input_dir)
    if check:
        reproduction.validate_reference_values(excursions, cycles)
    values = np.asarray(
        [[float(row[field]) for field in VARIABLE_FIELDS] for row in excursions],
        dtype=float,
    )
    if values.shape != (len(PARTICIPANTS), len(VARIABLES)):
        raise ValueError(f"expected a {len(PARTICIPANTS)} x {len(VARIABLES)} excursion matrix; found {values.shape}")
    summary = reproduction.build_cohort_summary(excursions)
    return excursions, cycles, values, summary


def compute_spearman_matrix(values: np.ndarray) -> np.ndarray:
    """Compute the Spearman matrix from participant rows in canonical order."""

    matrix = np.asarray(spearmanr(values, axis=0).statistic, dtype=float)
    if matrix.shape != (len(VARIABLES), len(VARIABLES)):
        raise ValueError(f"expected a square Spearman matrix; found {matrix.shape}")
    return matrix


def load_regression_target() -> tuple[tuple[str, ...], np.ndarray, float]:
    if not REGRESSION_TARGET.is_file():
        raise FileNotFoundError(f"regression target is missing: {REGRESSION_TARGET}")
    payload = json.loads(REGRESSION_TARGET.read_text(encoding="utf-8"))
    order = tuple(payload.get("variable_order", ()))
    target = np.asarray(payload.get("spearman_matrix", ()), dtype=float)
    tolerance = float(payload.get("tolerance", 1e-5))
    return order, target, tolerance


def rounded_report_value(value: object) -> Decimal:
    """Round a reported statistic using decimal half-up convention."""

    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def validate_spearman_matrix(matrix: np.ndarray, check: bool = False) -> None:
    if not np.all(np.isfinite(matrix)):
        raise ValueError("Spearman matrix contains non-finite values")
    if not np.allclose(matrix, matrix.T, atol=1e-12, rtol=0):
        raise ValueError("Spearman matrix is not symmetric")
    if not np.allclose(np.diag(matrix), np.ones(len(VARIABLES)), atol=1e-12, rtol=0):
        raise ValueError("Spearman matrix diagonal is not one")
    if check:
        target_order, target, tolerance = load_regression_target()
        if target_order != VARIABLE_FIELDS:
            raise ValueError("Spearman regression target order diverges from canonical variable order")
        if target.shape != matrix.shape or not np.allclose(matrix, target, atol=tolerance, rtol=0):
            raise ValueError("computed Spearman matrix does not match the regression target")


def save_figure(fig: plt.Figure, stem: str, output_dir: Path, asset_dir: Path | None = None) -> dict[str, list[str]]:
    output_dir.mkdir(parents=True, exist_ok=True)
    if asset_dir is not None:
        asset_dir.mkdir(parents=True, exist_ok=True)
    base_metadata = {
        "Creator": "wheelchair-imu-angular-profiling",
        "Title": stem.replace("_", " "),
    }
    output_files: list[str] = []
    asset_files: list[str] = []
    for extension in FIGURE_FORMATS:
        output_path = output_dir / f"{stem}.{extension}"
        metadata = dict(base_metadata)
        if extension == "pdf":
            metadata.update({"CreationDate": None, "ModDate": None})
        elif extension == "svg":
            metadata["Date"] = None
        fig.savefig(
            output_path,
            format=extension,
            dpi=300,
            facecolor="white",
            edgecolor="none",
            bbox_inches="tight",
            metadata=metadata,
        )
        if extension == "svg":
            svg_bytes = output_path.read_bytes()
            svg_bytes = re.sub(rb"[ \t]+(?=\r?$)", b"", svg_bytes, flags=re.MULTILINE)
            output_path.write_bytes(svg_bytes)
        output_files.append(portable_path(output_path))
        if asset_dir is not None:
            asset_path = asset_dir / output_path.name
            shutil.copyfile(output_path, asset_path)
            asset_files.append(portable_path(asset_path))
    return {"outputs": output_files, "assets": asset_files}


def portable_path(path: Path) -> str:
    """Return a repository-relative manifest path without leaking local paths."""

    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.name


def create_figure_5(values: np.ndarray) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(7.6, 5.2), constrained_layout=True)
    offsets = np.linspace(-0.11, 0.11, values.shape[0])
    participant_color = "#0f766e"
    median_color = "#111827"
    for column, variable in enumerate(VARIABLES):
        observations = values[:, column]
        x = np.full(observations.shape, column, dtype=float) + offsets
        ax.scatter(
            x,
            observations,
            s=42,
            color=participant_color,
            edgecolors="white",
            linewidths=0.75,
            alpha=0.95,
            zorder=3,
        )
        median = float(np.median(observations))
        ax.plot(
            [column - 0.23, column + 0.23],
            [median, median],
            color=median_color,
            linewidth=2.3,
            solid_capstyle="round",
            zorder=4,
        )

    ax.scatter([], [], s=42, color=participant_color, edgecolors="white", linewidths=0.75, label="Participant")
    ax.plot([], [], color=median_color, linewidth=2.3, label="Cohort median")
    ax.set_xticks(range(len(VARIABLES)), VARIABLE_LABELS)
    ax.set_xlim(-0.45, len(VARIABLES) - 0.55)
    ax.set_ylim(bottom=0)
    ax.set_ylabel("Angular excursion (°)")
    ax.set_title("Participant-level angular excursions")
    ax.grid(axis="y", zorder=0)
    ax.grid(axis="x", visible=False)
    ax.legend(frameon=False, loc="upper left", ncol=2, handlelength=2.2)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    return fig


def create_figure_6(matrix: np.ndarray) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(7.0, 6.2), constrained_layout=True)
    image = ax.imshow(matrix, cmap="coolwarm", vmin=-1, vmax=1, aspect="equal")
    tick_positions = np.arange(len(VARIABLES))
    ax.set_xticks(tick_positions, VARIABLE_LABELS, rotation=28, ha="right")
    ax.set_yticks(tick_positions, VARIABLE_LABELS)
    ax.set_xlabel("Angular descriptor")
    ax.set_ylabel("Angular descriptor")
    ax.set_title("Exploratory Spearman rank correlations")
    ax.set_xticks(np.arange(-0.5, len(VARIABLES), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(VARIABLES), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=1.2)
    ax.tick_params(which="minor", bottom=False, left=False)
    for row in range(matrix.shape[0]):
        for column in range(matrix.shape[1]):
            text_color = "white" if abs(matrix[row, column]) >= 0.55 else "#111827"
            ax.text(
                column,
                row,
                f"{matrix[row, column]:.4f}",
                ha="center",
                va="center",
                color=text_color,
                fontsize=9,
            )
    colorbar = fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    colorbar.set_label("Spearman ρ")
    return fig


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def repository_version() -> str:
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r"^version\s*=\s*[\"']([^\"']+)[\"']", text, re.MULTILINE)
    if match is None:
        raise ValueError("project version is missing from pyproject.toml")
    return match.group(1)


def repository_sha() -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    value = result.stdout.strip()
    return value or None


def build_manifest(
    input_dir: Path,
    output_records: dict[str, dict[str, list[str]]],
    publish_assets: bool,
) -> dict[str, object]:
    source = input_dir / "participant_level_excursions.csv"
    relative_source = portable_path(source)
    manifest: dict[str, object] = {
        "repository_version": repository_version(),
        "commit_sha": repository_sha(),
        "plotting_script_version": PLOTTING_SCRIPT_VERSION,
        "plotting_backend": "matplotlib-Agg",
        "input_files": {
            relative_source: {"sha256": sha256(source)},
        },
        "participants": len(PARTICIPANTS),
        "variable_order": [
            {"field": variable.field, "label": variable.label}
            for variable in VARIABLES
        ],
        "figures": {
            figure_name: {
                "source": relative_source,
                "files": records["outputs"],
                **({"assets": records["assets"]} if publish_assets else {}),
            }
            for figure_name, records in output_records.items()
        },
        "unsupported_figures": {
            "figure_2": {
                "generated": False,
                "reason": "Public participant mean normalized profiles are not available.",
            },
            "figure_3": {
                "generated": False,
                "reason": "Public participant mean normalized profiles are not available.",
            },
            "figure_4": {
                "generated": False,
                "reason": "Public participant mean normalized profiles are not available.",
            },
        },
        "profile_figures_generated": False,
        "retained_cycle_data_available": False,
        "deterministic_generation": True,
    }
    return manifest


def run(
    input_dir: Path = DEFAULT_INPUT_DIR,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    asset_dir: Path = DEFAULT_ASSET_DIR,
    check: bool = False,
    publish_assets: bool = False,
) -> dict[str, object]:
    configure_matplotlib()
    excursions, _cycles, values, summary = load_values(input_dir, check=check)
    matrix = compute_spearman_matrix(values)
    validate_spearman_matrix(matrix, check=check)
    if [row["variable"] for row in summary] != list(VARIABLE_FIELDS):
        raise ValueError("summary variable order diverges from canonical variable order")
    reported_medians = [rounded_report_value(row["median_deg"]) for row in summary]
    observed_medians = [rounded_report_value(np.median(values[:, index])) for index in range(values.shape[1])]
    if reported_medians != observed_medians:
        raise ValueError("Figure 5 medians do not match the plotted observations")

    output_dir.mkdir(parents=True, exist_ok=True)
    asset_target = asset_dir if publish_assets else None
    output_records: dict[str, dict[str, list[str]]] = {}
    figure_5 = create_figure_5(values)
    try:
        output_records["figure_5"] = save_figure(figure_5, "figure_5_excursions", output_dir, asset_target)
    finally:
        plt.close(figure_5)
    figure_6 = create_figure_6(matrix)
    try:
        output_records["figure_6"] = save_figure(figure_6, "figure_6_spearman", output_dir, asset_target)
    finally:
        plt.close(figure_6)

    manifest = build_manifest(input_dir, output_records, publish_assets=publish_assets)
    manifest_path = output_dir / "figure_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    required_output_names = [
        "figure_5_excursions.png",
        "figure_5_excursions.pdf",
        "figure_5_excursions.svg",
        "figure_6_spearman.png",
        "figure_6_spearman.pdf",
        "figure_6_spearman.svg",
        "figure_manifest.json",
    ]
    if check:
        for name in required_output_names:
            path = output_dir / name
            if not path.is_file() or path.stat().st_size == 0:
                raise RuntimeError(f"required manuscript figure output is missing: {path}")
        if publish_assets:
            for name in required_output_names[:-1]:
                path = asset_dir / name
                if not path.is_file() or path.stat().st_size == 0:
                    raise RuntimeError(f"stable manuscript asset is missing: {path}")
        print("MANUSCRIPT FIGURES CHECK: PASS")
    else:
        print(f"Manuscript figures written to {output_dir}")
    return manifest


if __name__ == "__main__":
    arguments = parse_args()
    run(
        input_dir=arguments.input_dir,
        output_dir=arguments.output_dir,
        asset_dir=arguments.asset_dir,
        check=arguments.check,
        publish_assets=arguments.publish_assets,
    )
