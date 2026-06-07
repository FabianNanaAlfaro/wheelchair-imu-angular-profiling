#!/usr/bin/env python3
"""iSen CSV batch processing utility.

This script provides a cleaned, public-facing version of the exploratory iSen
processing workflow. It reads de-identified iSen CSV files, applies low-pass
filtering, computes exploratory angular descriptors from X/Y pairs, and exports
plots and optional processed CSV files.

Important
---------
The final manuscript angular variables should be generated using the corrected
MATLAB workflow when reproducing the reported iSen patterns. This Python script
is included as an exploratory/support utility.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt


def butterworth_lowpass(data: np.ndarray, cutoff_hz: float = 6.0, fs: float = 100.0, order: int = 4) -> np.ndarray:
    """Apply a zero-phase Butterworth low-pass filter."""
    nyquist = 0.5 * fs
    if cutoff_hz >= nyquist:
        raise ValueError(f"cutoff_hz ({cutoff_hz}) must be below Nyquist ({nyquist}).")
    b, a = butter(order, cutoff_hz / nyquist, btype="low", analog=False)
    return filtfilt(b, a, np.asarray(data, dtype=float))


def read_isen_csv(path: Path) -> pd.DataFrame:
    """Read an iSen CSV file using automatic separator detection."""
    return pd.read_csv(path, sep=None, engine="python")


def get_time_vector(df: pd.DataFrame) -> Tuple[np.ndarray, float]:
    """Extract the time vector and sampling frequency from the first column."""
    time = pd.to_numeric(df.iloc[:, 0], errors="coerce").to_numpy(dtype=float)
    if np.isnan(time).any():
        raise ValueError("The time column contains non-numeric values.")
    time = time - time[0]
    if np.nanmax(time) > 1e4:
        time = time / 1000.0
    fs = 1.0 / np.nanmean(np.diff(time))
    return time, fs


def compute_exploratory_angles(df: pd.DataFrame, cutoff_hz: float = 6.0) -> Dict[str, pd.DataFrame]:
    """Compute exploratory angles from *_X and *_Y pairs.

    This is not the final corrected method used for the manuscript patterns. It
    is kept as a support utility for exploratory inspection of exported signals.
    """
    time, fs = get_time_vector(df)
    columns = list(df.columns)
    x_cols = [c for c in columns if str(c).endswith("_X")]
    results: Dict[str, pd.DataFrame] = {}

    for x_col in x_cols:
        base = str(x_col).removesuffix("_X")
        y_col = f"{base}_Y"
        if y_col not in df.columns:
            continue

        x = butterworth_lowpass(pd.to_numeric(df[x_col], errors="coerce").to_numpy(), cutoff_hz, fs)
        y = butterworth_lowpass(pd.to_numeric(df[y_col], errors="coerce").to_numpy(), cutoff_hz, fs)
        angle = np.degrees(np.arctan2(y, x))
        results[base] = pd.DataFrame({"time_s": time, "angle_deg": angle})

    return results


def process_folder(input_folder: Path, output_folder: Path, cutoff_hz: float) -> None:
    """Process every CSV file in a folder."""
    output_folder.mkdir(parents=True, exist_ok=True)
    plot_folder = output_folder / "plots"
    plot_folder.mkdir(exist_ok=True)

    for csv_path in sorted(input_folder.glob("*.csv")):
        print(f"Processing {csv_path.name}")
        df = read_isen_csv(csv_path)
        angles = compute_exploratory_angles(df, cutoff_hz=cutoff_hz)

        for angle_name, out_df in angles.items():
            safe_name = f"{csv_path.stem}_{angle_name}".replace(" ", "_")
            out_df.to_csv(output_folder / f"{safe_name}.csv", index=False)

            fig, ax = plt.subplots(figsize=(10, 4))
            ax.plot(out_df["time_s"], out_df["angle_deg"], linewidth=1.2)
            ax.set_title(f"{csv_path.stem} | {angle_name}")
            ax.set_xlabel("Time (s)")
            ax.set_ylabel("Exploratory angle (deg)")
            ax.grid(True)
            fig.tight_layout()
            fig.savefig(plot_folder / f"{safe_name}.png", dpi=300)
            plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch process de-identified iSen CSV files.")
    parser.add_argument("--input-folder", required=True, type=Path)
    parser.add_argument("--output-folder", required=True, type=Path)
    parser.add_argument("--cutoff-hz", default=6.0, type=float)
    args = parser.parse_args()

    process_folder(args.input_folder, args.output_folder, args.cutoff_hz)


if __name__ == "__main__":
    main()
