"""Regenerate manuscript-level summaries from the public analytical dataset."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
from pathlib import Path

from scipy.stats import spearmanr


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_DIR = ROOT / "data" / "manuscript"
DEFAULT_OUTPUT_DIR = ROOT / "outputs" / "manuscript_reproduction"
PARTICIPANTS = tuple(f"P{i}" for i in range(1, 11))
EXCURSION_FIELDS = (
    "participant_id",
    "shoulder_fe_deg",
    "shoulder_aa_deg",
    "elbow_fe_deg",
    "wrist_fe_deg",
    "wrist_rud_deg",
)
CYCLE_FIELDS = (
    "participant_id",
    "detected_cycles",
    "retained_cycles",
    "not_retained_cycles",
    "retained_percent",
)
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
EXPECTED_CYCLES = {
    "P1": (15, 8, 7, 53.3),
    "P2": (21, 8, 13, 38.1),
    "P3": (10, 8, 2, 80.0),
    "P4": (32, 8, 24, 25.0),
    "P5": (17, 8, 9, 47.1),
    "P6": (18, 8, 10, 44.4),
    "P7": (19, 8, 11, 42.1),
    "P8": (10, 8, 2, 80.0),
    "P9": (23, 8, 15, 34.8),
    "P10": (22, 8, 14, 36.4),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--check", action="store_true", help="validate inputs and generated schemas")
    return parser.parse_args()


def read_csv(path: Path, expected_fields: tuple[str, ...]) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(f"required public input is missing: {path}")
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fields = tuple(reader.fieldnames or ())
        if fields != expected_fields:
            raise ValueError(f"{path} must have columns {expected_fields}; found {fields}")
        rows = list(reader)
    if not rows:
        raise ValueError(f"required public input is empty: {path}")
    return rows


def number(value: str, field: str, row_number: int) -> float:
    try:
        result = float(value)
    except ValueError as exc:
        raise ValueError(f"non-numeric value in {field} at row {row_number}") from exc
    if not math.isfinite(result):
        raise ValueError(f"non-finite value in {field} at row {row_number}")
    return result


def integer(value: str, field: str, row_number: int) -> int:
    result = number(value, field, row_number)
    if result != int(result) or result < 0:
        raise ValueError(f"{field} must be a non-negative integer at row {row_number}")
    return int(result)


def fmt(value: float) -> str:
    return f"{value:.12g}"


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_inputs(input_dir: Path) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    excursions = read_csv(input_dir / "participant_level_excursions.csv", EXCURSION_FIELDS)
    cycles = read_csv(input_dir / "cycle_traceability.csv", CYCLE_FIELDS)
    if [row["participant_id"] for row in excursions] != list(PARTICIPANTS):
        raise ValueError("participant_level_excursions.csv must contain exactly P1 through P10 in order")
    if [row["participant_id"] for row in cycles] != list(PARTICIPANTS):
        raise ValueError("cycle_traceability.csv must contain exactly P1 through P10 in order")
    for row_number, row in enumerate(excursions, start=2):
        for field in EXCURSION_FIELDS[1:]:
            number(row[field], field, row_number)
    for row_number, row in enumerate(cycles, start=2):
        detected = integer(row["detected_cycles"], "detected_cycles", row_number)
        retained = integer(row["retained_cycles"], "retained_cycles", row_number)
        not_retained = integer(row["not_retained_cycles"], "not_retained_cycles", row_number)
        retained_percent = number(row["retained_percent"], "retained_percent", row_number)
        if detected - retained != not_retained:
            raise ValueError(f"cycle counts do not balance at row {row_number}")
        if detected == 0 or retained > detected or abs(retained_percent - round(100 * retained / detected, 1)) > 0.05:
            raise ValueError(f"cycle retention values do not balance at row {row_number}")
    return excursions, cycles


def validate_reference_values(excursions: list[dict[str, str]], cycles: list[dict[str, str]]) -> None:
    for row in excursions:
        observed = tuple(float(row[field]) for field in EXCURSION_FIELDS[1:])
        expected = EXPECTED_EXCURSIONS[row["participant_id"]]
        if any(abs(actual - target) > 0.01 for actual, target in zip(observed, expected)):
            raise ValueError(f"manuscript excursion reference mismatch for {row['participant_id']}")
    for row in cycles:
        observed = (
            int(row["detected_cycles"]),
            int(row["retained_cycles"]),
            int(row["not_retained_cycles"]),
            float(row["retained_percent"]),
        )
        expected = EXPECTED_CYCLES[row["participant_id"]]
        if observed[:3] != expected[:3] or abs(observed[3] - expected[3]) > 0.05:
            raise ValueError(f"cycle traceability reference mismatch for {row['participant_id']}")
    totals = tuple(sum(int(row[field]) for row in cycles) for field in ("detected_cycles", "retained_cycles", "not_retained_cycles"))
    if totals != (187, 80, 107) or any(int(row["retained_cycles"]) != 8 for row in cycles):
        raise ValueError(f"cycle traceability totals mismatch: {totals}")


def build_cohort_summary(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    output = []
    for field in EXCURSION_FIELDS[1:]:
        values = [number(row[field], field, index) for index, row in enumerate(rows, start=2)]
        mean = statistics.fmean(values)
        sd = statistics.stdev(values)
        median = statistics.median(values)
        minimum = min(values)
        maximum = max(values)
        reference = EXPECTED_SUMMARY[field]
        observed = (mean, sd, median, minimum, maximum)
        if any(abs(actual - target) > 0.01 for actual, target in zip(observed, reference)):
            raise ValueError(f"cohort summary reference mismatch for {field}")
        output.append(
            {
                "variable": field,
                "n": len(values),
                "mean_deg": fmt(mean),
                "sd_deg": fmt(sd),
                "median_deg": fmt(median),
                "min_deg": fmt(minimum),
                "max_deg": fmt(maximum),
            }
        )
    return output


def build_spearman_matrix(rows: list[dict[str, str]]) -> tuple[list[str], list[dict[str, object]]]:
    fields = list(EXCURSION_FIELDS[1:])
    matrix = [[number(row[field], field, index) for field in fields] for index, row in enumerate(rows, start=2)]
    correlation = spearmanr(matrix, axis=0).statistic
    result = []
    for index, field in enumerate(fields):
        result.append({"variable": field, **{other: fmt(float(correlation[index, j])) for j, other in enumerate(fields)}})
    return fields, result


def build_cycle_summary(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    result = [
        {
            "participant_id": row["participant_id"],
            "detected_cycles": int(row["detected_cycles"]),
            "retained_cycles": int(row["retained_cycles"]),
            "not_retained_cycles": int(row["not_retained_cycles"]),
            "retained_percent": fmt(float(row["retained_percent"])),
        }
        for row in rows
    ]
    result.append(
        {
            "participant_id": "TOTAL",
            "detected_cycles": sum(int(row["detected_cycles"]) for row in rows),
            "retained_cycles": sum(int(row["retained_cycles"]) for row in rows),
            "not_retained_cycles": sum(int(row["not_retained_cycles"]) for row in rows),
            "retained_percent": "",
        }
    )
    return result


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run(input_dir: Path, output_dir: Path, check: bool) -> int:
    excursions, cycles = load_inputs(input_dir)
    if check:
        validate_reference_values(excursions, cycles)
    output_dir.mkdir(parents=True, exist_ok=True)

    write_csv(output_dir / "participant_level_excursions.csv", list(EXCURSION_FIELDS), [dict(row) for row in excursions])
    write_csv(
        output_dir / "cohort_excursion_summary.csv",
        ["variable", "n", "mean_deg", "sd_deg", "median_deg", "min_deg", "max_deg"],
        build_cohort_summary(excursions),
    )
    fields, matrix_rows = build_spearman_matrix(excursions)
    write_csv(output_dir / "spearman_excursion_matrix.csv", ["variable", *fields], matrix_rows)
    write_csv(output_dir / "cycle_traceability_summary.csv", list(CYCLE_FIELDS), build_cycle_summary(cycles))

    manifest = {
        "inputs": {
            "participant_level_excursions.csv": sha256(input_dir / "participant_level_excursions.csv"),
            "cycle_traceability.csv": sha256(input_dir / "cycle_traceability.csv"),
        },
        "participants": list(PARTICIPANTS),
        "outputs": [
            "participant_level_excursions.csv",
            "cohort_excursion_summary.csv",
            "spearman_excursion_matrix.csv",
            "cycle_traceability_summary.csv",
        ],
        "profile_trajectories_generated": False,
        "profile_trajectory_note": "Participant mean normalized trajectories are not included in the public analytical layer.",
        "retained_cycle_ids_generated": False,
        "retained_cycle_id_note": "Only participant-level detected/retained counts are public.",
    }
    (output_dir / "reproduction_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    if check:
        expected_outputs = [output_dir / name for name in manifest["outputs"]] + [output_dir / "reproduction_manifest.json"]
        if any(not path.is_file() or path.stat().st_size == 0 for path in expected_outputs):
            raise RuntimeError("one or more manuscript reproduction outputs are missing")
        print("MANUSCRIPT REPRODUCTION CHECK: PASS")
    else:
        print(f"Manuscript summaries written to {output_dir}")
    return 0


if __name__ == "__main__":
    arguments = parse_args()
    raise SystemExit(run(arguments.input_dir, arguments.output_dir, arguments.check))
