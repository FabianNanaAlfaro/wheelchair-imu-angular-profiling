# Manuscript-related analysis

This page documents the analytical configuration associated with the reported study of right-upper-limb motion during self-propelled manual-wheelchair propulsion. It is distinct from the public reference implementation, which is designed as a transparent and runnable example for the wider database.

## Scope

The paper analysis used manufacturer-provided iSen angular outputs, steady-state propulsion-cycle selection, temporal normalization, participant-level summaries, and exploratory associations among the resulting descriptors.

The public manuscript-supporting files are in [`../data/manuscript/`](../data/manuscript/). The available summaries can be regenerated with [`../scripts/reproduce_manuscript_outputs.py`](../scripts/reproduce_manuscript_outputs.py). The public files do not contain cycle-level boundaries or normalized profile traces, so the reproduction entry point does not claim to regenerate unavailable profile figures.

## Quantitative data source

iSen exports provide the primary quantitative angular variables. The reported variables are manufacturer-defined Euler-angle outputs from the inertial-sensor system. No independent author-side sensor-fusion or orientation re-estimation was applied.

The descriptors are device-defined angular outputs. They are not presented as independently validated anatomical joint angles. No anatomical or functional anatomical calibration was applied, and no external kinematic validation of the reported descriptors was performed.

## Processing configuration

The manuscript-related configuration consists of:

- acquisition and iSen export at 100 Hz;
- manufacturer-defined Euler-angle outputs;
- no additional orientation re-estimation or sensor-fusion reconstruction;
- no anatomical or functional anatomical calibration;
- review and selection of steady-state propulsion cycles using signal quality-control criteria;
- eight complete retained propulsion cycles per participant;
- fourth-order Butterworth low-pass filtering with a 10 Hz cutoff;
- normalization of each complete retained propulsion cycle to 100 points;
- participant-level averaging of the normalized cycles;
- participant-level angular-excursion computation; and
- descriptive summaries of the participant-level outputs.

The public manuscript-supporting files expose the participant-level excursion inputs and cycle-count traceability used by the reproduction entry point. They do not contain cycle-level boundaries or normalized profile traces, so this repository does not claim complete reconstruction from original acquisition through every reported result.

## Statistical analysis

Participant-level summaries include the mean, standard deviation, median, and range of the angular descriptors and angular excursions. Spearman correlations are exploratory and are calculated at the participant level where the corresponding variables are available.

The analyses are descriptive and exploratory. They do not support subgroup inference, causal interpretation, mechanistic claims, or clinical conclusions from correlation coefficients.

## Interpretation

All angular variables should be interpreted as device-defined angular descriptors or manufacturer-defined IMU angular outputs. Their numerical values describe the selected iSen output variables under the stated processing configuration; they should not be relabelled as anatomically calibrated joint angles.

## Relationship to the wider repository

The repository documents the broader research database and therefore contains components with different purposes. The public Python reference implementation uses a 6 Hz cutoff, neutral-window alignment, explicit component selection, and configurable phase windows so that its behavior can be inspected and reproduced from a synthetic example. MATLAB templates, notebooks, and legacy scripts serve complementary study, development, or supporting-analysis roles. Those components should be read according to their documented scope rather than treated as identical analytical implementations.

For the public reference implementation, see [`processing_pipeline.md`](processing_pipeline.md). For the public data boundary and reuse conditions, see [`public_data.md`](public_data.md).
