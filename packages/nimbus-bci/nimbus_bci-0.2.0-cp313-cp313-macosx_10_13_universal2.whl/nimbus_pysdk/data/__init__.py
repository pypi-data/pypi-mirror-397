"""Data contracts and validation for BCI data."""

from .contracts import BCIData, BCIMetadata
from .validation import validate_data, check_model_compatibility

__all__ = [
    "BCIData",
    "BCIMetadata",
    "validate_data",
    "check_model_compatibility",
]

