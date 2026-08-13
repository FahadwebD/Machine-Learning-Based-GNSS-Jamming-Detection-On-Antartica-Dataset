# Implementation Scripts

The thesis implementation is executed in numbered stages. The local working directory is `C:\GNSS_Thesis\scripts`.

## Script sequence

1. `01_audit_ubx.py` — streams the selected raw UBX files, counts available UBX message types, and saves decoded examples.
2. `02_extract_rf_spectrum.py` — extracts approximately 1 Hz receiver RF and spectrum features from MON-RF and MON-SPAN and creates the pilot label table.
3. `03_pilot_eda.py` — performs initial exploratory analysis and saves preliminary plots.
4. `04_extract_measx_features.py` — extracts satellite-level RXM-MEASX information, aggregates approximately 5 Hz observations to 1 Hz, and merges GNSS features with the RF/spectrum table.
5. `05_feature_screening.py` — compares candidate features within the mixed day and ranks standardised differences.
6. `06_ml_baseline.py` — trains Logistic Regression and Random Forest baseline classifiers, generates metrics/confusion matrices, and runs the unseen clean-day false-alarm stress test.
7. `07_grouped_validation.py` — implements grouped temporal validation so that neighbouring observations from the same temporal block cannot appear in both training and testing.

## Repository status

The audit and EDA scripts are stored in this repository. Additional local scripts are being copied into GitHub as the research record is consolidated. The raw UBX files are intentionally excluded from version control because of their size.

## Reproducibility note

The two-day work is a proof of concept. Final thesis processing will replace sequential alignment with explicit receiver timestamps and will expand validation to multiple clean and jamming days.
