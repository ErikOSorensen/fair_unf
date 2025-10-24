"""Core UNF calculation functions.

This module implements the main UNF fingerprint calculation and combination
logic according to the UNF v6 specification.
"""

import hashlib
import base64
from typing import Any, Sequence
from .normalize import (
    normalize_numeric,
    normalize_string,
    normalize_boolean,
    normalize_date,
    normalize_datetime,
)


class UNFConfig:
    """Configuration for UNF calculation."""

    def __init__(
        self,
        version: int = 6,
        precision: int = 7,
        max_chars: int = 128,
        hash_bits: int = 128,
        truncate: bool = False,
    ):
        """Initialize UNF configuration.

        Args:
            version: UNF version (currently only 6 is supported).
            precision: Number of significant digits for numeric values.
            max_chars: Maximum characters for string values.
            hash_bits: Number of bits to keep from hash (128, 192, 196, or 256).
            truncate: If True, truncate instead of round numeric values.
        """
        if version != 6:
            raise ValueError("Only UNF version 6 is supported")
        if hash_bits not in (128, 192, 196, 256):
            raise ValueError("hash_bits must be one of: 128, 192, 196, 256")

        self.version = version
        self.precision = precision
        self.max_chars = max_chars
        self.hash_bits = hash_bits
        self.truncate = truncate

    def get_header(self) -> str:
        """Get the UNF header string with parameters.

        Returns:
            Header string like "UNF:6:" or "UNF:6:N9,X256,H256:"
        """
        parts = [f"UNF:{self.version}"]

        # Add non-default parameters
        params = []
        if self.precision != 7:
            params.append(f"N{self.precision}")
        if self.max_chars != 128:
            params.append(f"X{self.max_chars}")
        if self.hash_bits != 128:
            params.append(f"H{self.hash_bits}")
        if self.truncate:
            params.append("R1")

        if params:
            parts.append(",".join(params))

        return ":".join(parts) + ":"


def normalize_value(
    value: Any,
    config: UNFConfig | None = None
) -> bytes:
    """Normalize a single value according to its type.

    Args:
        value: The value to normalize.
        config: UNF configuration (uses defaults if None).

    Returns:
        Normalized value as bytes.
    """
    if config is None:
        config = UNFConfig()

    # Handle None/missing values
    if value is None:
        return b'\000\000\000'

    # Numeric types
    if isinstance(value, (int, float)):
        normalized = normalize_numeric(
            value,
            precision=config.precision,
            round_mode=not config.truncate
        )
        return normalized.encode('utf-8')

    # String type
    if isinstance(value, str):
        return normalize_string(value, max_chars=config.max_chars)

    # Boolean type
    if isinstance(value, bool):
        normalized = normalize_boolean(value)
        return normalized.encode('utf-8')

    # Date/datetime types
    from datetime import date, datetime

    if isinstance(value, datetime):
        normalized = normalize_datetime(value)
        return normalized.encode('utf-8')

    if isinstance(value, date):
        normalized = normalize_date(value)
        return normalized.encode('utf-8')

    # Default: convert to string
    return str(value).encode('utf-8')


def calculate_unf(
    data: Sequence[Any],
    config: UNFConfig | None = None
) -> str:
    """Calculate the UNF fingerprint for a vector of data.

    Args:
        data: Sequence of values (a single variable/column).
        config: UNF configuration (uses defaults if None).

    Returns:
        UNF fingerprint string (e.g., "UNF:6:abc123...==").

    Examples:
        >>> calculate_unf([1.0, 2.0, 3.0])
        'UNF:6:...'
        >>> calculate_unf([1.0, None, 3.0])
        'UNF:6:...'

    Note:
        When using with pandas DataFrames, NaN values should be converted to None
        first for correct missing value handling. See calculate_unf_pandas() for
        a convenience function that handles this automatically.
    """
    if config is None:
        config = UNFConfig()

    # Convert NaN to None for proper missing value handling
    # This is necessary because pandas and other libraries use NaN (float('nan'))
    # for missing values, but UNF requires missing values to be encoded as None
    cleaned_data = []
    for value in data:
        # Check if value is NaN (works for numpy, pandas, and regular floats)
        if isinstance(value, float):
            import math
            if math.isnan(value):
                cleaned_data.append(None)
            else:
                cleaned_data.append(value)
        else:
            cleaned_data.append(value)

    # Normalize each element
    normalized_elements = []
    for value in cleaned_data:
        norm_value = normalize_value(value, config)

        # Non-missing values get terminated with newline + null byte
        if norm_value != b'\000\000\000':
            normalized_elements.append(norm_value + b'\n\000')
        else:
            normalized_elements.append(norm_value)

    # Concatenate all normalized strings
    concatenated = b''.join(normalized_elements)

    # Compute SHA256 hash
    hash_obj = hashlib.sha256(concatenated)
    hash_bytes = hash_obj.digest()

    # Truncate to specified number of bits
    num_bytes = config.hash_bits // 8
    truncated_hash = hash_bytes[:num_bytes]

    # Encode in base64
    b64_hash = base64.b64encode(truncated_hash).decode('ascii')

    # Return with header
    return config.get_header() + b64_hash


def combine_unfs(
    unfs: Sequence[str],
    config: UNFConfig | None = None
) -> str:
    """Combine multiple UNF fingerprints into a single UNF.

    This is used to create a fingerprint for a dataset from individual
    variable fingerprints. The UNFs are sorted before combining to ensure
    column order doesn't affect the result.

    Args:
        unfs: Sequence of UNF fingerprint strings.
        config: UNF configuration (uses defaults if None).

    Returns:
        Combined UNF fingerprint string.

    Examples:
        >>> unf1 = calculate_unf([1, 2, 3])
        >>> unf2 = calculate_unf([4, 5, 6])
        >>> combine_unfs([unf1, unf2])
        'UNF:6:...'
    """
    if config is None:
        config = UNFConfig()

    if not unfs:
        return config.get_header()

    # Sort UNFs in POSIX locale order (byte-wise sorting)
    sorted_unfs = sorted(unfs)

    # Treat the sorted UNFs as a vector and calculate UNF
    # Each UNF is treated as a string value
    normalized_elements = []
    for unf in sorted_unfs:
        # Encode as UTF-8, terminate with newline + null
        normalized_elements.append(unf.encode('utf-8') + b'\n\000')

    # Concatenate
    concatenated = b''.join(normalized_elements)

    # Compute SHA256 hash
    hash_obj = hashlib.sha256(concatenated)
    hash_bytes = hash_obj.digest()

    # Truncate to specified number of bits
    num_bytes = config.hash_bits // 8
    truncated_hash = hash_bytes[:num_bytes]

    # Encode in base64
    b64_hash = base64.b64encode(truncated_hash).decode('ascii')

    # Return with header
    return config.get_header() + b64_hash


def calculate_dataset_unf(
    data: Sequence[Sequence[Any]],
    config: UNFConfig | None = None
) -> str:
    """Calculate UNF for a complete dataset (multiple variables).

    This is a convenience function that calculates individual UNFs for each
    variable and then combines them.

    Args:
        data: Sequence of variables (columns), where each variable is a sequence of values.
        config: UNF configuration (uses defaults if None).

    Returns:
        Dataset-level UNF fingerprint string.

    Examples:
        >>> data = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]  # 3 variables
        >>> calculate_dataset_unf(data)
        'UNF:6:...'
    """
    if config is None:
        config = UNFConfig()

    # Calculate UNF for each variable
    variable_unfs = [calculate_unf(variable, config) for variable in data]

    # Combine them
    return combine_unfs(variable_unfs, config)


def calculate_unf_from_stata(
    filepath: str,
    config: UNFConfig | None = None
) -> dict[str, str]:
    """Calculate UNFs for all variables in a Stata file.

    This function reads a Stata (.dta) file and calculates UNF values that
    match R's haven/UNF implementation by:
    - Using numeric codes for labeled variables (not string labels)
    - Properly handling missing values (NaN -> None)

    Args:
        filepath: Path to the Stata (.dta) file.
        config: UNF configuration (uses defaults if None).

    Returns:
        Dictionary mapping variable names to their UNF fingerprints, plus a
        special '__dataset__' key for the dataset-level UNF.

    Examples:
        >>> unfs = calculate_unf_from_stata("data.dta")
        >>> print(unfs['variable_name'])
        'UNF:6:...'
        >>> print(unfs['__dataset__'])  # dataset-level UNF
        'UNF:6:...'

    Note:
        Requires the pyreadstat package to be installed:
            pip install pyreadstat
    """
    try:
        import pyreadstat
    except ImportError:
        raise ImportError(
            "pyreadstat is required for reading Stata files. "
            "Install it with: pip install pyreadstat"
        )

    if config is None:
        config = UNFConfig()

    # Read Stata file without converting value labels to strings
    # This matches R's haven behavior where labeled variables retain numeric codes
    df, meta = pyreadstat.read_dta(filepath, apply_value_formats=False)

    # Calculate UNF for each variable
    variable_unfs = {}
    for column in df.columns:
        # NaN values are automatically handled by calculate_unf
        variable_unfs[column] = calculate_unf(df[column].tolist(), config)

    # Calculate dataset-level UNF
    all_variable_data = [df[col].tolist() for col in df.columns]
    variable_unfs['__dataset__'] = calculate_dataset_unf(all_variable_data, config)

    return variable_unfs
