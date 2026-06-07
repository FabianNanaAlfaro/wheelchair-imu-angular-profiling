# Code package: Wheelchair IMU Angular Profiling

This folder contains cleaned and public-facing analysis scripts associated with the study:

**IMU-derived upper-limb angular profiling during controlled short-distance overground manual wheelchair propulsion in a heterogeneous Peruvian cohort**

The scripts were reorganized for GitHub release. Comments and documentation were standardized in English. The code is intended to support reproducibility of the reported descriptive workflow, tables, and figures. Raw videos and identifiable visual materials are not included.

## Important methodological note

The quantitative angular variables reported in the manuscript were derived from **iSen IMU outputs**, not from Kinovea/videogrammetry angles. Video/Kinovea files were used as methodological support for:

- protocol documentation,
- cycle-boundary confirmation,
- quality-control review,
- contextual inspection of propulsion patterns.

The `comparacion_kino_isen_clean.m` script is therefore a **quality-control comparison script**, not the primary source of the final angular variables.

## Participant-specific iSen angle workflow

The final iSen pattern extraction followed two routes:

1. **Participants P01–P08:** iSen patterns were derived using the corrected procedure implemented in `codigo_fin_clean.m` and `compute_isen_angle_from_csv.m`. This procedure uses a time window for neutral/reference alignment, chooses the relevant iSen exported component, applies low-pass filtering, and allows documented final scaling/offset adjustments when needed.
2. **Participants P09–P10:** the resultant angle was available directly and was used as the iSen angular descriptor without reconstructing it from X/Y components.

After this processing, propulsion patterns were separated through manual visual review supported by synchronized video and signal inspection. This manual separation step is part of the documented quality-control workflow and should not be interpreted as a fully automatic event-detection algorithm.

## Repository structure

```text
matlab/
  PATRONES_FINAL_clean.m              Main plotting script for publication-style participant profiles and summaries.
  codigo_fin_clean.m                  Corrected iSen angle extraction workflow for final pattern generation.
  compute_isen_angle_from_csv.m       Helper function used by codigo_fin_clean and comparison scripts.
  comparacion_kino_isen_clean.m       Kinovea-vs-iSen visual quality-control comparison using corrected iSen angles.
  automatizacion_clean.m              Legacy/support utility for processing Kinovea coordinate exports.

python/
  iSen_pcs_clean.py                   Batch Python utility for exploratory iSen CSV processing and visualization.
  summarize_angle_results_clean.py    Python utility to summarize angular descriptors from processed CSV files.

notebooks/
  proceso_isen_clean.ipynb            Cleaned notebook version of the exploratory iSen processing workflow.
  ISE_P_clean.ipynb                   Cleaned notebook version of the iSen summary workflow.

data_examples/
  resultados_anonymized.csv           Anonymized example of the older summary-results table.
```

## How to use the MATLAB scripts

1. Put the finalized participant-level spreadsheets or CSV files in a local data folder.
2. Open `matlab/PATRONES_FINAL_clean.m` and edit the `inputFolder` variable.
3. Run the script to generate participant-level angular profile figures and summary tables.
4. For raw iSen CSV processing, use `matlab/codigo_fin_clean.m` and edit the file paths and participant-specific options.
5. For Kinovea support review, use `matlab/comparacion_kino_isen_clean.m`; this script overlays video-derived support signals with corrected iSen angular descriptors.

## How to use the Python scripts

1. Install dependencies:

```bash
pip install numpy pandas matplotlib scipy
```

2. Run exploratory iSen processing:

```bash
python python/iSen_pcs_clean.py --input-folder data --output-folder outputs
```

3. Summarize processed angles:

```bash
python python/summarize_angle_results_clean.py --input-folder outputs --output-csv outputs/angular_summary.csv
```

## Privacy and de-identification

The cleaned scripts remove local absolute paths and direct identifiers. Public data should use participant codes (`P01`–`P10`) only. Do not upload raw videos, identifiable images, original file paths containing participant names, or non-anonymized laboratory files.

## License

The code is provided for academic reproducibility of the associated study. See the repository license file for terms of use.
