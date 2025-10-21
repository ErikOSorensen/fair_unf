"""Universal Numerical Fingerprint (UNF) calculation library.

This library implements the UNF v6 specification for creating cryptographic
fingerprints of datasets. UNF provides a way to verify data integrity and
detect changes in datasets.
"""

from .unf import calculate_unf, combine_unfs, calculate_dataset_unf, UNFConfig
from .normalize import (
    normalize_numeric,
    normalize_string,
    normalize_boolean,
    normalize_date,
    normalize_datetime,
)

__version__ = "0.1.0"

__all__ = [
    "calculate_unf",
    "combine_unfs",
    "calculate_dataset_unf",
    "UNFConfig",
    "normalize_numeric",
    "normalize_string",
    "normalize_boolean",
    "normalize_date",
    "normalize_datetime",
]
