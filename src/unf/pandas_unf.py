"""Pandas integration for UNF calculation.

This module provides convenience functions for calculating UNF fingerprints
directly from pandas Series and DataFrame objects.
"""

from typing import TYPE_CHECKING

from .unf import calculate_unf, UNFConfig

if TYPE_CHECKING:
    import pandas as pd


def series_unf(series: "pd.Series", config: UNFConfig | None = None) -> str:
    """Calculate UNF for a pandas Series.

    Args:
        series: pandas Series to calculate UNF for.
        config: Optional UNF configuration.

    Returns:
        UNF fingerprint string.

    Examples:
        >>> import pandas as pd
        >>> from unf.pandas_unf import series_unf
        >>> s = pd.Series([1, 2, 3, 4, 5])
        >>> unf = series_unf(s)
        >>> print(unf)
        'UNF:6:...'
    """
    try:
        import pandas as pd
    except ImportError:
        raise ImportError(
            "pandas is required for pandas_unf. "
            "Install it with: pip install unf[pandas]"
        )

    if not isinstance(series, pd.Series):
        raise TypeError(f"Expected pd.Series, got {type(series)}")

    # Convert Series to list, replacing pd.NA/pd.NaT with None
    data = [None if pd.isna(x) else x for x in series]

    return calculate_unf(data, config)


def dataframe_unf(df: "pd.DataFrame", config: UNFConfig | None = None) -> str:
    """Calculate UNF for a pandas DataFrame.

    The UNF is calculated by computing individual UNFs for each column
    and then combining them in a sort-based, order-independent manner.
    This means the column order doesn't affect the resulting UNF.

    Args:
        df: pandas DataFrame to calculate UNF for.
        config: Optional UNF configuration.

    Returns:
        Dataset-level UNF fingerprint string.

    Examples:
        >>> import pandas as pd
        >>> from unf.pandas_unf import dataframe_unf
        >>> df = pd.DataFrame({
        ...     'id': [1, 2, 3],
        ...     'name': ['Alice', 'Bob', 'Charlie'],
        ...     'score': [85.5, 90.0, 88.5]
        ... })
        >>> unf = dataframe_unf(df)
        >>> print(unf)
        'UNF:6:...'
    """
    try:
        import pandas as pd
    except ImportError:
        raise ImportError(
            "pandas is required for pandas_unf. "
            "Install it with: pip install unf[pandas]"
        )

    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected pd.DataFrame, got {type(df)}")

    if df.empty:
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
    df: "pd.DataFrame",
    config: UNFConfig | None = None
) -> dict[str, str]:
    """Calculate individual UNFs for each column in a DataFrame.

    Returns a dictionary mapping column names to their UNF fingerprints.

    Args:
        df: pandas DataFrame to calculate column UNFs for.
        config: Optional UNF configuration.

    Returns:
        Dictionary mapping column names to UNF strings.

    Examples:
        >>> import pandas as pd
        >>> from unf.pandas_unf import dataframe_column_unfs
        >>> df = pd.DataFrame({
        ...     'id': [1, 2, 3],
        ...     'name': ['Alice', 'Bob', 'Charlie']
        ... })
        >>> unfs = dataframe_column_unfs(df)
        >>> print(unfs)
        {'id': 'UNF:6:...', 'name': 'UNF:6:...'}
    """
    try:
        import pandas as pd
    except ImportError:
        raise ImportError(
            "pandas is required for pandas_unf. "
            "Install it with: pip install unf[pandas]"
        )

    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected pd.DataFrame, got {type(df)}")

    return {
        str(column): series_unf(df[column], config)
        for column in df.columns
    }
