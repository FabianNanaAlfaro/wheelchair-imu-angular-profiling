"""Canonical variable definitions for manuscript-level outputs."""

from __future__ import annotations

from typing import NamedTuple


class ManuscriptVariable(NamedTuple):
    """A manuscript descriptor with its machine field and display label."""

    field: str
    label: str


PARTICIPANTS = tuple(f"P{i}" for i in range(1, 11))

# Keep this tuple as the single source of truth for extraction, statistics,
# plotting, axis labels, legends, and heatmap ordering.
VARIABLES = (
    ManuscriptVariable("shoulder_fe_deg", "Shoulder FE"),
    ManuscriptVariable("shoulder_aa_deg", "Shoulder AA"),
    ManuscriptVariable("elbow_fe_deg", "Elbow FE"),
    ManuscriptVariable("wrist_fe_deg", "Wrist FE"),
    ManuscriptVariable("wrist_rud_deg", "Wrist RUD"),
)

VARIABLE_FIELDS = tuple(variable.field for variable in VARIABLES)
VARIABLE_LABELS = tuple(variable.label for variable in VARIABLES)
EXCURSION_FIELDS = ("participant_id", *VARIABLE_FIELDS)
CYCLE_FIELDS = (
    "participant_id",
    "detected_cycles",
    "retained_cycles",
    "not_retained_cycles",
    "retained_percent",
)

if len(set(VARIABLE_FIELDS)) != len(VARIABLE_FIELDS):
    raise RuntimeError("manuscript variable fields must be unique")
if len(set(VARIABLE_LABELS)) != len(VARIABLE_LABELS):
    raise RuntimeError("manuscript variable labels must be unique")
