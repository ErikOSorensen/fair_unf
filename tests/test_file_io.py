"""Tests for file I/O functionality."""

import pytest
from pathlib import Path
import tempfile
import os

# Check if pandas is available
try:
    import pandas as pd
    import numpy as np
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not PANDAS_AVAILABLE,
    reason="pandas not installed"
)

if PANDAS_AVAILABLE:
    from unf.file_io import (
        file_unf,
        csv_unf,
        parquet_unf,
        stata_unf,
        json_unf,
        excel_unf,
    )
    from unf import dataframe_unf


@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing."""
    return pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
        'age': [25, 30, 35, 28, 32],
        'score': [85.5, 90.0, 88.5, 92.0, 87.5]
    })


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


class TestCSVUnf:
    """Tests for CSV file UNF calculation."""

    def test_csv_basic(self, sample_dataframe, temp_dir):
        """Test basic CSV UNF calculation."""
        csv_path = temp_dir / "test.csv"
        sample_dataframe.to_csv(csv_path, index=False)

        unf = csv_unf(csv_path)
        assert unf.startswith("UNF:6:")

        # Should match DataFrame UNF
        df_unf = dataframe_unf(sample_dataframe)
        assert unf == df_unf

    def test_csv_with_options(self, sample_dataframe, temp_dir):
        """Test CSV with custom separator."""
        tsv_path = temp_dir / "test.tsv"
        sample_dataframe.to_csv(tsv_path, index=False, sep="\t")

        unf = csv_unf(tsv_path, sep="\t")
        assert unf.startswith("UNF:6:")

    def test_csv_with_metadata(self, sample_dataframe, temp_dir):
        """Test CSV UNF with metadata."""
        csv_path = temp_dir / "test.csv"
        sample_dataframe.to_csv(csv_path, index=False)

        result = csv_unf(csv_path, return_metadata=True)
        assert isinstance(result, dict)
        assert 'unf' in result
        assert 'format' in result
        assert 'shape' in result
        assert 'columns' in result
        assert result['format'] == 'csv'
        assert result['shape'] == (5, 4)


class TestParquetUnf:
    """Tests for Parquet file UNF calculation."""

    def test_parquet_basic(self, sample_dataframe, temp_dir):
        """Test basic Parquet UNF calculation."""
        try:
            import pyarrow
        except ImportError:
            pytest.skip("pyarrow not installed")

        parquet_path = temp_dir / "test.parquet"
        sample_dataframe.to_parquet(parquet_path, index=False)

        unf = parquet_unf(parquet_path)
        assert unf.startswith("UNF:6:")

        # Should match DataFrame UNF
        df_unf = dataframe_unf(sample_dataframe)
        assert unf == df_unf

    def test_parquet_with_metadata(self, sample_dataframe, temp_dir):
        """Test Parquet UNF with metadata."""
        try:
            import pyarrow
        except ImportError:
            pytest.skip("pyarrow not installed")

        parquet_path = temp_dir / "test.parquet"
        sample_dataframe.to_parquet(parquet_path, index=False)

        result = parquet_unf(parquet_path, return_metadata=True)
        assert isinstance(result, dict)
        assert result['format'] == 'parquet'
        assert result['shape'] == (5, 4)


class TestStataUnf:
    """Tests for Stata file UNF calculation."""

    def test_stata_basic(self, sample_dataframe, temp_dir):
        """Test basic Stata UNF calculation."""
        dta_path = temp_dir / "test.dta"
        sample_dataframe.to_stata(dta_path, write_index=False)

        unf = stata_unf(dta_path)
        assert unf.startswith("UNF:6:")

    def test_stata_with_metadata(self, sample_dataframe, temp_dir):
        """Test Stata UNF with metadata."""
        dta_path = temp_dir / "test.dta"
        sample_dataframe.to_stata(dta_path, write_index=False)

        result = stata_unf(dta_path, return_metadata=True)
        assert isinstance(result, dict)
        assert result['format'] == 'stata'
        assert result['shape'] == (5, 4)


class TestJSONUnf:
    """Tests for JSON file UNF calculation."""

    def test_json_basic(self, sample_dataframe, temp_dir):
        """Test basic JSON UNF calculation."""
        json_path = temp_dir / "test.json"
        sample_dataframe.to_json(json_path, orient='records')

        unf = json_unf(json_path)
        assert unf.startswith("UNF:6:")

    def test_json_with_metadata(self, sample_dataframe, temp_dir):
        """Test JSON UNF with metadata."""
        json_path = temp_dir / "test.json"
        sample_dataframe.to_json(json_path, orient='records')

        result = json_unf(json_path, return_metadata=True)
        assert isinstance(result, dict)
        assert result['format'] == 'json'


class TestExcelUnf:
    """Tests for Excel file UNF calculation."""

    def test_excel_basic(self, sample_dataframe, temp_dir):
        """Test basic Excel UNF calculation."""
        try:
            import openpyxl
        except ImportError:
            pytest.skip("openpyxl not installed")

        excel_path = temp_dir / "test.xlsx"
        sample_dataframe.to_excel(excel_path, index=False)

        unf = excel_unf(excel_path)
        assert unf.startswith("UNF:6:")

    def test_excel_with_metadata(self, sample_dataframe, temp_dir):
        """Test Excel UNF with metadata."""
        try:
            import openpyxl
        except ImportError:
            pytest.skip("openpyxl not installed")

        excel_path = temp_dir / "test.xlsx"
        sample_dataframe.to_excel(excel_path, index=False)

        result = excel_unf(excel_path, return_metadata=True)
        assert isinstance(result, dict)
        assert result['format'] == 'excel'
        assert result['shape'] == (5, 4)


class TestFileUnfAutoDetect:
    """Tests for auto-detecting file format."""

    def test_autodetect_csv(self, sample_dataframe, temp_dir):
        """Test auto-detection for CSV."""
        csv_path = temp_dir / "test.csv"
        sample_dataframe.to_csv(csv_path, index=False)

        unf = file_unf(csv_path)
        assert unf.startswith("UNF:6:")

    def test_autodetect_tsv(self, sample_dataframe, temp_dir):
        """Test auto-detection for TSV."""
        tsv_path = temp_dir / "test.tsv"
        sample_dataframe.to_csv(tsv_path, index=False, sep="\t")

        unf = file_unf(tsv_path, sep="\t")
        assert unf.startswith("UNF:6:")

    def test_autodetect_parquet(self, sample_dataframe, temp_dir):
        """Test auto-detection for Parquet."""
        try:
            import pyarrow
        except ImportError:
            pytest.skip("pyarrow not installed")

        parquet_path = temp_dir / "test.parquet"
        sample_dataframe.to_parquet(parquet_path, index=False)

        unf = file_unf(parquet_path)
        assert unf.startswith("UNF:6:")

    def test_autodetect_stata(self, sample_dataframe, temp_dir):
        """Test auto-detection for Stata."""
        dta_path = temp_dir / "test.dta"
        sample_dataframe.to_stata(dta_path, write_index=False)

        unf = file_unf(dta_path)
        assert unf.startswith("UNF:6:")

    def test_autodetect_json(self, sample_dataframe, temp_dir):
        """Test auto-detection for JSON."""
        json_path = temp_dir / "test.json"
        sample_dataframe.to_json(json_path, orient='records')

        unf = file_unf(json_path)
        assert unf.startswith("UNF:6:")

    def test_autodetect_excel(self, sample_dataframe, temp_dir):
        """Test auto-detection for Excel."""
        try:
            import openpyxl
        except ImportError:
            pytest.skip("openpyxl not installed")

        excel_path = temp_dir / "test.xlsx"
        sample_dataframe.to_excel(excel_path, index=False)

        unf = file_unf(excel_path)
        assert unf.startswith("UNF:6:")

    def test_explicit_format(self, sample_dataframe, temp_dir):
        """Test explicit format specification."""
        # Save as .txt but read as CSV
        txt_path = temp_dir / "test.txt"
        sample_dataframe.to_csv(txt_path, index=False)

        unf = file_unf(txt_path, format="csv")
        assert unf.startswith("UNF:6:")

    def test_unknown_extension(self, temp_dir):
        """Test handling of unknown extension."""
        unknown_path = temp_dir / "test.unknown"
        unknown_path.touch()

        with pytest.raises(ValueError, match="Cannot detect format"):
            file_unf(unknown_path)

    def test_unsupported_format(self, temp_dir):
        """Test handling of unsupported format."""
        csv_path = temp_dir / "test.csv"
        csv_path.touch()

        with pytest.raises(ValueError, match="Unsupported format"):
            file_unf(csv_path, format="unsupported")


class TestFormatConsistency:
    """Test that UNF is consistent across formats."""

    def test_csv_parquet_consistency(self, sample_dataframe, temp_dir):
        """Test that CSV and Parquet produce same UNF."""
        try:
            import pyarrow
        except ImportError:
            pytest.skip("pyarrow not installed")

        csv_path = temp_dir / "test.csv"
        parquet_path = temp_dir / "test.parquet"

        sample_dataframe.to_csv(csv_path, index=False)
        sample_dataframe.to_parquet(parquet_path, index=False)

        csv_unf_val = file_unf(csv_path)
        parquet_unf_val = file_unf(parquet_path)

        assert csv_unf_val == parquet_unf_val

    def test_csv_stata_consistency(self, sample_dataframe, temp_dir):
        """Test that CSV and Stata produce same UNF."""
        csv_path = temp_dir / "test.csv"
        dta_path = temp_dir / "test.dta"

        sample_dataframe.to_csv(csv_path, index=False)
        sample_dataframe.to_stata(dta_path, write_index=False)

        csv_unf_val = file_unf(csv_path)
        stata_unf_val = file_unf(dta_path)

        assert csv_unf_val == stata_unf_val

    def test_csv_excel_consistency(self, sample_dataframe, temp_dir):
        """Test that CSV and Excel produce same UNF."""
        try:
            import openpyxl
        except ImportError:
            pytest.skip("openpyxl not installed")

        csv_path = temp_dir / "test.csv"
        excel_path = temp_dir / "test.xlsx"

        sample_dataframe.to_csv(csv_path, index=False)
        sample_dataframe.to_excel(excel_path, index=False)

        csv_unf_val = file_unf(csv_path)
        excel_unf_val = file_unf(excel_path)

        assert csv_unf_val == excel_unf_val


class TestMetadata:
    """Tests for metadata functionality."""

    def test_metadata_structure(self, sample_dataframe, temp_dir):
        """Test metadata structure."""
        csv_path = temp_dir / "test.csv"
        sample_dataframe.to_csv(csv_path, index=False)

        result = file_unf(csv_path, return_metadata=True)

        assert isinstance(result, dict)
        assert 'unf' in result
        assert 'format' in result
        assert 'shape' in result
        assert 'columns' in result
        assert 'filepath' in result

        assert result['unf'].startswith("UNF:6:")
        assert result['format'] == 'csv'
        assert result['shape'] == (5, 4)
        assert len(result['columns']) == 4
        assert 'id' in result['columns']
