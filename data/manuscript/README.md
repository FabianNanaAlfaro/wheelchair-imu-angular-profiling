# Manuscript-supporting dataset

## Scope

This directory contains the de-identified public analytical files supporting the reported manuscript-level excursion summaries and cycle-count traceability. The manuscript cohort contains exactly ten coded participants, `P1` through `P10`.

## Files

- `participant_level_excursions.csv`: one row per participant and five angular-excursion variables, in degrees.
- `cycle_traceability.csv`: one row per participant with detected, retained, and not-retained cycle counts. It contains counts only; no individual cycle identifiers are asserted.
- `../../assets/manuscript/`: validated publication assets for Figures 5 and 6.

Normalized participant mean trajectories and retained-cycle records are not included because their underlying public analytical values cannot be recovered confidently. No synthetic profiles or cycle identifiers are provided.

## Processing relationship

The manuscript-related configuration is documented in [`../../docs/manuscript_analysis.md`](../../docs/manuscript_analysis.md). The public Python reference implementation remains a separate 6 Hz example.

## Reproduction

From the repository root:

```powershell
python -m pip install -r requirements.txt
python scripts\reproduce_manuscript_outputs.py --check
```

This regenerates the participant-level excursion table, cohort-level summary, exploratory Spearman matrix, and cycle-traceability summary under `outputs/manuscript_reproduction/`.

The supported figure files are generated separately with:

```powershell
python scripts\generate_manuscript_figures.py --check --publish-assets
```

That command generates Figures 5 and 6 from `participant_level_excursions.csv` and records their provenance in `outputs/manuscript_figures/figure_manifest.json`.

## Boundaries

Restricted acquisition media are not required for the public reproduction of the derived analytical summaries provided here. The workflow does not claim complete reconstruction of unavailable profile figures or individual retained-cycle records.
