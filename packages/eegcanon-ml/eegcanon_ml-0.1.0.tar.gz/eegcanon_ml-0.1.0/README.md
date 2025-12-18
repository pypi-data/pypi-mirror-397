# EEGCanon

EEGCanon is a Python framework that converts heterogeneous EEG data (EDF, CSV)
into a canonical, standardized representation for reproducible EEG
machine learning and signal analysis.

## Why EEGCanon?

EEG pipelines today suffer from:
- dataset-specific preprocessing
- inconsistent channel naming
- irreproducible ML results

EEGCanon introduces a **common EEG data contract**.

## Features

- Load EEG from EDF and CSV
- Canonical 10–20 channel mapping
- Sampling-rate normalization
- Structured warnings and provenance
- Epoching support
- Feature extraction (PSD, Bandpower, Hjorth)
- PyTorch dataset compatibility

## Installation

```bash
pip install eegcanon