"""Descriptive metrics for processed angle signals."""

from __future__ import annotations

import numpy as np


def derivatives(time_s: np.ndarray, angle_deg: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return angular velocity and acceleration using the recorded timestamps."""

    time = np.asarray(time_s, dtype=float).reshape(-1)
    angle = np.asarray(angle_deg, dtype=float).reshape(-1)
    if time.shape != angle.shape or time.size < 3:
        raise ValueError("At least three aligned time/angle samples are required.")
    if not np.all(np.isfinite(time)) or not np.all(np.isfinite(angle)):
        raise ValueError("Time and angle must be finite.")
    velocity = np.gradient(angle, time)
    acceleration = np.gradient(velocity, time)
    return velocity, acceleration


def describe_signal(
    time_s: np.ndarray,
    angle_deg: np.ndarray,
    velocity_deg_s: np.ndarray,
    acceleration_deg_s2: np.ndarray,
) -> dict[str, float | int]:
    """Create JSON-safe descriptive values for one processed signal."""

    time = np.asarray(time_s, dtype=float)
    angle = np.asarray(angle_deg, dtype=float)
    velocity = np.asarray(velocity_deg_s, dtype=float)
    acceleration = np.asarray(acceleration_deg_s2, dtype=float)
    return {
        "samples": int(angle.size),
        "duration_s": float(time[-1] - time[0]),
        "sampling_hz": float(1.0 / np.median(np.diff(time))),
        "max_deg": float(np.max(angle)),
        "min_deg": float(np.min(angle)),
        "range_deg": float(np.ptp(angle)),
        "mean_deg": float(np.mean(angle)),
        "sd_deg": float(np.std(angle, ddof=1)),
        "max_velocity_deg_s": float(np.max(velocity)),
        "min_velocity_deg_s": float(np.min(velocity)),
        "max_acceleration_deg_s2": float(np.max(acceleration)),
        "min_acceleration_deg_s2": float(np.min(acceleration)),
    }
