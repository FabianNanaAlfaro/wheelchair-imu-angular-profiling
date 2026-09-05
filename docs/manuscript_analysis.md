# Manuscript-related analysis

This page documents the analytical configuration associated with the reported study of right-upper-limb motion during self-propelled manual-wheelchair propulsion. It is distinct from the public reference implementation, which is designed as a transparent and runnable example for the wider project.

## Scope

The manuscript-related analysis describes the processing of manufacturer-provided iSen angular outputs, the review of steady-state propulsion cycles, temporal normalization, participant-level summaries, and exploratory associations among the resulting descriptors.

## Quantitative data source

iSen exports provide the primary quantitative angular variables. The reported variables are manufacturer-defined Euler-angle outputs from the inertial-sensor system. No independent author-side sensor-fusion or orientation re-estimation was applied.

The descriptors are device-defined angular outputs. They are not presented as independently validated anatomical joint angles. The study did not include functional anatomical calibration or optical-motion-capture validation of the reported descriptors.

## Supporting video review

Synchronized frontal and sagittal video, including Kinovea-based review, supports acquisition documentation, synchronization, steady-state cycle-boundary review, and visual quality control. Video is not the primary quantitative source of the reported angular outcomes.

Source recordings remain in the restricted study store. The public repository contains selected protocol illustrations and no source video.

## Processing configuration

The manuscript-related configuration consists of:

- acquisition and iSen export at 100 Hz;
- manufacturer-defined Euler-angle outputs;
- no additional orientation re-estimation or sensor-fusion reconstruction;
- no anatomical or functional anatomical calibration;
- review and selection of steady-state propulsion cycles using signal and synchronized-video inspection;
- eight complete retained propulsion cycles per participant;
- fourth-order Butterworth low-pass filtering with a 10 Hz cutoff;
- normalization of each complete retained propulsion cycle to 100 points;
- participant-level averaging of the normalized cycles;
- participant-level angular-excursion computation; and
- descriptive summaries of the participant-level outputs.

The de-identified materials and study workflow files available here support inspection of the relevant processing stages. Restricted acquisition files are not required to understand the documented configuration, but their absence means that this repository does not claim complete reconstruction from camera acquisition through every reported result.

## Statistical analysis

Participant-level summaries include the mean, standard deviation, median, and range of the angular descriptors and angular excursions. Spearman correlations are exploratory and are calculated at the participant level where the corresponding variables are available.

The analyses are descriptive and exploratory. They do not support subgroup inference, causal interpretation, mechanistic claims, or clinical conclusions from correlation coefficients.

## Interpretation

All angular variables should be interpreted as device-defined angular descriptors or manufacturer-defined IMU angular outputs. Their numerical values describe the selected iSen output variables under the stated processing configuration; they should not be relabelled as anatomically calibrated joint angles.

## Relationship to the wider repository

The repository documents the broader research workflow and therefore contains components with different purposes. The public Python reference implementation uses a 6 Hz cutoff, neutral-window alignment, explicit component selection, and configurable phase windows so that its behavior can be inspected and reproduced from a synthetic example. MATLAB templates, Kinovea support utilities, notebooks, and legacy scripts serve complementary study, development, or quality-control roles. Those components should be read according to their documented scope rather than treated as identical analytical implementations.

For the public reference implementation, see [`processing_pipeline.md`](processing_pipeline.md). For the public data boundary and reuse conditions, see [`public_data.md`](public_data.md).
