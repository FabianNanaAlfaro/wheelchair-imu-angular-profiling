# Code guide

This folder groups the MATLAB, Python, and notebook components developed for the wheelchair IMU study. The components have different roles: use the public package for a clean end-to-end example, and use the study and support scripts when inspecting the wider workflow.

## Components by role

| Component | Role | Recommended entry point |
| --- | --- | --- |
| `src/wheelchair_pipeline/` | Public reference implementation with input checks, manifests, and tests. | `python scripts/run_public_demo.py` |
| `codes/matlab/PATRONES_FINAL_clean.m` | Participant-level profile plots, excursion summaries, and optional descriptive/correlation tables. | Adapt the local input folder and run in MATLAB. |
| `codes/matlab/compute_isen_angle_from_csv.m` | Reusable helper for device-defined iSen descriptors from exported CSV files. | Call the function with an explicit descriptor key and options. |
| `codes/matlab/codigo_fin_clean.m` | Study workflow template for extracting multiple iSen descriptors and saving profile tables. | Review the settings before a local run. |
| `codes/python/` | Batch inspection and summary utilities retained from the study workflow. | Review the file-level docstrings before adapting. |
| `codes/notebooks/` | Compact exploratory examples without participant outputs. | Use the synthetic demo for a tested run. |
| `examples/synthetic/` | Deterministic data and commands for public reproducibility. | `python scripts/run_public_demo.py` |

## Public reference implementation

The package in `src/wheelchair_pipeline/` reads an exported signal table, checks the time vector, applies a fourth-order zero-phase Butterworth filter, computes a device-defined descriptor, derives velocity and acceleration, normalizes configured phases to 100 points, and writes inspectable outputs with a manifest. Its default reference configuration uses a 6 Hz cutoff and a neutral window.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts\run_public_demo.py
python -m unittest discover -s tests -v
```

For input schemas and parameter definitions, see [`docs/processing_pipeline.md`](../docs/processing_pipeline.md). For the configuration associated with the manuscript, see [`docs/manuscript_analysis.md`](../docs/manuscript_analysis.md).

## MATLAB study and support scripts

The MATLAB scripts are templates because exact iSen column names can vary between exports. They use local paths for local study files and write generated outputs outside the tracked public tree. Review descriptor names, filter settings, cycle windows, and input columns before adapting them to a new export.

The quantitative angular variables are device-defined descriptors. They should not be labelled anatomically calibrated joint angles unless a separate calibration and validation procedure has been performed.

## Expected local inputs

For a local study run, keep restricted acquisition files outside this repository and use de-identified copies of exported tables. A typical iSen component schema is:

```text
time_s, <descriptor>_X, <descriptor>_Y
```

Use an explicit `pairBase`/`--pair-base` when automatic component matching is not appropriate. Use `directColumn`/`--direct-column` and direct-resultant mode only when the export already contains the relevant angle column.

## Data boundary

The public `data/` folder contains de-identified iSen exports and the support workbook. Restricted acquisition files, recruitment/consent documents, calibration artefacts, and local path manifests remain outside the public tree. See [`docs/public_data.md`](../docs/public_data.md) before adding any new file.
