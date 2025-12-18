"""NimbusPySDK: Bayesian classifiers for BCI applications.

This SDK provides sklearn-compatible Bayesian classifiers with
support for streaming inference, online learning, and rich diagnostics.

Examples
--------
Basic usage with sklearn-compatible API:

>>> from nimbus_pysdk import NimbusLDA
>>> clf = NimbusLDA()
>>> clf.fit(X_train, y_train)
>>> predictions = clf.predict(X_test)

Using with sklearn pipelines:

>>> from sklearn.pipeline import make_pipeline
>>> from sklearn.preprocessing import StandardScaler
>>> pipe = make_pipeline(StandardScaler(), NimbusLDA())
>>> pipe.fit(X_train, y_train)

Streaming inference:

>>> from nimbus_pysdk.inference import StreamingSession
>>> session = StreamingSession(model, metadata)
>>> for chunk in eeg_stream:
...     result = session.process_chunk(chunk)
>>> final = session.finalize_trial()
"""

# Core model I/O
from .nimbus_io import NimbusModel, nimbus_load, nimbus_save

# Functional API (backward compatible)
from .models.nimbus_lda import (
    nimbus_lda_fit,
    nimbus_lda_predict,
    nimbus_lda_predict_proba,
    nimbus_lda_update,
)
from .models.nimbus_gmm import (
    nimbus_gmm_fit,
    nimbus_gmm_predict,
    nimbus_gmm_predict_proba,
    nimbus_gmm_update,
)
from .models.nimbus_softmax import (
    nimbus_softmax_fit,
    nimbus_softmax_predict,
    nimbus_softmax_predict_proba,
    nimbus_softmax_predict_samples,
    nimbus_softmax_update,
)

# sklearn-compatible classifier classes
from .models import NimbusLDA, NimbusGMM, NimbusSoftmax

# Data contracts
from .data import BCIData, BCIMetadata, validate_data, check_model_compatibility

# Inference modules
from .inference import (
    predict_batch,
    BatchResult,
    StreamingSession,
    ChunkResult,
    StreamingResult,
    aggregate_chunks,
    compute_temporal_weights,
)

# Metrics
from .metrics import (
    compute_entropy,
    compute_mahalanobis_distances,
    compute_outlier_scores,
    CalibrationMetrics,
    compute_calibration_metrics,
    calculate_itr,
    compute_balance,
    OnlinePerformanceTracker,
    TrialQuality,
    assess_trial_quality,
    should_reject_trial,
)

# Utilities
from .utils import (
    aggregate_temporal_features,
    NormalizationParams,
    NormalizationStatus,
    estimate_normalization_params,
    apply_normalization,
    check_normalization_status,
    PreprocessingReport,
    diagnose_preprocessing,
    compute_fisher_score,
    rank_features_by_discriminability,
)

# MNE compatibility (lazy imports to avoid hard dependency)
from .compat import (
    from_mne_epochs,
    to_mne_epochs,
    extract_csp_features,
    extract_bandpower_features,
    create_bci_pipeline,
)

__version__ = "0.2.0"

__all__ = [
    # Version
    "__version__",
    # Core I/O
    "NimbusModel",
    "nimbus_save",
    "nimbus_load",
    # Functional API (backward compatible)
    "nimbus_lda_fit",
    "nimbus_lda_update",
    "nimbus_lda_predict_proba",
    "nimbus_lda_predict",
    "nimbus_gmm_fit",
    "nimbus_gmm_update",
    "nimbus_gmm_predict_proba",
    "nimbus_gmm_predict",
    "nimbus_softmax_fit",
    "nimbus_softmax_update",
    "nimbus_softmax_predict_proba",
    "nimbus_softmax_predict",
    "nimbus_softmax_predict_samples",
    # sklearn-compatible classifier classes
    "NimbusLDA",
    "NimbusGMM",
    "NimbusSoftmax",
    # Data contracts
    "BCIData",
    "BCIMetadata",
    "validate_data",
    "check_model_compatibility",
    # Inference
    "predict_batch",
    "BatchResult",
    "StreamingSession",
    "ChunkResult",
    "StreamingResult",
    "aggregate_chunks",
    "compute_temporal_weights",
    # Metrics
    "compute_entropy",
    "compute_mahalanobis_distances",
    "compute_outlier_scores",
    "CalibrationMetrics",
    "compute_calibration_metrics",
    "calculate_itr",
    "compute_balance",
    "OnlinePerformanceTracker",
    "TrialQuality",
    "assess_trial_quality",
    "should_reject_trial",
    # Utilities
    "aggregate_temporal_features",
    "NormalizationParams",
    "NormalizationStatus",
    "estimate_normalization_params",
    "apply_normalization",
    "check_normalization_status",
    "PreprocessingReport",
    "diagnose_preprocessing",
    "compute_fisher_score",
    "rank_features_by_discriminability",
    # MNE compatibility
    "from_mne_epochs",
    "to_mne_epochs",
    "extract_csp_features",
    "extract_bandpower_features",
    "create_bci_pipeline",
]
