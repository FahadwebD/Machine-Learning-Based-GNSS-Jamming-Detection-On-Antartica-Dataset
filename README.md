# Machine Learning-Based GNSS Jamming Detection and Temporal Generalisation

**Real-world maritime receiver and spectrum measurements from the Antarctica expedition dataset**

This repository documents the implementation for my MR603/Master of Research thesis on machine-learning-based GNSS jamming detection using real-world maritime GNSS receiver data. The project focuses not only on classification accuracy, but on whether a detector remains reliable when operating conditions change across time and across days.

## Current research direction

The study uses the public **“Voyage to the Frozen Continent”** Antarctica maritime GNSS dataset and combines multiple receiver information sources:

- `MON-RF` — receiver RF diagnostics and receiver-reported jamming state
- `MON-SPAN` — RF spectrum measurements
- `RXM-MEASX` — satellite-level C/N0, Doppler and measurement-quality information
- `NAV-SAT` / `NAV-PVT` — available for later timestamp-based synchronisation and additional navigation-quality features

The central research question is whether strong performance under a conventional random train/test split remains reliable under grouped temporal and held-out-day evaluation.

## Pilot implementation completed

Two raw UBX days were used for the proof of concept:

| Day | Role | Approx. 1-second rows | Receiver-reported label profile |
|---|---|---:|---|
| 2024-10-10 | Clean reference day | 86,399 | 86,399 normal; 0 jamming |
| 2025-03-24 | Mixed/high-interference day | 86,395 | 51,401 normal; 34,994 jamming |
| **Combined** | Pilot dataset | **172,794** | **137,800 normal; 34,994 jamming** |

The raw files were parsed directly with Python/`pyubx2`. Approximately 1.47 million UBX messages were decoded from each pilot day.

## Preliminary findings

### Feature screening

Within 24 March 2025, the largest preliminary univariate separation was observed in satellite-measurement count. Mean C/N0 was almost unchanged between the two receiver-reported conditions.

- Mean satellite count: 24.658 normal vs 23.332 jamming
- Maximum C/N0: 49.924 vs 49.457 dB-Hz
- Mean absolute Doppler: 1694.407 vs 1656.932 Hz
- Receiver noise per ms: 76.676 vs 77.388
- Mean C/N0: 41.492 vs 41.491 dB-Hz

This supports a multi-feature approach rather than relying on a single mean-C/N0 threshold.

### Baseline machine learning

A conventional stratified 70/30 random split within 24 March produced:

| Model | Accuracy | Precision | Recall | F1 | False-alarm rate | PR-AUC | ROC-AUC |
|---|---:|---:|---:|---:|---:|---:|---:|
| Logistic Regression | 0.7125 | 0.6265 | 0.7189 | 0.6695 | 0.2918 | 0.7098 | 0.7925 |
| Random Forest | 0.8787 | 0.8283 | 0.8839 | 0.8552 | 0.1248 | 0.9355 | 0.9528 |

These are **pilot baseline results only**. Because one-second observations are temporally correlated, random observation-level splitting may overestimate performance.

### Unseen clean-day stress test

Models trained on 24 March were then applied without retraining to the completely unseen clean day of 10 October 2024:

| Model | Clean rows | Predicted jamming | False-alarm rate |
|---|---:|---:|---:|
| Logistic Regression | 86,399 | 45 | ~0.05% |
| Random Forest | 86,399 | 31,063 | 35.95% |

This does **not** yet constitute a complete cross-day sensitivity test because the unseen day contains no positive jamming observations. It is specifically an unseen-normal false-alarm stress test.

## Data-leakage controls

Two leakage risks are treated separately:

1. **Target leakage** — `jamming_state`, the derived `jamming_label`, and the internal receiver `jam_indicator` are excluded from model predictors.
2. **Temporal train/test leakage** — neighbouring one-second observations can be strongly correlated. Following supervisor feedback, grouped temporal validation is being added so that complete temporal blocks are assigned exclusively to training or testing.

The next validation stage compares:

- conventional random split
- grouped temporal cross-validation with non-overlapping blocks
- held-out-day evaluation across multiple clean and jamming days

## Repository structure

```text
.
├── README.md
├── requirements.txt
├── .gitignore
├── scripts/
│   ├── 01_audit_ubx.py
│   ├── 02_extract_rf_spectrum.py
│   ├── 03_pilot_eda.py
│   ├── 04_extract_measx_features.py
│   ├── 05_feature_screening.py
│   ├── 06_ml_baseline.py
│   └── 07_grouped_validation.py
├── docs/
│   ├── PROGRESS.md
│   ├── METHODOLOGY.md
│   └── SUPERVISOR_FEEDBACK.md
├── results/
│   └── README.md
├── figures/
│   └── README.md
└── evidence/
    └── README.md
```

## Dataset

The raw Antarctica UBX archive is **not stored in this repository** because the source files are very large. The dataset is publicly available from Zenodo:

- Voyage to the Frozen Continent / Antarctica GNSS dataset
- Zenodo record: https://zenodo.org/records/15783534

For the pilot, only selected daily UBX members were downloaded and processed locally.

## Reproducibility

Install dependencies with:

```bash
python -m pip install -r requirements.txt
```

The intended script order is:

```text
01 audit raw UBX messages
02 extract MON-RF and MON-SPAN features
03 exploratory analysis
04 extract RXM-MEASX GNSS features and merge
05 feature screening
06 baseline ML evaluation
07 grouped temporal validation
```

## Current limitations

- Two-day pilot only
- Unseen external day is clean only
- Receiver-reported jamming state is a reference label, not independent laboratory ground truth
- Pilot synchronisation uses sequential message order rather than explicit receiver timestamps
- NAV-SAT and NAV-PVT are not yet integrated into the final analytical table
- Current Random Forest feature importance is model-specific
- Countermeasure selection is deliberately outside the current core scope

## Next work

1. Complete grouped temporal validation with zero train/test group overlap.
2. Compare random-split and grouped-validation performance.
3. Replace sequential alignment with explicit timestamp-based synchronisation.
4. Add multiple clean and jamming days from separated voyage periods.
5. Evaluate held-out jamming days, not only unseen clean days.
6. Add permutation importance and, if useful, SHAP explainability.

## Thesis working title

**Machine Learning-Based GNSS Jamming Detection and Temporal Generalisation Using Real-World Maritime Receiver and Spectrum Measurements**

---

This repository is a research implementation and progress record. Preliminary results should not be interpreted as deployment-ready GNSS jamming detection performance until the planned multi-day temporal validation is completed.
