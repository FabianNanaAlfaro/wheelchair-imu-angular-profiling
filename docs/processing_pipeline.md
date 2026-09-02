# Processing pipeline

This document is the executable contract for the public reference implementation. It describes the processing stages without exposing the private acquisition store.

## Input contract

The Python reference pipeline accepts a CSV with one time column and one or more numeric signal columns. X/Y component pairs use a shared base name:

```csv
time_s,hombro_fe_X,hombro_fe_Y,codo_fe_X,codo_fe_Y
0.00,12.0,0.1,8.0,0.2
0.01,12.2,0.1,8.1,0.2
0.02,12.6,0.2,8.2,0.3
```

The reader also recognises `Tiempo`, `Time`, `time`, or `t` and tolerates comma, semicolon, or tab-separated exports. Time is converted to seconds when an export is clearly in milliseconds, then checked for finite, strictly increasing samples.

## Stages

### 1. Import and quality checks

Read the time vector and numeric channels. Reject missing values, repeated timestamps, non-finite values, and insufficient samples rather than silently producing a misleading output.

### 2. Signal conditioning

Apply a fourth-order low-pass Butterworth filter with a 6 Hz cutoff. The implementation uses zero-phase filtering (`scipy.signal.filtfilt`) so the public demo does not introduce a phase shift. The cutoff must remain below the Nyquist frequency derived from the input time vector.

### 3. Device-defined angle

For an X/Y pair, the implementation can select the pair explicitly or use a documented keyword match. It selects the component with the larger range in the analysis window, estimates a baseline from the neutral window, and applies the configured sign, target, scale, and offset:

```text
angle = sign * (selected_component - mean(neutral_window))
        + target_neutral
angle = scale * angle + offset
```

For an export that already contains a resultant angle, `direct_resultant` mode filters that column directly. These are **device-defined angular descriptors**, not anatomically calibrated joint angles.

### 4. Angular derivatives

The first and second derivatives are computed against the recorded time vector:

```text
velocity     = d(angle) / dt
acceleration = d(velocity) / dt
```

The code uses `numpy.gradient`, which supports the actual sample times instead of assuming a hidden sampling rate.

### 5. Phase segmentation

The caller provides explicit `[start, end]` windows for propulsion and recovery. This preserves the study's quality-control decision and keeps event boundaries auditable. The public code does not infer a clinical event automatically.

### 6. Temporal normalization

Each phase is interpolated independently to 100 equally spaced phase points. The output contains `phase`, `phase_percent`, `angle_deg`, `velocity_deg_s`, and `acceleration_deg_s2`. This makes within-phase curves comparable without sharing participant identifiers.

### 7. Export and provenance

Each run writes:

- `processed_signal.csv` — filtered angle and derivatives;
- `phase_normalized.csv` — 100 points per configured phase;
- `summary.json` — descriptive metrics;
- `pipeline_manifest.json` — input hash, parameters, software mode, and output schema;
- `angle_profile.png` — optional plot of the demo or a locally supplied signal.

## Run the reference implementation

From the repository root:

```powershell
python scripts\run_public_demo.py
```

Or install the package and invoke the CLI:

```powershell
python -m pip install -e .
wheelchair-pipeline run --input examples/synthetic/imu_trial.csv --output examples/synthetic/outputs
```

The exact demo configuration is visible in the generated manifest. No private path is needed.

## iSen and Kinovea roles

iSen is the primary source for the quantitative angular descriptors described in the public project documentation. Kinovea/videogrammetry is retained as supporting evidence for acquisition documentation, temporal alignment, cycle review, and quality control. The two modalities should not be treated as interchangeable measurements.
