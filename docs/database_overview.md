# General database overview

This page describes the public database layer of the wheelchair IMU study. The database is a collection of de-identified research materials for method inspection and reproducibility support; it is not a clinical database or a diagnostic product.

## Public contents

| Path | Contents | Intended use |
| --- | --- | --- |
| `data/iSen/` | De-identified iSen CSV exports organised by coded trial folders. | Inspect exported signal structure and develop analysis code. |
| `data/profiling_data.xlsx` | De-identified support workbook with coded participant material, review sheets, and derived summaries. | Review public tabular material and derived descriptors. |
| `examples/synthetic/` | Deterministic generated input and reproducible outputs. | Run the reference implementation without research records. |

The coded folders and trial labels are operational identifiers only. They are not names and must not be linked to external identifying information.

## General database versus paper analysis

The general database contains the public materials collected and prepared for the wider study workflow. The paper used a defined analytical configuration from the iSen outputs. That configuration is documented in [`manuscript_analysis.md`](manuscript_analysis.md), including the sampling frequency, filter, retained cycles, normalization, summaries, and exploratory statistics.

The public Python reference implementation is a separate, transparent example. Its default settings are documented in [`processing_pipeline.md`](processing_pipeline.md). A difference in configuration reflects the intended role of each component and should be recorded when adapting the code.

## File handling

The public CSV and workbook files should be treated as de-identified research support materials. Preserve coded labels, record the repository version used, and document any changes to filtering, cycle selection, normalization, or summary calculations in downstream work.

Do not attempt re-identification, merge the coded records with identifying sources, or publish a derivative that adds personal information. Do not add restricted study files to this repository.

## Restricted materials

Original acquisition files, signed study documents, direct identifiers, calibration material, machine-specific paths, and unreleased intermediate files are outside the public database layer. Questions about access to restricted study materials can be directed to [Fabian A. Ñaña](mailto:fabian.nana@pucp.edu.pe); access is evaluated separately from this public repository.

## Citation and versioning

Record the repository tag used with any analysis. Cite the version in [`../CITATION.cff`](../CITATION.cff) and describe whether the work used the general database, the manuscript-related configuration, or the public reference implementation.
