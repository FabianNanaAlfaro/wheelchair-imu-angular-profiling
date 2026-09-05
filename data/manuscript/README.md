# Manuscript-supporting dataset

## Scope

This directory contains de-identified public analytical files supporting the reported manuscript-level summaries. Values are derived from the public iSen summary layer and are provided for transparent inspection of participant-level descriptors and angular excursions.

## Files

- `participant_level_descriptors.csv`: long-format participant-level descriptors. Each row represents one participant and descriptor; values are summary outputs, not cycle-level records. Participants are represented by coded labels such as `P01`.
- `participant_level_excursions.csv`: wide-format participant-level angular excursions in degrees, derived from the corresponding descriptor maxima and minima.

Cycle-level boundaries, retained-cycle identifiers, and normalized profile traces are not included because they cannot be reconstructed confidently from the public summary layer. No synthetic cycle traceability is presented.

## Processing relationship

The manuscript-related configuration is documented in [`../../docs/manuscript_analysis.md`](../../docs/manuscript_analysis.md). The public Python reference implementation remains a separate 6 Hz example.

## Reproduction

From the repository root:

```powershell
python -m pip install -r requirements.txt
python scripts\reproduce_manuscript_outputs.py --check
```

This regenerates participant-level descriptive summaries, angular-excursion summaries, and an exploratory Spearman correlation matrix under `outputs/manuscript_reproduction/`.

## Boundaries

Restricted acquisition media are not required for the public reproduction of the derived analytical summaries provided here. The workflow does not claim complete reconstruction of every acquisition-to-result step or unavailable profile figure.
