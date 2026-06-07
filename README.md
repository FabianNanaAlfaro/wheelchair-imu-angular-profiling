# Wheelchair IMU Angular Profiling

This repository contains analysis code and anonymized support data associated with a preliminary study on IMU-derived upper-limb angular profiling during controlled short-distance manual wheelchair propulsion.

The study included 10 adult manual wheelchair users who performed controlled straight overground propulsion trials using their personal wheelchairs. IMU data were acquired from the right upper limb and trunk reference during the task, and synchronized video recordings were used only for protocol documentation, cycle-boundary confirmation, quality control, and contextual propulsion-style review.

The study was developed at the Laboratorio de Investigación en Biomecánica y Rehabilitación Aplicada (LIBRA), Pontificia Universidad Católica del Perú (PUCP), by F. Ñaña, F. Nava, V. Abarca, and D. A. Elias. Data collection was conducted between January and April 2025 under ethical approval No. 143-2024-CEICVyT/PUCP.

The shared materials are intended to support reproducibility of the reported tables, figures, and descriptive analyses. Raw videos and potentially identifiable visual materials are not included due to participant privacy considerations.

## Repository contents

The repository is organized as follows:

```text
codes/
  Analysis scripts and cleaned code used for IMU processing, pattern extraction,
  descriptive summaries, and figure generation.

data/
  Anonymized support data used to reproduce the reported descriptive analyses.

data/iSen/
  De-identified iSen data files for the 10 participants included in the study.

data/profiling_data.xlsx
  Anonymized support workbook containing participant-level profiling data,
  traceability information, and video-supported review information used to
  document the analysis process.
```

## Data description

The shared data include anonymized IMU-derived files and support spreadsheets related to the 10 participants included in the study. These files were prepared to support reproducibility of:

* retained-cycle inspection and traceability;
* participant-level angular profiling;
* descriptive angular-excursion summaries;
* figure and table generation;
* contextual video-supported review of propulsion patterns.

All quantitative angular variables reported in the associated manuscript were derived from IMU outputs. The video-supported review was used only as methodological support to confirm task execution, cycle boundaries, quality-control decisions, and contextual propulsion-style classification.

## Code description

The `codes/` folder contains cleaned analysis scripts used to support the processing and visualization workflow. These scripts include MATLAB and Python files for:

* processing iSen-derived angular signals;
* extracting and visualizing propulsion patterns;
* comparing IMU-derived profiles with video-supported/Kinovea-assisted review;
* generating descriptive summaries and figures;
* documenting the processing workflow used in the manuscript.

The code is provided to support transparency and reproducibility of the reported descriptive analyses. It is not intended as a standalone validated clinical software package.

## Privacy and anonymization

The repository does not include raw videos, identifiable images, names, personal identifiers, or other potentially identifiable visual materials. Participants are represented using anonymized codes. The shared files were prepared for reproducibility while minimizing the risk of participant re-identification.

Because the study involved a small cohort of manual wheelchair users, raw videos and potentially identifiable visual recordings are not publicly shared.

## Authors

Fabian A. Ñaña, Fabricio Nava, Victoria E. Abarca, and Dante A. Elias.

All authors are affiliated with the Laboratorio de Investigación en Biomecánica y Rehabilitación Aplicada (LIBRA), Pontificia Universidad Católica del Perú (PUCP), Lima, Peru.

## Ethical approval

This study was approved by the Research Ethics Committee for Life Sciences and Technologies of the Pontificia Universidad Católica del Perú.

Approval number: 143-2024-CEICVyT/PUCP.

## How to cite

If you use this repository, please cite it as follows.

### APA 7th edition

Ñaña, F. A., Nava, F., Abarca, V. E., & Elias, D. A. (2026). *Wheelchair IMU angular profiling* (Version 1.0.0) [Data set and code]. GitHub. https://github.com/FabianNanaAlfaro/wheelchair-imu-angular-profiling

### IEEE

F. A. Ñaña, F. Nava, V. E. Abarca, and D. A. Elias, “Wheelchair IMU angular profiling,” GitHub repository, version 1.0.0, 2026. [Online]. Available: https://github.com/FabianNanaAlfaro/wheelchair-imu-angular-profiling

## Related manuscript

This repository supports a preliminary manuscript on IMU-derived upper-limb angular profiling during controlled short-distance manual wheelchair propulsion in a heterogeneous Peruvian cohort.

A full citation to the manuscript will be added once the article is published or available as a preprint.

