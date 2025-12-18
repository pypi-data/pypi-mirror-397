"""Nimbus BCI classifiers - functional and sklearn-compatible APIs."""

# Functional API (existing)
from .nimbus_lda import nimbus_lda_fit, nimbus_lda_predict, nimbus_lda_predict_proba, nimbus_lda_update
from .nimbus_gmm import nimbus_gmm_fit, nimbus_gmm_predict, nimbus_gmm_predict_proba, nimbus_gmm_update
from .nimbus_softmax import (
    nimbus_softmax_fit,
    nimbus_softmax_predict,
    nimbus_softmax_predict_proba,
    nimbus_softmax_predict_samples,
    nimbus_softmax_update,
)

# sklearn-compatible classes (new)
from .nimbus_lda import NimbusLDA
from .nimbus_gmm import NimbusGMM
from .nimbus_softmax import NimbusSoftmax

# Base class for custom models
from .base import NimbusClassifierMixin

__all__ = [
    # Functional API
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
    # sklearn-compatible classes
    "NimbusLDA",
    "NimbusGMM",
    "NimbusSoftmax",
    "NimbusClassifierMixin",
]


