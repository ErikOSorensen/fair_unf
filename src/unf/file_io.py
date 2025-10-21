"""File I/O support for UNF calculation.

This module provides functions to calculate UNF fingerprints directly from
various file formats supported by pandas, including CSV, Parquet, Stata, SAS,
SPSS, Excel, and more.
"""

from pathlib import Path
from typing import TYPE_CHECKING, Any

from .unf import UNFConfig

if TYPE_CHECKING:
    import pandas as pd


# Format detection mapping
FORMAT_EXTENSIONS = {
    '.csv': 'csv',
    '.tsv': 'csv',
    '.txt': 'csv',
    '.parquet': 'parquet',
    '.pq': 'parquet',
    '.feather': 'feather',
    '.dta': 'stata',
    '.sas7bdat': 'sas',
    '.xpt': 'sas',
    '.sav': 'spss',
    '.xlsx': 'excel',
    '.xls': 'excel',
    '.json': 'json',
    '.h5': 'hdf',
    '.hdf': 'hdf',
}


def _ensure_pandas():
    """Ensure pandas is available."""
    try:
        import pandas as pd
        return pd
    except ImportError:
        raise ImportError(
            "pandas is required for file I/O. "
            "Install it with: pip install unf[pandas]"
        )


def csv_unf(
    filepath: str | Path,
    config: UNFConfig | None = None,
    return_metadata: bool = False,
    **kwargs: Any
) -> str | dict[str, Any]:
    """Calculate UNF for a CSV file.

    Args:
        filepath: Path to CSV file.
        config: Optional UNF configuration.
        return_metadata: If True, return dict with UNF and file metadata.
        **kwargs: Additional arguments passed to pd.read_csv().

    Returns:
        UNF string, or dict with UNF and metadata if return_metadata=True.

    Examples:
        >>> from unf.file_io import csv_unf
        >>> unf = csv_unf("data.csv")
        >>> unf = csv_unf("data.tsv", sep="\\t")
    """
    pd = _ensure_pandas()
    from .pandas_unf import dataframe_unf

    df = pd.read_csv(filepath, **kwargs)
    unf = dataframe_unf(df, config)

    if return_metadata:
        return {
            'unf': unf,
            'format': 'csv',
            'shape': df.shape,
            'columns': list(df.columns),
            'filepath': str(filepath)
        }
    return unf


def parquet_unf(
    filepath: str | Path,
    config: UNFConfig | None = None,
    return_metadata: bool = False,
    **kwargs: Any
) -> str | dict[str, Any]:
    """Calculate UNF for a Parquet file.

    Args:
        filepath: Path to Parquet file.
        config: Optional UNF configuration.
        return_metadata: If True, return dict with UNF and file metadata.
        **kwargs: Additional arguments passed to pd.read_parquet().

    Returns:
        UNF string, or dict with UNF and metadata if return_metadata=True.

    Examples:
        >>> from unf.file_io import parquet_unf
        >>> unf = parquet_unf("data.parquet")
    """
    pd = _ensure_pandas()
    from .pandas_unf import dataframe_unf

    try:
        df = pd.read_parquet(filepath, **kwargs)
    except ImportError as e:
        raise ImportError(
            "pyarrow or fastparquet is required to read Parquet files. "
            "Install with: pip install pyarrow"
        ) from e

    unf = dataframe_unf(df, config)

    if return_metadata:
        return {
            'unf': unf,
            'format': 'parquet',
            'shape': df.shape,
            'columns': list(df.columns),
            'filepath': str(filepath)
        }
    return unf


def feather_unf(
    filepath: str | Path,
    config: UNFConfig | None = None,
    return_metadata: bool = False,
    **kwargs: Any
) -> str | dict[str, Any]:
    """Calculate UNF for a Feather file.

    Args:
        filepath: Path to Feather file.
        config: Optional UNF configuration.
        return_metadata: If True, return dict with UNF and file metadata.
        **kwargs: Additional arguments passed to pd.read_feather().

    Returns:
        UNF string, or dict with UNF and metadata if return_metadata=True.

    Examples:
        >>> from unf.file_io import feather_unf
        >>> unf = feather_unf("data.feather")
    """
    pd = _ensure_pandas()
    from .pandas_unf import dataframe_unf

    try:
        df = pd.read_feather(filepath, **kwargs)
    except ImportError as e:
        raise ImportError(
            "pyarrow is required to read Feather files. "
            "Install with: pip install pyarrow"
        ) from e

    unf = dataframe_unf(df, config)

    if return_metadata:
        return {
            'unf': unf,
            'format': 'feather',
            'shape': df.shape,
            'columns': list(df.columns),
            'filepath': str(filepath)
        }
    return unf


def stata_unf(
    filepath: str | Path,
    config: UNFConfig | None = None,
    return_metadata: bool = False,
    **kwargs: Any
) -> str | dict[str, Any]:
    """Calculate UNF for a Stata .dta file.

    Args:
        filepath: Path to Stata file.
        config: Optional UNF configuration.
        return_metadata: If True, return dict with UNF and file metadata.
        **kwargs: Additional arguments passed to pd.read_stata().

    Returns:
        UNF string, or dict with UNF and metadata if return_metadata=True.

    Examples:
        >>> from unf.file_io import stata_unf
        >>> unf = stata_unf("data.dta")
    """
    pd = _ensure_pandas()
    from .pandas_unf import dataframe_unf

    df = pd.read_stata(filepath, **kwargs)
    unf = dataframe_unf(df, config)

    if return_metadata:
        return {
            'unf': unf,
            'format': 'stata',
            'shape': df.shape,
            'columns': list(df.columns),
            'filepath': str(filepath)
        }
    return unf


def sas_unf(
    filepath: str | Path,
    config: UNFConfig | None = None,
    return_metadata: bool = False,
    **kwargs: Any
) -> str | dict[str, Any]:
    """Calculate UNF for a SAS file (.sas7bdat or .xpt).

    Args:
        filepath: Path to SAS file.
        config: Optional UNF configuration.
        return_metadata: If True, return dict with UNF and file metadata.
        **kwargs: Additional arguments passed to pd.read_sas().

    Returns:
        UNF string, or dict with UNF and metadata if return_metadata=True.

    Examples:
        >>> from unf.file_io import sas_unf
        >>> unf = sas_unf("data.sas7bdat")
    """
    pd = _ensure_pandas()
    from .pandas_unf import dataframe_unf

    df = pd.read_sas(filepath, **kwargs)
    unf = dataframe_unf(df, config)

    if return_metadata:
        return {
            'unf': unf,
            'format': 'sas',
            'shape': df.shape,
            'columns': list(df.columns),
            'filepath': str(filepath)
        }
    return unf


def spss_unf(
    filepath: str | Path,
    config: UNFConfig | None = None,
    return_metadata: bool = False,
    **kwargs: Any
) -> str | dict[str, Any]:
    """Calculate UNF for an SPSS .sav file.

    Args:
        filepath: Path to SPSS file.
        config: Optional UNF configuration.
        return_metadata: If True, return dict with UNF and file metadata.
        **kwargs: Additional arguments passed to pd.read_spss().

    Returns:
        UNF string, or dict with UNF and metadata if return_metadata=True.

    Examples:
        >>> from unf.file_io import spss_unf
        >>> unf = spss_unf("data.sav")
    """
    pd = _ensure_pandas()
    from .pandas_unf import dataframe_unf

    try:
        df = pd.read_spss(filepath, **kwargs)
    except ImportError as e:
        raise ImportError(
            "pyreadstat is required to read SPSS files. "
            "Install with: pip install pyreadstat"
        ) from e

    unf = dataframe_unf(df, config)

    if return_metadata:
        return {
            'unf': unf,
            'format': 'spss',
            'shape': df.shape,
            'columns': list(df.columns),
            'filepath': str(filepath)
        }
    return unf


def excel_unf(
    filepath: str | Path,
    config: UNFConfig | None = None,
    return_metadata: bool = False,
    sheet_name: str | int = 0,
    **kwargs: Any
) -> str | dict[str, Any]:
    """Calculate UNF for an Excel file (.xlsx or .xls).

    Args:
        filepath: Path to Excel file.
        config: Optional UNF configuration.
        return_metadata: If True, return dict with UNF and file metadata.
        sheet_name: Sheet name or index (default: 0, first sheet).
        **kwargs: Additional arguments passed to pd.read_excel().

    Returns:
        UNF string, or dict with UNF and metadata if return_metadata=True.

    Examples:
        >>> from unf.file_io import excel_unf
        >>> unf = excel_unf("data.xlsx")
        >>> unf = excel_unf("data.xlsx", sheet_name="Sheet2")
    """
    pd = _ensure_pandas()
    from .pandas_unf import dataframe_unf

    try:
        df = pd.read_excel(filepath, sheet_name=sheet_name, **kwargs)
    except ImportError as e:
        raise ImportError(
            "openpyxl is required to read Excel files. "
            "Install with: pip install openpyxl"
        ) from e

    unf = dataframe_unf(df, config)

    if return_metadata:
        return {
            'unf': unf,
            'format': 'excel',
            'shape': df.shape,
            'columns': list(df.columns),
            'sheet_name': sheet_name,
            'filepath': str(filepath)
        }
    return unf


def json_unf(
    filepath: str | Path,
    config: UNFConfig | None = None,
    return_metadata: bool = False,
    **kwargs: Any
) -> str | dict[str, Any]:
    """Calculate UNF for a JSON file.

    Args:
        filepath: Path to JSON file.
        config: Optional UNF configuration.
        return_metadata: If True, return dict with UNF and file metadata.
        **kwargs: Additional arguments passed to pd.read_json().

    Returns:
        UNF string, or dict with UNF and metadata if return_metadata=True.

    Examples:
        >>> from unf.file_io import json_unf
        >>> unf = json_unf("data.json")
    """
    pd = _ensure_pandas()
    from .pandas_unf import dataframe_unf

    df = pd.read_json(filepath, **kwargs)
    unf = dataframe_unf(df, config)

    if return_metadata:
        return {
            'unf': unf,
            'format': 'json',
            'shape': df.shape,
            'columns': list(df.columns),
            'filepath': str(filepath)
        }
    return unf


def file_unf(
    filepath: str | Path,
    format: str | None = None,
    config: UNFConfig | None = None,
    return_metadata: bool = False,
    **kwargs: Any
) -> str | dict[str, Any]:
    """Calculate UNF from any supported file format.

    Automatically detects format from file extension if not specified.

    Supported formats:
    - CSV (.csv, .tsv, .txt)
    - Parquet (.parquet, .pq)
    - Feather (.feather)
    - Stata (.dta)
    - SAS (.sas7bdat, .xpt)
    - SPSS (.sav)
    - Excel (.xlsx, .xls)
    - JSON (.json)

    Args:
        filepath: Path to file.
        format: File format. Auto-detected from extension if None.
        config: Optional UNF configuration.
        return_metadata: If True, return dict with UNF and file metadata.
        **kwargs: Additional arguments passed to the format-specific pandas reader.

    Returns:
        UNF string, or dict with UNF and metadata if return_metadata=True.

    Raises:
        ValueError: If format cannot be detected or is unsupported.

    Examples:
        >>> from unf import file_unf
        >>> # Auto-detect format
        >>> unf = file_unf("data.csv")
        >>> unf = file_unf("data.parquet")
        >>> unf = file_unf("data.dta")
        >>>
        >>> # Explicit format with custom options
        >>> unf = file_unf("data.txt", format="csv", sep="\\t")
        >>>
        >>> # Get metadata
        >>> result = file_unf("data.csv", return_metadata=True)
        >>> print(result['unf'])
        >>> print(result['shape'])
    """
    path = Path(filepath)

    # Detect format from extension if not provided
    if format is None:
        suffix = path.suffix.lower()
        format = FORMAT_EXTENSIONS.get(suffix)
        if format is None:
            raise ValueError(
                f"Cannot detect format from extension '{suffix}'. "
                f"Supported extensions: {', '.join(FORMAT_EXTENSIONS.keys())}. "
                f"Specify format explicitly using format parameter."
            )

    # Dispatch to format-specific function
    format_lower = format.lower()
    if format_lower == 'csv':
        return csv_unf(filepath, config, return_metadata, **kwargs)
    elif format_lower == 'parquet':
        return parquet_unf(filepath, config, return_metadata, **kwargs)
    elif format_lower == 'feather':
        return feather_unf(filepath, config, return_metadata, **kwargs)
    elif format_lower == 'stata':
        return stata_unf(filepath, config, return_metadata, **kwargs)
    elif format_lower == 'sas':
        return sas_unf(filepath, config, return_metadata, **kwargs)
    elif format_lower == 'spss':
        return spss_unf(filepath, config, return_metadata, **kwargs)
    elif format_lower == 'excel':
        return excel_unf(filepath, config, return_metadata, **kwargs)
    elif format_lower == 'json':
        return json_unf(filepath, config, return_metadata, **kwargs)
    else:
        raise ValueError(
            f"Unsupported format: '{format}'. "
            f"Supported formats: csv, parquet, feather, stata, sas, spss, excel, json"
        )
