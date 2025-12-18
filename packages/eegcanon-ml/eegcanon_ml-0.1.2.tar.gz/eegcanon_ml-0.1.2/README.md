# EEGCanon-ML 🧠⚡

EEGCanon-ML is a Python framework that converts heterogeneous EEG data
(EDF, CSV) into a **canonical, standardized representation** for
reproducible machine learning and signal analysis.

It provides a **common EEG data language** so that models, features,
and experiments can be compared fairly across datasets.

---

## Why EEGCanon-ML?

EEG workflows today suffer from:
- dataset-specific preprocessing scripts
- inconsistent channel naming
- incompatible sampling rates
- poor reproducibility across studies

**EEGCanon-ML enforces a standard EEG contract.**

---

## Key Features

- Unified EEG loading (EDF, CSV)
- Canonical 10-20 channel mapping
- Sampling-rate normalization
- Structured warnings & provenance tracking
- Epoching support
- Feature extraction (PSD, Bandpower, Hjorth)
- PyTorch-ready datasets

---

## Installation

```bash
pip install eegcanon-ml


