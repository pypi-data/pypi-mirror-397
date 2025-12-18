"""Streaming inference for real-time BCI classification.

This module provides chunk-by-chunk streaming inference
for real-time BCI applications.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

import numpy as np

from ..metrics.diagnostics import compute_entropy
from ..metrics.calibration import CalibrationMetrics, compute_calibration_metrics
from ..metrics.performance import compute_balance
from ..utils.feature_aggregation import aggregate_temporal_features
from ..data.validation import labels_to_zero_indexed, validate_chunk
from .aggregation import aggregate_chunks, compute_temporal_weights
from .dispatch import get_predict_proba_fn

if TYPE_CHECKING:
    from ..data.contracts import BCIMetadata
    from ..nimbus_io import NimbusModel


@dataclass
class ChunkResult:
    """Result from processing a single chunk.

    Attributes
    ----------
    prediction : int
        Predicted class for this chunk.
    confidence : float
        Confidence for this chunk (= max of posterior).
    posterior : np.ndarray
        Posterior distribution for this chunk.
    latency_ms : float
        Processing time for this chunk in milliseconds.
    """

    prediction: int
    confidence: float
    posterior: np.ndarray
    latency_ms: float


@dataclass
class StreamingResult:
    """Final result from a streaming trial.

    Attributes
    ----------
    prediction : int
        Aggregated prediction.
    confidence : float
        Aggregated confidence (= max of posterior).
    posterior : np.ndarray
        Aggregated posterior distribution.
    chunk_posteriors : list of np.ndarray
        Full posterior from each chunk (for visualization).
    entropy : float
        Shannon entropy of final posterior in bits.
    aggregation_method : str
        Method used for aggregation.
    n_chunks : int
        Number of chunks processed.
    latency_ms : float
        Total trial inference time in milliseconds.
    chunk_latencies_ms : list of float
        Latency for each chunk.
    balance : float
        Class distribution balance across chunks.
    calibration : CalibrationMetrics or None
        Calibration metrics if label was provided.
    """

    prediction: int
    confidence: float
    posterior: np.ndarray
    chunk_posteriors: list
    entropy: float
    aggregation_method: str
    n_chunks: int
    latency_ms: float
    chunk_latencies_ms: list
    balance: float
    calibration: Optional[CalibrationMetrics] = None


class StreamingSession:
    """Session for streaming BCI inference.

    Maintains state across chunks within a single trial.
    Provides chunk-by-chunk processing for real-time applications.

    Parameters
    ----------
    model : NimbusModel
        Fitted Nimbus model.
    metadata : BCIMetadata
        Metadata describing the data format.

    Examples
    --------
    >>> from nimbus_pysdk.inference import StreamingSession
    >>> session = StreamingSession(model, metadata)
    >>>
    >>> for chunk in eeg_stream:
    ...     result = session.process_chunk(chunk)
    ...     print(f"Chunk: {result.prediction} ({result.confidence:.2f})")
    >>>
    >>> final = session.finalize_trial(method="weighted_vote")
    >>> print(f"Final: {final.prediction}")
    """

    def __init__(self, model: "NimbusModel", metadata: "BCIMetadata"):
        self.model = model
        self.metadata = metadata
        self.label_base = int(np.asarray(model.params.get("label_base", 0), dtype=np.int64))
        self._predict_proba = get_predict_proba_fn(model)

        # Session state
        self._chunk_predictions: list[int] = []
        self._chunk_confidences: list[float] = []
        self._chunk_posteriors: list[np.ndarray] = []
        self._chunk_latencies_ms: list[float] = []
        self._trial_active: bool = False
        self._chunk_count: int = 0

        # Validate compatibility
        model_n_classes = int(model.params.get("n_classes", 0))
        if model_n_classes != metadata.n_classes:
            raise ValueError(
                f"Model has {model_n_classes} classes, "
                f"but metadata specifies {metadata.n_classes}"
            )

    @property
    def is_active(self) -> bool:
        """Check if a trial is currently active."""
        return self._trial_active

    @property
    def chunk_count(self) -> int:
        """Number of chunks processed in current trial."""
        return self._chunk_count

    def process_chunk(
        self,
        chunk: np.ndarray,
        *,
        num_posterior_samples: int = 20,
        rng_seed: Optional[int] = None,
    ) -> ChunkResult:
        """Process a single chunk of EEG features.

        Parameters
        ----------
        chunk : np.ndarray
            Chunk features of shape (n_features, n_samples).
        num_posterior_samples : int, default=20
            Samples for softmax prediction.
        rng_seed : int, optional
            Random seed. Defaults to chunk_count.

        Returns
        -------
        ChunkResult
            Result for this chunk.
        """
        start_time = time.perf_counter()

        # Validate chunk
        chunk = np.asarray(chunk, dtype=np.float64)
        validate_chunk(chunk, self.metadata)

        # Aggregate temporal dimension
        aggregated = aggregate_temporal_features(
            chunk, self.metadata.temporal_aggregation
        )
        X = aggregated.reshape(1, -1)  # (1, n_features)

        # Run inference
        rng_seed = rng_seed if rng_seed is not None else self._chunk_count
        posterior = self._predict_proba(
            X,
            num_posterior_samples=num_posterior_samples,
            rng_seed=rng_seed,
        )[0]

        # Extract prediction and confidence
        prediction0 = int(np.argmax(posterior))
        prediction = int(prediction0 + self.label_base)
        confidence = float(np.max(posterior))
        latency_ms = (time.perf_counter() - start_time) * 1000

        # Update session state
        self._chunk_predictions.append(prediction0)
        self._chunk_confidences.append(confidence)
        self._chunk_posteriors.append(posterior.copy())
        self._chunk_latencies_ms.append(latency_ms)
        self._chunk_count += 1
        self._trial_active = True

        return ChunkResult(
            prediction=prediction,
            confidence=confidence,
            posterior=posterior,
            latency_ms=latency_ms,
        )

    def finalize_trial(
        self,
        *,
        method: str = "weighted_vote",
        temporal_weighting: bool = True,
        label: Optional[int] = None,
    ) -> StreamingResult:
        """Finalize trial by aggregating chunk predictions.

        Parameters
        ----------
        method : str, default="weighted_vote"
            Aggregation method:
            - "weighted_vote": Confidence-weighted voting
            - "max_confidence": Use highest confidence chunk
            - "posterior_mean": Average posteriors (Bayesian)
        temporal_weighting : bool, default=True
            Apply paradigm-specific temporal weights.
        label : int, optional
            True label for calibration metrics.

        Returns
        -------
        StreamingResult
            Aggregated trial result.
        """
        if not self._trial_active or self._chunk_count == 0:
            raise ValueError("No active trial. Process at least one chunk first.")

        n_classes = self.metadata.n_classes

        # Apply temporal weighting if requested
        confidences_to_use = self._chunk_confidences.copy()

        if temporal_weighting and self._chunk_count > 1:
            weights = compute_temporal_weights(
                self.metadata.paradigm, self._chunk_count
            )
            confidences_to_use = [c * w for c, w in zip(confidences_to_use, weights)]

        # Aggregate predictions
        final_pred0, final_conf, final_posterior = aggregate_chunks(
            self._chunk_predictions,
            confidences_to_use,
            n_classes,
            posteriors=self._chunk_posteriors,
            method=method,
        )
        final_pred = int(final_pred0 + self.label_base)

        # Compute final entropy
        final_entropy = compute_entropy(final_posterior)

        # Compute balance
        balance = compute_balance(np.array(self._chunk_predictions), n_classes)

        # Total latency
        total_latency_ms = sum(self._chunk_latencies_ms)

        # Calibration metrics if label provided
        calibration = None
        if label is not None:
            lab0 = labels_to_zero_indexed(
                np.asarray([label]),
                n_classes=n_classes,
                label_base=self.label_base,
            )[0]
            labels_vec = np.full(self._chunk_count, int(lab0), dtype=np.int64)
            calibration = compute_calibration_metrics(
                np.array(self._chunk_predictions),
                np.array(self._chunk_confidences),
                labels_vec,
            )

        result = StreamingResult(
            prediction=final_pred,
            confidence=final_conf,
            posterior=final_posterior,
            chunk_posteriors=[p.copy() for p in self._chunk_posteriors],
            entropy=final_entropy,
            aggregation_method=method,
            n_chunks=self._chunk_count,
            latency_ms=total_latency_ms,
            chunk_latencies_ms=self._chunk_latencies_ms.copy(),
            balance=balance,
            calibration=calibration,
        )

        # Reset for next trial
        self.reset()

        return result

    def reset(self):
        """Reset session for next trial."""
        self._chunk_predictions.clear()
        self._chunk_confidences.clear()
        self._chunk_posteriors.clear()
        self._chunk_latencies_ms.clear()
        self._trial_active = False
        self._chunk_count = 0


