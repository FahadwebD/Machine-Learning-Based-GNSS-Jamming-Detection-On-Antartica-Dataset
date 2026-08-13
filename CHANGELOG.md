# Project Changelog

## 2026-08-14

- Confirmed the working thesis title.
- Consolidated the repository README and methodology documentation.
- Added the raw UBX audit script and pilot exploratory-analysis script.
- Documented the seven-stage implementation pipeline.
- Added reproducibility requirements and repository exclusions for large raw data files.
- Recorded the two-day pilot results and the need for stricter temporal validation.

## Pilot milestones completed

- Selected two raw UBX pilot days.
- Parsed and audited raw receiver messages.
- Constructed the approximately one-second RF/spectrum table.
- Integrated satellite-level GNSS measurements into the pilot dataset.
- Screened candidate features.
- Trained Logistic Regression and Random Forest baselines.
- Performed an external clean-day false-alarm stress test.

## Current milestone

Implement grouped temporal validation and compare it with the conventional random observation-level baseline before expanding to multiple clean and interference days.
