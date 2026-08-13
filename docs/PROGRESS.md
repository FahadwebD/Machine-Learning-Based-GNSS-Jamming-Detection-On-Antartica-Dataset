# Thesis Implementation Progress

## Current status

**Two-day pilot implementation completed. Grouped temporal validation and multi-day extension are the next stages.**

## Working title

Machine Learning-Based GNSS Jamming Detection and Temporal Generalisation Using Real-World Maritime Receiver and Spectrum Measurements

## Completed pilot workflow

1. Selected two raw Antarctica UBX days.
2. Parsed raw UBX binary streams using `pyubx2`.
3. Audited available receiver message types.
4. Inspected exact MON-RF and MON-SPAN fields.
5. Extracted approximately 1 Hz RF and spectrum features.
6. Built a preliminary binary label from receiver-reported MON-RF jamming state.
7. Extracted RXM-MEASX satellite-level C/N0, Doppler and measurement-quality features.
8. Aggregated RXM-MEASX from approximately 5 Hz to approximately 1 Hz.
9. Merged GNSS, RF and spectrum features into one pilot table.
10. Performed within-day feature screening.
11. Trained Logistic Regression and Random Forest baselines.
12. Evaluated a conventional stratified random split.
13. Performed an unseen clean-day false-alarm stress test.
14. Received supervisor feedback to strengthen leakage control through grouping.

## Pilot data

| Day | Role | Rows | Label profile |
|---|---|---:|---|
| 2024-10-10 | Clean reference | 86,399 | 86,399 normal; 0 jamming |
| 2025-03-24 | Mixed/high-interference | 86,395 | 51,401 normal; 34,994 jamming |
| Combined | Pilot | 172,794 | 137,800 normal; 34,994 jamming |

## UBX audit

| Message | 2024-10-10 | 2025-03-24 | Pilot use |
|---|---:|---:|---|
| NAV-PVT | 431,996 | 431,971 | available; not yet integrated |
| NAV-SAT | 431,996 | 431,971 | available; not yet integrated |
| RXM-MEASX | 431,994 | 431,971 | GNSS feature extraction |
| MON-RF | 86,399 | 86,395 | RF diagnostics + reference label |
| MON-SPAN | 86,399 | 86,395 | spectrum features |
| RXM-RLM | 2,593 | 1,068 | not used in current model |

## Feature-screening results from 24 March 2025

| Feature | Normal mean | Jamming mean | Standardised difference |
|---|---:|---:|---:|
| Mean satellite count | 24.658 | 23.332 | -0.656 |
| Valid C/N0 count | 24.658 | 23.332 | -0.656 |
| Maximum C/N0 | 49.924 | 49.457 | -0.423 |
| Mean absolute Doppler (Hz) | 1694.407 | 1656.932 | -0.297 |
| C/N0 standard deviation | 5.570 | 5.371 | -0.247 |
| Minimum C/N0 | 26.711 | 27.394 | +0.226 |
| Receiver noise per ms | 76.676 | 77.388 | +0.173 |
| Spectrum standard deviation | 10.587 | 10.634 | +0.111 |
| Mean C/N0 | 41.492 | 41.491 | ~0.000 |

## Baseline ML results

### Within-day stratified random split

| Metric | Logistic Regression | Random Forest |
|---|---:|---:|
| Accuracy | 0.7125 | 0.8787 |
| Balanced accuracy | 0.7135 | 0.8796 |
| Precision | 0.6265 | 0.8283 |
| Recall | 0.7189 | 0.8839 |
| F1 | 0.6695 | 0.8552 |
| False-alarm rate | 0.2918 | 0.1248 |
| Missed-detection rate | 0.2811 | 0.1161 |
| PR-AUC | 0.7098 | 0.9355 |
| ROC-AUC | 0.7925 | 0.9528 |

### Unseen clean-day stress test

Models trained on all of 24 March were applied without retraining to 10 October.

| Model | Unseen clean rows | Predicted jamming | False-alarm rate |
|---|---:|---:|---:|
| Logistic Regression | 86,399 | 45 | ~0.05% |
| Random Forest | 86,399 | 31,063 | 35.95% |

This test measures unseen-day false alarms only. It does not yet measure cross-day jamming sensitivity because the held-out day contains no jamming positives.

## Supervisor feedback incorporated

The latest feedback emphasised the need to ensure that training and testing data do not leak information through temporal proximity. The next experiment therefore uses grouped temporal validation so neighbouring one-second observations remain inside the same train/test group.

## Next work

- Complete grouped temporal cross-validation and confirm zero group overlap.
- Compare random-split vs grouped-validation performance.
- Test multiple block sizes or event-based grouping.
- Expand to multiple clean and jamming days.
- Replace sequential alignment with timestamp-based synchronisation.
- Evaluate truly held-out jamming days.
- Add permutation importance and, if useful, SHAP.
