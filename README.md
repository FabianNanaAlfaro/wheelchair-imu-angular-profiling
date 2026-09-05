# Wheelchair IMU General Database & Analysis Companion

[![CI](https://github.com/FabianNanaAlfaro/wheelchair-imu-angular-profiling/actions/workflows/ci.yml/badge.svg)](https://github.com/FabianNanaAlfaro/wheelchair-imu-angular-profiling/actions/workflows/ci.yml)
[![Release](https://img.shields.io/badge/release-v1.1.7-0f766e)](CHANGELOG.md)
[![License](https://img.shields.io/badge/code%20license-MIT-111827)](LICENSE)

Public de-identified iSen database and analysis companion for upper-limb motion during self-propelled manual-wheelchair propulsion. The repository combines general research materials, analysis utilities, a tested Python reference implementation, MATLAB templates, and synthetic examples.

> **Release status — v1.1.7**
>
> This repository documents the broader study database and computational workflow. The analysis associated with the paper is described separately so that its configuration is not confused with the other research and development components.

For questions about restricted study materials, contact [Fabian A. Ñaña](mailto:fabian.nana@pucp.edu.pe). Restricted material is not distributed through this repository.

## Repository scope

This repository documents the broader experimental and computational workflow developed during the wheelchair IMU study. It includes study documentation, de-identified research materials, analysis utilities, legacy/development code, and a tested public reference implementation. Individual components are documented according to their intended role; not every implementation represents the same analytical configuration.

## General database

The public database layer contains de-identified iSen exports, a general workbook with coded participant-level material, and derived public summaries. It is intended for method inspection, exploratory reuse, and reproducibility support. The database overview, file structure, and reuse conditions are described in [`docs/database_overview.md`](docs/database_overview.md).

## Manuscript-related analysis

The paper used a defined iSen-based analytical configuration: 100 Hz acquisition, manufacturer-defined Euler-angle outputs, steady-state cycle selection, eight retained cycles per participant, 10 Hz fourth-order Butterworth filtering, 100-point cycle normalization, participant-level averaging, angular-excursion summaries, and exploratory Spearman correlations. See [`docs/manuscript_analysis.md`](docs/manuscript_analysis.md) for the complete scope and interpretation.

The public manuscript-supporting analytical files and their reproduction command are collected in [`data/manuscript/`](data/manuscript/) and [`scripts/reproduce_manuscript_outputs.py`](scripts/reproduce_manuscript_outputs.py).

Publication-ready Figures 5–6 are generated from that same excursion table by [`scripts/generate_manuscript_figures.py`](scripts/generate_manuscript_figures.py) and are stored in [`assets/manuscript/`](assets/manuscript/). Figures 2–4 are not generated because participant mean normalized profiles are not part of the public analytical layer.

## Public reference implementation

The tested Python package in `src/wheelchair_pipeline/` is a transparent reference workflow for exported signal tables. It uses explicit input checks, a fourth-order zero-phase Butterworth filter, device-defined descriptor calculation, numerical derivatives, phase normalization, JSON summaries, and a provenance manifest. Its default reference configuration uses a 6 Hz cutoff and a neutral window.

Run the public demonstration from the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts\run_public_demo.py
```

The deterministic example creates 400 samples at 100 Hz and writes processed signal, normalized phase, summary, manifest, and plot outputs under `examples/synthetic/outputs/`. Generated outputs are ignored by Git.

## Reproducibility scope

The synthetic example reproduces the public reference implementation end to end. The de-identified iSen files and workbook support inspection and reuse of public research materials. Full reconstruction from original acquisition through every paper result is not claimed because restricted study files are not distributed.

## Repository map

```text
codes/
  matlab/                         iSen extraction and participant-level summaries
  python/                         Exploratory batch and summary utilities
  notebooks/                      Data-agnostic exploratory notebooks
data/
  iSen/                           De-identified iSen CSV exports
  profiling_data.xlsx             De-identified general iSen workbook
  manuscript/                     Manuscript-supporting analytical summaries
assets/
  manuscript/                     Publication-ready Figures 5–6
docs/
  database_overview.md            General database scope and file inventory
  manuscript_analysis.md          Configuration associated with the paper
  processing_pipeline.md          Public reference implementation
  public_data.md                  Public data boundary and reuse conditions
examples/synthetic/               Deterministic generated input and instructions
src/wheelchair_pipeline/          Tested Python reference implementation
scripts/                          Demo, manuscript reproduction, and release audit
tests/                            Offline smoke tests
```

## Methodological interpretation

The primary quantitative variables are manufacturer-defined iSen angular outputs. They are device-defined descriptors, not independently validated anatomical joint angles. The study did not include functional anatomical calibration or optical-motion-capture validation of the reported descriptors.

The manuscript-related configuration and the public reference implementation are intentionally documented as separate layers. Other MATLAB, Python, and notebook components are retained as study workflow, development, or supporting analysis utilities and may use different settings according to their intended purpose.

## Data availability and privacy

The public tree contains no source acquisition recordings, signed forms, direct identifiers, local computer paths, credentials, or participant names. Participant codes are used where coded research material is necessary. See [`docs/public_data.md`](docs/public_data.md) before reusing or extending the public data layer.

## Citation

Use the versioned citation in [`CITATION.cff`](CITATION.cff):

> Ñaña, F. A., Nava, F., Abarca, V. E., & Elias, D. A. (2026). *Wheelchair IMU General Database & Analysis Companion* (Version 1.1.7) [Software and de-identified research materials]. GitHub. https://github.com/FabianNanaAlfaro/wheelchair-imu-angular-profiling

No article DOI is asserted by this repository. Add an article DOI only when it has been formally assigned by the publisher or indexing service.

## Related documentation

- [General database overview](docs/database_overview.md)
- [Manuscript-related analysis](docs/manuscript_analysis.md)
- [Manuscript-supporting dataset](data/manuscript/README.md)
- [Manuscript reproduction script](scripts/reproduce_manuscript_outputs.py)
- [Manuscript figure generator](scripts/generate_manuscript_figures.py)
- [Manuscript figures and scope](docs/manuscript_figures.md)
- [Public reference pipeline](docs/processing_pipeline.md)
- [Public data card](docs/public_data.md)
- [Code guide](codes/README_CODE.md)
- [Changelog](CHANGELOG.md)

## License

The MIT license applies to the code and documentation. De-identified research materials remain subject to the permissions and conditions described in [`docs/public_data.md`](docs/public_data.md).
