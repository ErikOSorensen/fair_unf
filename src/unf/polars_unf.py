"""Polars integration for UNF calculation.

This module provides convenience functions for calculating UNF fingerprints
directly from polars Series and DataFrame objects.

Polars has superior null handling compared to pandas - it uses out-of-band
encoding (separate validity bitmask) and properly distinguishes between
null (missing data) and NaN (undefined floating-point values). When you
call .to_list() on a polars Series, missing values are automatically
returned as Python None objects, which is exactly what the UNF specification
requires.

This means polars data can be used directly without any NaN → None conversion
"hack" needed for pandas data.
"""

from typing import TYPE_CHECKING

from .unf import calculate_unf, UNFConfig

if TYPE_CHECKING:
    import polars as pl


def series_unf(series: "pl.Series", config: UNFConfig | None = None) -> str:
    """Calculate UNF for a polars Series.

    Polars automatically handles missing values correctly by converting
    them to Python None objects when calling .to_list(), which matches
    the UNF specification requirements.

    Args:
        series: polars Series to calculate UNF for.
        config: Optional UNF configuration.

    Returns:
        UNF fingerprint string.

    Examples:
        >>> import polars as pl
        >>> from unf.polars_unf import series_unf
        >>> s = pl.Series([1, 2, 3, 4, 5])
        >>> unf = series_unf(s)
        >>> print(unf)
        'UNF:6:...'

        >>> # Missing values are handled correctly
        >>> s_with_nulls = pl.Series([1.0, 2.0, None, 4.0])
        >>> unf = series_unf(s_with_nulls)
        >>> print(unf)
        'UNF:6:...'

    Note:
        Polars distinguishes between null (missing) and NaN (undefined float).
        If your data contains explicit NaN values (not null), they will be
        preserved and encoded as NaN in the UNF calculation, which may not
        match other implementations that treat NaN as missing.
    """
    try:
        import polars as pl
    except ImportError:
        raise ImportError(
            "polars is required for polars_unf. "
            "Install it with: pip install unf[polars]"
        )

    if not isinstance(series, pl.Series):
        raise TypeError(f"Expected pl.Series, got {type(series)}")

    # Polars .to_list() automatically converts null to None
    # This is superior to pandas which uses NaN
    data = series.to_list()

    return calculate_unf(data, config)


def dataframe_unf(df: "pl.DataFrame", config: UNFConfig | None = None) -> str:
    """Calculate UNF for a polars DataFrame.

    The UNF is calculated by computing individual UNFs for each column
    and then combining them in a sort-based, order-independent manner.
    This means the column order doesn't affect the resulting UNF.

    Args:
        df: polars DataFrame to calculate UNF for.
        config: Optional UNF configuration.

    Returns:
        Dataset-level UNF fingerprint string.

    Examples:
        >>> import polars as pl
        >>> from unf.polars_unf import dataframe_unf
        >>> df = pl.DataFrame({
        ...     'id': [1, 2, 3],
        ...     'name': ['Alice', 'Bob', 'Charlie'],
        ...     'score': [85.5, 90.0, 88.5]
        ... })
        >>> unf = dataframe_unf(df)
        >>> print(unf)
        'UNF:6:...'

        >>> # With missing values
        >>> df_with_nulls = pl.DataFrame({
        ...     'id': [1, 2, 3],
        ...     'value': [1.5, None, 3.5]
        ... })
        >>> unf = dataframe_unf(df_with_nulls)
        >>> print(unf)
        'UNF:6:...'
    """
    try:
        import polars as pl
    except ImportError:
        raise ImportError(
            "polars is required for polars_unf. "
            "Install it with: pip install unf[polars]"
        )

    if not isinstance(df, pl.DataFrame):
        raise TypeError(f"Expected pl.DataFrame, got {type(df)}")

    if df.is_empty():
        from .unf import combine_unfs
        return combine_unfs([], config)

    # Calculate UNF for each column
    column_unfs = []
    for column in df.columns:
        series = df[column]
        unf = series_unf(series, config)
        column_unfs.append(unf)

    # Combine column UNFs
    from .unf import combine_unfs
    return combine_unfs(column_unfs, config)


def dataframe_column_unfs(
    df: "pl.DataFrame",
    config: UNFConfig | None = None
) -> dict[str, str]:
    """Calculate individual UNFs for each column in a DataFrame.

    Returns a dictionary mapping column names to their UNF fingerprints.

    Args:
        df: polars DataFrame to calculate column UNFs for.
        config: Optional UNF configuration.

    Returns:
        Dictionary mapping column names to UNF strings.

    Examples:
        >>> import polars as pl
        >>> from unf.polars_unf import dataframe_column_unfs
        >>> df = pl.DataFrame({
        ...     'id': [1, 2, 3],
        ...     'name': ['Alice', 'Bob', 'Charlie']
        ... })
        >>> unfs = dataframe_column_unfs(df)
        >>> print(unfs)
        {'id': 'UNF:6:...', 'name': 'UNF:6:...'}
    """
    try:
        import polars as pl
    except ImportError:
        raise ImportError(
            "polars is required for polars_unf. "
            "Install it with: pip install unf[polars]"
        )

    if not isinstance(df, pl.DataFrame):
        raise TypeError(f"Expected pl.DataFrame, got {type(df)}")

    return {
        str(column): series_unf(df[column], config)
        for column in df.columns
    }
