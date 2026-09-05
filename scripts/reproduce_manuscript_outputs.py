"""Regenerate manuscript-level summary views from the public analytical layer."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

from scipy.stats import spearmanr


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_DIR = ROOT / "data" / "manuscript"
DEFAULT_OUTPUT_DIR = ROOT / "outputs" / "manuscript_reproduction"
DESCRIPTOR_COLUMNS = (
    "participant_id",
    "descriptor_id",
    "descriptor_label",
    "source_sheet",
    "source_row",
    "max_deg",
    "min_deg",
    "excursion_deg",
    "sd_deg",
    "mean_deg",
    "max_velocity_deg_s",
    "min_velocity_deg_s",
    "max_acceleration_deg_s2",
    "min_acceleration_deg_s2",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--check", action="store_true", help="validate inputs and generated schemas")
    return parser.parse_args()


def read_csv(path: Path, required: tuple[str, ...]) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(f"required public input is missing: {path}")
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or not set(required).issubset(reader.fieldnames):
            raise ValueError(f"{path} does not contain the required columns: {required}")
        return list(reader)


def number(value: str, field: str, row_number: int) -> float:
    try:
        result = float(value)
    except ValueError as exc:
        raise ValueError(f"non-numeric value in {field} at row {row_number}") from exc
    if not math.isfinite(result):
        raise ValueError(f"non-finite value in {field} at row {row_number}")
    return result


def fmt(value: float) -> str:
    return f"{value:.12g}"


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_inputs(input_dir: Path) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    descriptors = read_csv(input_dir / "participant_level_descriptors.csv", DESCRIPTOR_COLUMNS)
    excursions = read_csv(input_dir / "participant_level_excursions.csv", ("participant_id",))
    if not descriptors:
        raise ValueError("participant_level_descriptors.csv is empty")
    if not excursions:
        raise ValueError("participant_level_excursions.csv is empty")
    return descriptors, excursions


def build_descriptive_summary(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], list[float]] = defaultdict(list)
    for index, row in enumerate(rows, start=2):
        descriptor = row["descriptor_id"]
        grouped[(descriptor, "mean_deg")].append(number(row["mean_deg"], "mean_deg", index))
        grouped[(descriptor, "excursion_deg")].append(number(row["excursion_deg"], "excursion_deg", index))

    output: list[dict[str, object]] = []
    for (descriptor, metric), values in grouped.items():
        output.append(
            {
                "descriptor_id": descriptor,
                "metric": metric,
                "n": len(values),
                "mean": fmt(statistics.fmean(values)),
                "sd": fmt(statistics.stdev(values) if len(values) > 1 else 0.0),
                "median": fmt(statistics.median(values)),
                "minimum": fmt(min(values)),
                "maximum": fmt(max(values)),
                "range": fmt(max(values) - min(values)),
            }
        )
    return output


def build_excursion_summary(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for index, row in enumerate(rows, start=2):
        grouped[row["descriptor_id"]].append(number(row["excursion_deg"], "excursion_deg", index))
    return [
        {
            "descriptor_id": descriptor,
            "n": len(values),
            "mean_excursion_deg": fmt(statistics.fmean(values)),
            "sd_excursion_deg": fmt(statistics.stdev(values) if len(values) > 1 else 0.0),
            "median_excursion_deg": fmt(statistics.median(values)),
            "minimum_excursion_deg": fmt(min(values)),
            "maximum_excursion_deg": fmt(max(values)),
        }
        for descriptor, values in grouped.items()
    ]


def build_spearman_matrix(rows: list[dict[str, str]]) -> tuple[list[str], list[dict[str, object]]]:
    if not rows:
        raise ValueError("no participant-level excursion rows available")
    fieldnames = [field for field in rows[0] if field != "participant_id"]
    matrix_values = [
        [number(row[field], field, row_index) for row_index, row in enumerate(rows, start=2)]
        for field in fieldnames
    ]
    correlation = spearmanr(matrix_values, axis=1).statistic
    output = []
    for i, field in enumerate(fieldnames):
        output.append({"descriptor_id": field, **{other: fmt(float(correlation[i, j])) for j, other in enumerate(fieldnames)}})
    return fieldnames, output


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run(input_dir: Path, output_dir: Path, check: bool) -> int:
    descriptors, excursions = load_inputs(input_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    descriptive_path = output_dir / "descriptive_summary.csv"
    excursion_path = output_dir / "angular_excursion_summary.csv"
    correlation_path = output_dir / "spearman_excursion_matrix.csv"

    write_csv(
        descriptive_path,
        ["descriptor_id", "metric", "n", "mean", "sd", "median", "minimum", "maximum", "range"],
        build_descriptive_summary(descriptors),
    )
    write_csv(
        excursion_path,
        ["descriptor_id", "n", "mean_excursion_deg", "sd_excursion_deg", "median_excursion_deg", "minimum_excursion_deg", "maximum_excursion_deg"],
        build_excursion_summary(descriptors),
    )
    matrix_fields, matrix_rows = build_spearman_matrix(excursions)
    write_csv(correlation_path, ["descriptor_id", *matrix_fields], matrix_rows)

    manifest = {
        "inputs": {
            "participant_level_descriptors.csv": sha256(input_dir / "participant_level_descriptors.csv"),
            "participant_level_excursions.csv": sha256(input_dir / "participant_level_excursions.csv"),
        },
        "outputs": [path.name for path in (descriptive_path, excursion_path, correlation_path)],
        "profile_plots_generated": False,
        "profile_plot_note": "Cycle-normalized participant profiles are not included in the public manuscript-supporting layer.",
    }
    (output_dir / "reproduction_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    if check:
        for path in (descriptive_path, excursion_path, correlation_path, output_dir / "reproduction_manifest.json"):
            if not path.is_file() or path.stat().st_size == 0:
                raise RuntimeError(f"expected reproduction output was not created: {path}")
        with descriptive_path.open(newline="", encoding="utf-8") as handle:
            assert set(csv.DictReader(handle).fieldnames or ()) == {"descriptor_id", "metric", "n", "mean", "sd", "median", "minimum", "maximum", "range"}
        print("MANUSCRIPT REPRODUCTION CHECK: PASS")
    else:
        print(f"Manuscript summaries written to {output_dir}")
    return 0


if __name__ == "__main__":
    arguments = parse_args()
    raise SystemExit(run(arguments.input_dir, arguments.output_dir, arguments.check))
