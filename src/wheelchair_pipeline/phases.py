"""Explicit phase windows and time-normalized signal exports."""

from __future__ import annotations

from typing import Mapping

import numpy as np


def normalize_phase(
    time_s: np.ndarray,
    signals: Mapping[str, np.ndarray],
    start_s: float,
    end_s: float,
    points: int = 100,
) -> dict[str, np.ndarray]:
    """Interpolate each signal to equally spaced 0–100 percent phase points."""

    time = np.asarray(time_s, dtype=float).reshape(-1)
    start, end = float(start_s), float(end_s)
    if end <= start:
        raise ValueError("Phase end must be greater than phase start.")
    if points < 2:
        raise ValueError("At least two normalized phase points are required.")
    if start < time[0] or end > time[-1]:
        raise ValueError(f"Phase [{start}, {end}] lies outside the recorded time range.")

    mask = (time >= start) & (time <= end)
    if np.count_nonzero(mask) < 2:
        raise ValueError("Phase window contains fewer than two samples.")
    phase_time = np.linspace(start, end, int(points))
    result = {"phase_percent": np.linspace(0.0, 100.0, int(points))}
    for name, values in signals.items():
        values_array = np.asarray(values, dtype=float).reshape(-1)
        if values_array.shape != time.shape:
            raise ValueError(f"Signal {name!r} has a different length from time.")
        if not np.all(np.isfinite(values_array)):
            raise ValueError(f"Signal {name!r} contains non-finite values.")
        # Interpolate against the complete trace so phase boundaries that fall
        # between recorded samples are not clamped to the first in-window row.
        result[name] = np.interp(phase_time, time, values_array)
    return result
