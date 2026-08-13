# Supervisor Feedback Log

This file records methodological feedback and the implementation changes made in response.

## 14 August 2026 — Data leakage and grouped validation

### Feedback
The supervisor requested an evaluation strategy that prevents data leakage, specifically suggesting grouping so that closely related observations are not split between training and testing.

### Why this matters
The pilot dataset contains approximately one-second observations. A conventional random split can place neighbouring seconds from the same operating period in both the training and testing sets. These samples can be strongly correlated because they share satellite geometry, vessel motion, receiver conditions and the same interference episode.

### Action taken
A new script, `scripts/07_grouped_validation.py`, was added.

It:
- creates 10-minute temporal groups (600 consecutive seconds per group),
- uses `StratifiedGroupKFold` with five folds,
- assigns each complete temporal group to either training or testing within a fold,
- explicitly checks that the intersection of training and testing group IDs is zero,
- reports grouped accuracy, balanced accuracy, precision, recall, F1, false-alarm rate, missed-detection rate, PR-AUC and ROC-AUC,
- compares grouped validation against the earlier conventional random-split baseline when the baseline CSV is available.

### Interpretation rule
The 10-minute block size is a pilot grouping choice rather than a final scientific claim. The full thesis will strengthen this by testing multiple temporal block sizes and, most importantly, by holding out complete operating days once additional clean and jamming days have been processed.

### Planned evidence
The terminal output should show `group_overlap = 0` for every fold. This will be retained as implementation evidence for the supervisor and thesis methodology record.
