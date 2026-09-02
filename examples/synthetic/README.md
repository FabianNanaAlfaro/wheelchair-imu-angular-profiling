# Synthetic example

`imu_trial.csv` is generated deterministically by `scripts/run_public_demo.py` using a fixed seed. It has no participant provenance and is included only to prove that the public code runs without the restricted acquisition store.

The demo uses:

- 100 Hz sampling;
- a 6 Hz, fourth-order zero-phase low-pass filter;
- an explicit neutral window of 0.2–1.0 s;
- propulsion and recovery windows of 0–2.0 s and 2.0–3.99 s;
- 100 normalized points per phase.

Generated outputs are ignored by Git. To recreate them:

```powershell
python scripts\run_public_demo.py
```
