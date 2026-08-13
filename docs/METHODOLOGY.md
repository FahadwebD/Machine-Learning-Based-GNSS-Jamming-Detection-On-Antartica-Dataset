# Methodology Notes

## Study design

This is a quantitative, dataset-based machine-learning study using publicly available real-world GNSS receiver data collected during a maritime expedition to Antarctica.

## Data source

Primary dataset: **Voyage to the Frozen Continent** Antarctica GNSS dataset, archived on Zenodo.

Pilot files:

- `20241010.ubx` — clean/reference day
- `20250324.ubx` — mixed normal/jamming day

Raw UBX data are not committed to this repository because of file size. The repository stores code, documentation, figures and small summary outputs only.

## Message streams

The pilot identified the following core streams:

- `MON-RF` at approximately 1 Hz
- `MON-SPAN` at approximately 1 Hz
- `RXM-MEASX` at approximately 5 Hz
- `NAV-SAT` at approximately 5 Hz
- `NAV-PVT` at approximately 5 Hz

## Feature construction

### MON-RF

Receiver-side RF diagnostics include receiver noise, AGC count, I/Q diagnostic fields, internal jamming state and internal jamming indicator.

Important leakage rule:

- `jamming_state` is used only to create the pilot reference label.
- `jamming_label` is the target variable.
- `jam_indicator` is excluded from predictors because it may be closely related to the receiver's internal jamming logic.

### MON-SPAN

Spectrum arrays are summarised into features such as:

- mean
- median
- standard deviation
- minimum
- maximum
- quartiles
- peak-bin index
- peak-above-median

### RXM-MEASX

Satellite-level observations include C/N0, Doppler and measurement-quality fields. In the pilot, approximately five consecutive MEASX epochs were aggregated to one approximately one-second row before merging with MON-RF/MON-SPAN.

## Pilot synchronisation

The current proof-of-concept aligns streams using sequential message order because MON-RF and MON-SPAN have nearly identical 1 Hz counts and RXM-MEASX is approximately 5 Hz.

This is a pilot simplification. The full thesis should replace this with explicit timestamp-based synchronisation using receiver/UTC time references and may integrate NAV-PVT/NAV-SAT if useful.

## Feature screening

Candidate predictors are compared between normal and receiver-reported jamming observations within the same mixed day. This reduces the risk of interpreting unrelated between-day differences as jamming effects.

A standardised difference is used as an initial effect-size screen:

```text
(jamming mean - normal mean) / pooled standard deviation
```

## Baseline models

- Logistic Regression
- Random Forest

Extended models such as SVM or XGBoost are considered only if they add clear value after the leakage-controlled baseline is established.

## Evaluation strategy

Three evaluation levels are planned:

1. **Conventional random split** — reference baseline only.
2. **Grouped temporal validation** — neighbouring observations remain inside the same temporal group.
3. **Held-out-day validation** — entire days are excluded from training and used only for testing.

The grouped and held-out-day protocols are the key evaluations because one-second observations from the same operating period are temporally correlated.

## Metrics

The study reports:

- accuracy
- balanced accuracy
- precision
- recall / detection rate
- F1-score
- false-alarm rate
- missed-detection rate
- PR-AUC
- ROC-AUC

Accuracy is treated as supporting information rather than the only model-selection criterion.

## Explainability

Current pilot analysis includes Random Forest feature importance. The full multi-day study will supplement this with permutation importance and, where useful and computationally feasible, SHAP.

## Current methodological limitations

- only two pilot days
- held-out day contains no positive jamming observations
- receiver-reported label rather than independent laboratory ground truth
- sequential rather than timestamp-based synchronisation
- model-specific feature importance
- possible day-specific distribution shift

These limitations are explicit and guide the remaining experiments.
