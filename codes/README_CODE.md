# Code guide

This folder preserves the cleaned MATLAB/Python scripts used to document the project workflow. The tested, end-to-end public reference implementation lives in [`src/wheelchair_pipeline`](../src/wheelchair_pipeline/) and is the recommended starting point for a fresh reproduction.

## Which implementation should I use?

| Need | Recommended entry point |
| --- | --- |
| Run a complete public example | `python scripts/run_public_demo.py` |
| Adapt the pipeline to an iSen CSV | `wheelchair_pipeline run` or `src/wheelchair_pipeline/` |
| Inspect the original MATLAB-oriented workflow | `matlab/compute_isen_angle_from_csv.m` and `matlab/codigo_fin_clean.m` |
| Review Kinovea support trajectories | `matlab/comparacion_kino_isen_clean.m` |
| Explore older batch utilities | `python/iSen_pcs_clean.py` and `python/summarize_angle_results_clean.py` |

## MATLAB reference scripts

```text
matlab/
  compute_isen_angle_from_csv.m   Corrected device-defined iSen angle helper
  codigo_fin_clean.m              Multi-descriptor angle extraction template
  comparacion_kino_isen_clean.m   Kinovea/iSen visual quality-control overlay
  automatizacion_clean.m          Generic Kinovea coordinate-table helper
  PATRONES_FINAL_clean.m           Profile plotting and descriptive summaries
```

The MATLAB scripts are templates because exact iSen and Kinovea column names can vary between exports. They use the same documented concepts as the Python reference: neutral-window alignment, a fourth-order 6 Hz low-pass filter, explicit phase review, and transparent descriptive outputs.

The numeric angular variables are device-defined descriptors. They should not be labelled anatomically calibrated joint angles unless a separate calibration and validation procedure has been performed.

## Python support scripts

The older support utilities are retained for continuity with the original public release. They are useful for exploratory batch inspection, but the new package provides stronger input validation, an explicit manifest, phase normalization, and automated tests.

```powershell
python scripts\run_public_demo.py
python -m unittest discover -s tests -v
```

## Expected local inputs

For a local study run, keep the restricted acquisition store outside this repository and use de-identified copies of the exported files. A typical X/Y input schema is:

```text
time_s, <descriptor>_X, <descriptor>_Y
```

Use `--pair-base` when automatic keyword matching is not appropriate. Use `--direct-column` and `--mode direct_resultant` only when the export already contains a resultant angle column.

## Kinovea's role

Kinovea/videogrammetry is used for protocol documentation, synchronization support, cycle-boundary review, and quality control. The main quantitative angular descriptors documented in the study come from iSen outputs. The comparison script therefore produces a visual QC overlay and does not silently replace the primary signal.

## Data boundary

The public `data/` folder contains only the de-identified iSen exports and support workbook that were already released. Do not add source video, camera files, recruitment/consent documents, calibration artefacts, or local file paths. See [`docs/public_data.md`](../docs/public_data.md) for the complete boundary.
