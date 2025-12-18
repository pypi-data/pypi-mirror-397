# nimbus-bci

Bayesian BCI classifiers with **sklearn compatibility**, **streaming inference**, and **rich diagnostics**.

[![PyPI](https://img.shields.io/pypi/v/nimbus-bci)](https://pypi.org/project/nimbus-bci/)
[![Python](https://img.shields.io/pypi/pyversions/nimbus-bci)](https://pypi.org/project/nimbus-bci/)
[![License](https://img.shields.io/badge/license-Proprietary-blue)](LICENSE.txt)

## Features

- 🧠 **Three Bayesian classifiers**: LDA, GMM/QDA, and Softmax (Polya-Gamma)
- 🔧 **sklearn-compatible API**: Works with pipelines, cross-validation, and GridSearchCV
- 📊 **Streaming inference**: Real-time chunk-by-chunk processing
- 📈 **Rich diagnostics**: Entropy, Mahalanobis distance, calibration metrics (ECE/MCE)
- 🔄 **Online learning**: Update models with new data without retraining
- 🎯 **BCI-specific utilities**: ITR calculation, temporal aggregation, quality assessment
- 🔌 **MNE-Python integration**: Convert between MNE Epochs and Nimbus data formats

## Installation

```bash
pip install nimbus-bci
```

**From source:**
```bash
git clone https://github.com/nimbusbci/nimbuspysdk.git
cd nimbuspysdk
pip install -e ".[all]"
```

## Quick Start

### sklearn-Compatible API (Recommended)

```python
from nimbus_bci import NimbusLDA, NimbusGMM, NimbusSoftmax
import numpy as np

# Create and fit classifier
clf = NimbusLDA()
clf.fit(X_train, y_train)

# Predict
predictions = clf.predict(X_test)
probabilities = clf.predict_proba(X_test)

# Online learning
clf.partial_fit(X_new, y_new)
```

### Works with sklearn Pipelines

```python
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score, GridSearchCV

# Simple pipeline
pipe = make_pipeline(StandardScaler(), NimbusLDA())
pipe.fit(X_train, y_train)

# Cross-validation
scores = cross_val_score(NimbusLDA(), X, y, cv=5)
print(f"Accuracy: {scores.mean():.2%} (+/- {scores.std():.2%})")

# Hyperparameter tuning
param_grid = {'mu_scale': [1.0, 3.0, 5.0], 'class_prior_alpha': [0.5, 1.0]}
grid = GridSearchCV(NimbusLDA(), param_grid, cv=5)
grid.fit(X, y)
print(f"Best params: {grid.best_params_}")
```

### Streaming Inference (Real-Time BCI)

```python
from nimbus_bci import NimbusLDA, StreamingSession
from nimbus_bci.data import BCIMetadata

# Setup
metadata = BCIMetadata(
    sampling_rate=250.0,
    paradigm="motor_imagery",
    feature_type="csp",
    n_features=16,
    n_classes=4,
    chunk_size=125,  # 500ms chunks
    temporal_aggregation="logvar",
)

# Train model
clf = NimbusLDA()
clf.fit(X_train, y_train)

# Create streaming session
session = StreamingSession(clf.model_, metadata)

# Process chunks in real-time
for chunk in eeg_stream:
    result = session.process_chunk(chunk)
    print(f"Chunk prediction: {result.prediction} ({result.confidence:.2%})")

# Finalize trial with aggregation
final = session.finalize_trial(method="weighted_vote")
print(f"Final: class {final.prediction} (entropy: {final.entropy:.2f} bits)")
```

### Batch Inference with Diagnostics

```python
from nimbus_bci import predict_batch
from nimbus_bci.data import BCIData, BCIMetadata

# Create BCI data container
metadata = BCIMetadata(
    sampling_rate=250.0,
    paradigm="motor_imagery",
    feature_type="csp",
    n_features=16,
    n_classes=4,
)
data = BCIData(features, metadata, labels)

# Run batch inference with full diagnostics
result = predict_batch(model, data)

print(f"Mean entropy: {result.mean_entropy:.2f} bits")
print(f"Balance: {result.balance:.2%}")
print(f"ECE: {result.calibration.ece:.3f}")
print(f"Latency: {result.latency_ms:.1f}ms")
```

### MNE-Python Integration

```python
import mne
from nimbus_bci import NimbusLDA
from nimbus_bci.compat import from_mne_epochs, extract_csp_features

# Load and preprocess with MNE
raw = mne.io.read_raw_gdf("motor_imagery.gdf")
events = mne.find_events(raw)
epochs = mne.Epochs(raw, events, tmin=0, tmax=4, baseline=None, preload=True)
epochs.filter(8, 30)  # Mu + Beta bands

# Extract CSP features
csp_features, csp = extract_csp_features(epochs, n_components=8)

# Train Nimbus classifier
clf = NimbusLDA()
clf.fit(csp_features, epochs.events[:, 2])
```

## Available Classifiers

| Classifier | Description | Best For |
|------------|-------------|----------|
| `NimbusLDA` | Bayesian LDA with shared covariance | Fast, when classes have similar shapes |
| `NimbusGMM` | Bayesian GMM with class-specific covariances | Complex class distributions |
| `NimbusSoftmax` | Bayesian logistic regression (Polya-Gamma VI) | Non-Gaussian decision boundaries |

## Metrics & Diagnostics

```python
from nimbus_bci import (
    compute_entropy,            # Prediction uncertainty
    compute_calibration_metrics,  # ECE, MCE
    calculate_itr,              # Information Transfer Rate
    assess_trial_quality,       # Quality checks
)

# Entropy (uncertainty)
entropy = compute_entropy(posterior)  # bits

# Calibration
calib = compute_calibration_metrics(predictions, confidences, labels)
print(f"ECE: {calib.ece:.3f}, MCE: {calib.mce:.3f}")

# ITR
itr = calculate_itr(accuracy=0.85, n_classes=4, trial_duration=4.0)
print(f"ITR: {itr:.1f} bits/min")
```

## Normalization

Critical for cross-session BCI performance:

```python
from nimbus_bci import estimate_normalization_params, apply_normalization

# Estimate from training data
params = estimate_normalization_params(X_train, method="zscore")

# Apply to all data
X_train_norm = apply_normalization(X_train, params)
X_test_norm = apply_normalization(X_test, params)  # Same params!
```

## Project Structure

```
nimbus_bci/
├── models/              # Classifiers
│   ├── nimbus_lda/     # LDA (shared covariance)
│   ├── nimbus_gmm/     # GMM (class-specific covariances)
│   └── nimbus_softmax/ # Softmax (Polya-Gamma)
├── data/               # Data contracts (BCIData, BCIMetadata)
├── inference/          # Batch and streaming inference
├── metrics/            # Diagnostics, calibration, ITR
├── utils/              # Normalization, aggregation
└── compat/             # sklearn/MNE compatibility
```

## Functional API (Backward Compatible)

The original functional API is still available:

```python
from nimbus_bci import (
    nimbus_lda_fit, nimbus_lda_predict, nimbus_lda_update,
    nimbus_gmm_fit, nimbus_gmm_predict,
    nimbus_softmax_fit, nimbus_softmax_predict,
    nimbus_save, nimbus_load,
)

# Fit model
model = nimbus_lda_fit(X, y, n_classes=4, label_base=0, ...)

# Predict
probs = nimbus_lda_predict_proba(model, X_test)

# Update (online learning)
model = nimbus_lda_update(model, X_new, y_new)

# Save/load
nimbus_save(model, "model.npz")
model = nimbus_load("model.npz")
```

## Testing

```bash
pip install -e ".[dev]"
pytest -v
```

## Requirements

- Python ≥ 3.10
- NumPy ≥ 1.26
- JAX ≥ 0.4.25
- NumPyro ≥ 0.14.0
- scikit-learn ≥ 1.4

Optional:
- MNE ≥ 1.6 (for EEG integration)
- matplotlib ≥ 3.8 (for visualization)

## License

This software is **proprietary** and requires a valid license for use.

### License Tiers

| Tier | Use Case |
|------|----------|
| **Evaluation** | 30-day free trial for R&D |
| **Academic** | University research (free) |
| **Startup** | Companies < $1M revenue |
| **Commercial** | Full production rights |
| **Enterprise** | Unlimited deployments + SLA |
| **OEM/Embedded** | Medical devices, FDA support |

### Request Access

To obtain a license:
1. Email **hello@nimbusbci.com** with your use case
2. Receive API key and license agreement
3. Install and start building

**Website:** https://nimbusbci.com

---

© 2024-2025 [Nimbus BCI Inc.](https://nimbusbci.com) — The AI Engine for Brain-Computer Interfaces
