"""Small, dependency-light readers for exported time-series CSV files."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Tuple

import numpy as np


TIME_COLUMN_CANDIDATES = ("time_s", "Time", "time", "Tiempo", "t")


@dataclass(frozen=True)
class SignalTable:
    """Numeric signal table with a validated time vector."""

    time_s: np.ndarray
    channels: Dict[str, np.ndarray]
    source_columns: Tuple[str, ...]


def _detect_delimiter(sample: str) -> str:
    try:
        return csv.Sniffer().sniff(sample, delimiters=",;\t").delimiter
    except csv.Error:
        return ","


def _as_float(value: object, column: str, row_number: int) -> float:
    if value is None or str(value).strip() == "":
        raise ValueError(f"Missing numeric value in column {column!r}, row {row_number}.")
    text = str(value).strip().replace("\u00a0", "")
    try:
        return float(text)
    except ValueError as exc:
        # Some spreadsheet exports use a decimal comma. This fallback is safe
        # after the delimiter has already been detected by csv.Sniffer.
        try:
            return float(text.replace(",", "."))
        except ValueError:
            raise ValueError(
                f"Non-numeric value {text!r} in column {column!r}, row {row_number}."
            ) from exc


def _choose_time_column(fieldnames: Iterable[str]) -> str:
    names = tuple(fieldnames)
    for candidate in TIME_COLUMN_CANDIDATES:
        if candidate in names:
            return candidate
    if not names:
        raise ValueError("CSV has no header columns.")
    return names[0]


def _validate_time(time: np.ndarray) -> tuple[np.ndarray, float]:
    if time.size < 5:
        raise ValueError("At least five samples are required for filtering.")
    if not np.all(np.isfinite(time)):
        raise ValueError("Time contains non-finite values.")
    time = time - time[0]
    delta = np.diff(time)
    if not np.all(delta > 0):
        raise ValueError("Time must be strictly increasing; check duplicate or unsorted samples.")

    # iSen exports are normally in seconds. This conservative fallback handles
    # unmistakable millisecond exports without hiding the unit conversion.
    if float(np.nanmedian(delta)) > 0.5 or float(time[-1]) > 1.0e4:
        time = time / 1000.0
        delta = np.diff(time)
        if not np.all(delta > 0):
            raise ValueError("Millisecond-to-second conversion produced invalid time values.")

    fs = 1.0 / float(np.nanmedian(delta))
    if not np.isfinite(fs) or fs <= 0:
        raise ValueError("Could not derive a positive sampling frequency.")
    return time, fs


def read_signal_csv(path: str | Path) -> SignalTable:
    """Read a numeric signal CSV and validate its time vector.

    The first recognised time column is used; all remaining columns must be
    numeric. The function intentionally rejects malformed rows rather than
    interpolating or silently dropping samples.
    """

    csv_path = Path(path)
    if not csv_path.is_file():
        raise FileNotFoundError(csv_path)

    text = csv_path.read_text(encoding="utf-8-sig")
    delimiter = _detect_delimiter(text[:8192])
    reader = csv.DictReader(text.splitlines(), delimiter=delimiter)
    if reader.fieldnames is None:
        raise ValueError(f"CSV has no header: {csv_path}")

    fieldnames = tuple((name or "").strip() for name in reader.fieldnames)
    if not all(fieldnames):
        raise ValueError("CSV contains an empty header name.")
    if len(set(fieldnames)) != len(fieldnames):
        raise ValueError("CSV contains duplicate header names.")

    time_column = _choose_time_column(fieldnames)
    rows = list(reader)
    if not rows:
        raise ValueError(f"CSV has no data rows: {csv_path}")

    values = {name: [] for name in fieldnames}
    for row_number, row in enumerate(rows, start=2):
        if None in row:
            raise ValueError(f"Extra fields found in row {row_number} of {csv_path}.")
        for name in fieldnames:
            values[name].append(_as_float(row.get(name), name, row_number))

    time, _ = _validate_time(np.asarray(values.pop(time_column), dtype=float))
    channels = {
        name: np.asarray(column, dtype=float)
        for name, column in values.items()
    }
    if not channels:
        raise ValueError("CSV must contain at least one signal channel besides time.")
    for name, channel in channels.items():
        if channel.shape != time.shape or not np.all(np.isfinite(channel)):
            raise ValueError(f"Channel {name!r} is not finite or has the wrong length.")

    return SignalTable(time_s=time, channels=channels, source_columns=fieldnames)
