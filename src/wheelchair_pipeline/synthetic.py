"""Deterministic synthetic signal used by the public demo and tests."""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np


def write_synthetic_trial(
    path: str | Path,
    *,
    sample_rate_hz: float = 100.0,
    duration_s: float = 4.0,
    seed: int = 20260902,
) -> np.ndarray:
    """Write an iSen-like multi-channel trial and return its time vector."""

    if sample_rate_hz <= 2 * 6.0:
        raise ValueError("The demo sample rate must exceed the 6 Hz cutoff Nyquist requirement.")
    time = np.arange(0.0, duration_s, 1.0 / sample_rate_hz)
    rng = np.random.default_rng(seed)
    base = np.sin(2 * np.pi * 0.75 * time) + 0.18 * np.sin(2 * np.pi * 18.0 * time)
    channels = {
        "hombro_fe_X": 40.0 + 18.0 * base + rng.normal(0.0, 0.35, time.size),
        "hombro_fe_Y": 4.0 + 1.5 * np.cos(2 * np.pi * 0.75 * time) + rng.normal(0.0, 0.12, time.size),
        "codo_fe_X": 25.0 + 12.0 * np.sin(2 * np.pi * 0.75 * time + 0.4) + rng.normal(0.0, 0.25, time.size),
        "codo_fe_Y": 3.0 + 1.0 * np.cos(2 * np.pi * 0.75 * time + 0.4) + rng.normal(0.0, 0.12, time.size),
        "muneca_fe_X": 12.0 + 8.0 * np.sin(2 * np.pi * 0.75 * time - 0.2) + rng.normal(0.0, 0.2, time.size),
        "muneca_fe_Y": 2.0 + 0.8 * np.cos(2 * np.pi * 0.75 * time - 0.2) + rng.normal(0.0, 0.1, time.size),
    }
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["time_s", *channels.keys()])
        for index, timestamp in enumerate(time):
            writer.writerow([f"{timestamp:.6f}", *[f"{channels[name][index]:.10f}" for name in channels]])
    return time
