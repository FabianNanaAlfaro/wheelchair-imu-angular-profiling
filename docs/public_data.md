# Public data card

## Scope

The public release contains de-identified iSen exports, a support workbook, and a deterministic synthetic example. These are research support materials for method inspection and reproducibility; they are not a clinical dataset or a diagnostic product.

| Path | Description | Public boundary |
| --- | --- | --- |
| `data/iSen/` | De-identified iSen CSV exports organised by coded trial folders. | Signal exports only; no direct identifiers. |
| `data/profiling_data.xlsx` | De-identified support workbook with coded participant material, review sheets, and derived summaries. | No names, contact details, consent forms, or restricted acquisition records. |
| `examples/synthetic/` | Generated demonstration input and instructions. | Contains no participant provenance. |

## Not included

The following remain outside the public database layer:

- restricted acquisition records and unreleased intermediate files;
- signed study documents, recruitment material, direct identifiers, and contact lists;
- calibration files, local path manifests, credentials, and machine-specific configuration; and
- any file that could be used to reconnect a code to a person.

## Reuse guidance

The public iSen files and workbook should be treated as de-identified research support materials. Preserve the coded labels, record the repository version used, and document any downstream changes to filtering, cycle selection, normalization, or summary calculations.

Do not attempt re-identification, link the codes to other datasets, or publish a derivative that adds identifying information. The MIT license covers the code and documentation; data reuse remains subject to the permissions and conditions under which the research materials were prepared.

## Access questions

Questions about restricted study materials can be directed to [fabian.nana@pucp.edu.pe](mailto:fabian.nana@pucp.edu.pe). Access is evaluated separately from this public repository and is not provided through a public download link.
