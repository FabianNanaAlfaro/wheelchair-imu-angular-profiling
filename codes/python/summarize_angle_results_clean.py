#!/usr/bin/env python3
"""Summarize processed angular descriptor CSV files.

The script computes descriptive values for de-identified angle time series:
maximum, minimum, range, standard deviation, mean, and optional first/second
finite-difference descriptors.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def summarize_file(path: Path) -> dict:
    df = pd.read_csv(path)
    time_col = "time_s" if "time_s" in df.columns else df.columns[0]
    angle_col = "angle_deg" if "angle_deg" in df.columns else df.columns[-1]

    t = pd.to_numeric(df[time_col], errors="coerce").to_numpy(dtype=float)
    y = pd.to_numeric(df[angle_col], errors="coerce").to_numpy(dtype=float)
    valid = np.isfinite(t) & np.isfinite(y)
    t = t[valid]
    y = y[valid]

    if len(y) < 3:
        raise ValueError(f"Not enough valid samples in {path.name}")

    dt = np.nanmean(np.diff(t)) if len(t) > 1 else np.nan
    velocity = np.gradient(y, dt) if np.isfinite(dt) and dt > 0 else np.full_like(y, np.nan)
    acceleration = np.gradient(velocity, dt) if np.isfinite(dt) and dt > 0 else np.full_like(y, np.nan)

    return {
        "file": path.name,
        "max_deg": np.nanmax(y),
        "min_deg": np.nanmin(y),
        "range_deg": np.nanmax(y) - np.nanmin(y),
        "sd_deg": np.nanstd(y, ddof=1),
        "mean_deg": np.nanmean(y),
        "max_velocity_deg_s": np.nanmax(velocity),
        "min_velocity_deg_s": np.nanmin(velocity),
        "max_acceleration_deg_s2": np.nanmax(acceleration),
        "min_acceleration_deg_s2": np.nanmin(acceleration),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize processed angle CSV files.")
    parser.add_argument("--input-folder", required=True, type=Path)
    parser.add_argument("--output-csv", required=True, type=Path)
    args = parser.parse_args()

    rows = []
    for csv_path in sorted(args.input_folder.glob("*.csv")):
        rows.append(summarize_file(csv_path))

    out = pd.DataFrame(rows)
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.output_csv, index=False)
    print(f"Summary saved to {args.output_csv}")


if __name__ == "__main__":
    main()
