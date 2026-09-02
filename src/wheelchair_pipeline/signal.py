"""Filtering and device-defined angular descriptor calculations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import numpy as np
from scipy.signal import butter, filtfilt

from .io import SignalTable


@dataclass(frozen=True)
class AngleSeries:
    time_s: np.ndarray
    angle_deg: np.ndarray
    axis_used: str
    sampling_hz: float


def sampling_frequency(time_s: np.ndarray) -> float:
    delta = np.diff(np.asarray(time_s, dtype=float))
    if delta.size == 0 or not np.all(delta > 0):
        raise ValueError("Time must be strictly increasing.")
    return 1.0 / float(np.median(delta))


def butterworth_lowpass(
    values: np.ndarray,
    time_s: np.ndarray,
    cutoff_hz: float = 6.0,
    order: int = 4,
) -> np.ndarray:
    """Apply a zero-phase Butterworth low-pass filter."""

    y = np.asarray(values, dtype=float).reshape(-1)
    time = np.asarray(time_s, dtype=float).reshape(-1)
    if y.size != time.size or y.size < 5:
        raise ValueError("Signal and time must have the same length and at least five samples.")
    if not np.all(np.isfinite(y)):
        raise ValueError("Cannot filter a signal containing non-finite values.")
    fs = sampling_frequency(time)
    nyquist = fs / 2.0
    if cutoff_hz <= 0 or cutoff_hz >= nyquist:
        raise ValueError(f"cutoff_hz must be in (0, {nyquist:.6g}) Hz.")
    if order < 1 or int(order) != order:
        raise ValueError("order must be a positive integer.")

    b, a = butter(int(order), cutoff_hz / nyquist, btype="low", analog=False)
    padlen = min(3 * (max(len(a), len(b)) - 1), y.size - 1)
    if padlen < 1:
        raise ValueError("Signal is too short for the requested filter.")
    return filtfilt(b, a, y, padlen=padlen)


def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(term in text for term in terms)


def find_xy_pair(
    channels: Mapping[str, np.ndarray],
    angle_key: str,
    pair_base: str | None = None,
) -> tuple[str, str, str]:
    """Find a shared-base X/Y pair, with an auditable keyword score."""

    if pair_base:
        x_name, y_name = f"{pair_base}_X", f"{pair_base}_Y"
        if x_name not in channels or y_name not in channels:
            raise KeyError(f"Requested pair {pair_base!r} is not present.")
        return pair_base, x_name, y_name

    pairs = []
    for name in channels:
        if name.endswith("_X") and f"{name[:-2]}_Y" in channels:
            pairs.append((name[:-2], name, f"{name[:-2]}_Y"))
    if not pairs:
        raise KeyError("No matching *_X/*_Y channel pair was found.")

    key = angle_key.casefold()
    scored = []
    for base, x_name, y_name in pairs:
        candidate = base.casefold()
        score = 0
        if key == candidate:
            score += 10
        if _contains_any(key, ("shoulder", "hombro")) and _contains_any(candidate, ("shoulder", "hombro", "arm", "brazo")):
            score += 3
        if _contains_any(key, ("elbow", "codo")) and _contains_any(candidate, ("elbow", "codo")):
            score += 3
        if _contains_any(key, ("wrist", "muneca", "muñeca")) and _contains_any(candidate, ("wrist", "muneca", "muñeca", "hand", "mano")):
            score += 3
        if _contains_any(key, ("fe", "flex", "extension", "flexion")) and _contains_any(candidate, ("fe", "flex", "extension", "flexion")):
            score += 1
        if _contains_any(key, ("abd", "aduccion", "abduction")) and _contains_any(candidate, ("abd", "aduccion", "abduction")):
            score += 1
        scored.append((score, base, x_name, y_name))
    _, base, x_name, y_name = max(scored, key=lambda item: (item[0], item[1]))
    return base, x_name, y_name


def _window_mask(time_s: np.ndarray, window: tuple[float, float], label: str) -> np.ndarray:
    start, end = map(float, window)
    if end <= start:
        raise ValueError(f"{label} must have end > start.")
    mask = (time_s >= start) & (time_s <= end)
    if not np.any(mask):
        raise ValueError(f"{label} {window} does not overlap the signal.")
    return mask


def _find_direct_column(channels: Mapping[str, np.ndarray], angle_key: str) -> str:
    key = angle_key.casefold()
    candidates = [
        name for name in channels
        if any(token in name.casefold() for token in ("result", "angle", "angulo", key))
    ]
    if not candidates:
        raise KeyError("No direct resultant angle column was found; set direct_column explicitly.")
    return candidates[0]


def compute_device_defined_angle(
    table: SignalTable,
    angle_key: str,
    *,
    mode: str = "axis_offset",
    cutoff_hz: float = 6.0,
    order: int = 4,
    neutral_window: tuple[float, float] = (0.2, 1.0),
    analysis_window: tuple[float, float] | None = None,
    target_neutral: float = 0.0,
    scale: float = 1.0,
    offset: float = 0.0,
    pair_base: str | None = None,
    direct_column: str | None = None,
    invert_sign: bool = False,
) -> AngleSeries:
    """Compute the documented iSen-style device-defined descriptor."""

    time = table.time_s
    fs = sampling_frequency(time)
    normalized_mode = mode.casefold()
    if normalized_mode == "direct_resultant":
        column = direct_column or _find_direct_column(table.channels, angle_key)
        if column not in table.channels:
            raise KeyError(f"Direct angle column {column!r} is not present.")
        angle = butterworth_lowpass(table.channels[column], time, cutoff_hz, order)
        return AngleSeries(time, angle, column, fs)
    if normalized_mode != "axis_offset":
        raise ValueError("mode must be 'axis_offset' or 'direct_resultant'.")

    base, x_name, y_name = find_xy_pair(table.channels, angle_key, pair_base)
    x = butterworth_lowpass(table.channels[x_name], time, cutoff_hz, order)
    y = butterworth_lowpass(table.channels[y_name], time, cutoff_hz, order)
    neutral_mask = _window_mask(time, neutral_window, "neutral_window")
    if analysis_window is None:
        analysis_window = (neutral_window[1], min(neutral_window[1] + 1.5, float(time[-1])))
    analysis_mask = _window_mask(time, analysis_window, "analysis_window")

    if np.ptp(y[analysis_mask]) > np.ptp(x[analysis_mask]):
        selected, axis = y, "Y"
    else:
        selected, axis = x, "X"
    baseline = float(np.mean(selected[neutral_mask]))
    sign = -1.0 if invert_sign else 1.0
    angle = sign * (selected - baseline) + float(target_neutral)
    angle = float(scale) * angle + float(offset)
    return AngleSeries(time, angle, f"{base}:{axis}", fs)
