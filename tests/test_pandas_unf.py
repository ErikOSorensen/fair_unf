"""Tests for pandas integration."""

import pytest

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
    from unf import series_unf, dataframe_unf, dataframe_column_unfs, calculate_unf
    from unf.unf import UNFConfig


class TestSeriesUNF:
    """Tests for series_unf function."""

    def test_numeric_series(self):
        """Test UNF calculation for numeric series."""
        s = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
        unf = series_unf(s)
        assert unf.startswith("UNF:6:")

        # Should match the same UNF as a list
        list_unf = calculate_unf([1.0, 2.0, 3.0, 4.0, 5.0])
        assert unf == list_unf

    def test_string_series(self):
        """Test UNF calculation for string series."""
        s = pd.Series(["Alice", "Bob", "Charlie"])
        unf = series_unf(s)
        assert unf.startswith("UNF:6:")

        # Should match the same UNF as a list
        list_unf = calculate_unf(["Alice", "Bob", "Charlie"])
        assert unf == list_unf

    def test_integer_series(self):
        """Test UNF calculation for integer series."""
        s = pd.Series([1, 2, 3, 4, 5])
        unf = series_unf(s)
        assert unf.startswith("UNF:6:")

    def test_boolean_series(self):
        """Test UNF calculation for boolean series."""
        s = pd.Series([True, False, True, False])
        unf = series_unf(s)
        assert unf.startswith("UNF:6:")

    def test_series_with_na(self):
        """Test UNF calculation for series with missing values."""
        s = pd.Series([1.0, None, 3.0, pd.NA, 5.0])
        unf = series_unf(s)
        assert unf.startswith("UNF:6:")

        # Should match list with None values
        list_unf = calculate_unf([1.0, None, 3.0, None, 5.0])
        assert unf == list_unf

    def test_series_with_nat(self):
        """Test UNF calculation for series with NaT (not-a-time)."""
        s = pd.Series([pd.Timestamp('2024-01-01'), pd.NaT, pd.Timestamp('2024-01-03')])
        unf = series_unf(s)
        assert unf.startswith("UNF:6:")

    def test_series_with_custom_config(self):
        """Test UNF calculation with custom configuration."""
        s = pd.Series([3.14159, 2.71828])
        config = UNFConfig(precision=9)
        unf = series_unf(s, config)
        assert unf.startswith("UNF:6:N9:")

    def test_empty_series(self):
        """Test UNF calculation for empty series."""
        s = pd.Series([], dtype=float)
        unf = series_unf(s)
        assert unf.startswith("UNF:6:")

    def test_series_deterministic(self):
        """Test that UNF is deterministic for the same series."""
        s = pd.Series([1, 2, 3, 4, 5])
        unf1 = series_unf(s)
        unf2 = series_unf(s)
        assert unf1 == unf2

    def test_invalid_input(self):
        """Test that non-Series input raises TypeError."""
        with pytest.raises(TypeError):
            series_unf([1, 2, 3])


class TestDataFrameUNF:
    """Tests for dataframe_unf function."""

    def test_simple_dataframe(self):
        """Test UNF calculation for simple DataFrame."""
        df = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'score': [85.5, 90.0, 88.5]
        })
        unf = dataframe_unf(df)
        assert unf.startswith("UNF:6:")

    def test_numeric_dataframe(self):
        """Test UNF calculation for numeric DataFrame."""
        df = pd.DataFrame({
            'col1': [1.0, 2.0, 3.0],
            'col2': [4.0, 5.0, 6.0],
            'col3': [7.0, 8.0, 9.0]
        })
        unf = dataframe_unf(df)
        assert unf.startswith("UNF:6:")

    def test_dataframe_order_independence(self):
        """Test that column order doesn't affect UNF."""
        df1 = pd.DataFrame({
            'a': [1, 2, 3],
            'b': [4, 5, 6],
            'c': [7, 8, 9]
        })
        df2 = pd.DataFrame({
            'c': [7, 8, 9],
            'a': [1, 2, 3],
            'b': [4, 5, 6]
        })
        df3 = pd.DataFrame({
            'b': [4, 5, 6],
            'c': [7, 8, 9],
            'a': [1, 2, 3]
        })

        unf1 = dataframe_unf(df1)
        unf2 = dataframe_unf(df2)
        unf3 = dataframe_unf(df3)

        assert unf1 == unf2 == unf3

    def test_dataframe_with_missing(self):
        """Test UNF calculation for DataFrame with missing values."""
        df = pd.DataFrame({
            'a': [1.0, None, 3.0],
            'b': [4.0, 5.0, pd.NA],
            'c': ['x', 'y', None]
        })
        unf = dataframe_unf(df)
        assert unf.startswith("UNF:6:")

    def test_empty_dataframe(self):
        """Test UNF calculation for empty DataFrame."""
        df = pd.DataFrame()
        unf = dataframe_unf(df)
        assert unf == "UNF:6:"

    def test_dataframe_with_custom_config(self):
        """Test UNF calculation with custom configuration."""
        df = pd.DataFrame({
            'a': [3.14159, 2.71828],
            'b': [1.41421, 1.73205]
        })
        config = UNFConfig(precision=9)
        unf = dataframe_unf(df, config)
        assert unf.startswith("UNF:6:N9:")

    def test_dataframe_deterministic(self):
        """Test that UNF is deterministic for the same DataFrame."""
        df = pd.DataFrame({
            'a': [1, 2, 3],
            'b': [4, 5, 6]
        })
        unf1 = dataframe_unf(df)
        unf2 = dataframe_unf(df)
        assert unf1 == unf2

    def test_dataframe_mixed_types(self):
        """Test UNF for DataFrame with mixed column types."""
        df = pd.DataFrame({
            'int_col': [1, 2, 3],
            'float_col': [1.5, 2.5, 3.5],
            'str_col': ['a', 'b', 'c'],
            'bool_col': [True, False, True]
        })
        unf = dataframe_unf(df)
        assert unf.startswith("UNF:6:")

    def test_invalid_input(self):
        """Test that non-DataFrame input raises TypeError."""
        with pytest.raises(TypeError):
            dataframe_unf([[1, 2], [3, 4]])


class TestDataFrameColumnUNFs:
    """Tests for dataframe_column_unfs function."""

    def test_column_unfs(self):
        """Test getting individual column UNFs."""
        df = pd.DataFrame({
            'a': [1, 2, 3],
            'b': [4, 5, 6],
            'c': [7, 8, 9]
        })
        unfs = dataframe_column_unfs(df)

        assert isinstance(unfs, dict)
        assert len(unfs) == 3
        assert 'a' in unfs
        assert 'b' in unfs
        assert 'c' in unfs

        for col_unf in unfs.values():
            assert col_unf.startswith("UNF:6:")

    def test_column_unfs_match_series(self):
        """Test that column UNFs match individual series UNFs."""
        df = pd.DataFrame({
            'a': [1, 2, 3],
            'b': [4, 5, 6]
        })
        unfs = dataframe_column_unfs(df)

        # Should match individual series UNFs
        assert unfs['a'] == series_unf(df['a'])
        assert unfs['b'] == series_unf(df['b'])

    def test_column_unfs_with_custom_config(self):
        """Test column UNFs with custom configuration."""
        df = pd.DataFrame({
            'a': [3.14159, 2.71828]
        })
        config = UNFConfig(precision=9)
        unfs = dataframe_column_unfs(df, config)

        assert unfs['a'].startswith("UNF:6:N9:")

    def test_invalid_input(self):
        """Test that non-DataFrame input raises TypeError."""
        with pytest.raises(TypeError):
            dataframe_column_unfs([1, 2, 3])


class TestPandasIntegration:
    """Integration tests for pandas functionality."""

    def test_real_world_example(self):
        """Test with a realistic DataFrame."""
        df = pd.DataFrame({
            'student_id': [1001, 1002, 1003, 1004],
            'name': ['Alice', 'Bob', 'Charlie', 'David'],
            'age': [20, 21, 20, 22],
            'gpa': [3.8, 3.6, 3.9, 3.7],
            'enrolled': [True, True, False, True]
        })

        # Calculate overall UNF
        overall_unf = dataframe_unf(df)
        assert overall_unf.startswith("UNF:6:")

        # Calculate column UNFs
        col_unfs = dataframe_column_unfs(df)
        assert len(col_unfs) == 5

        # Test determinism
        assert dataframe_unf(df) == overall_unf

    def test_datetime_series(self):
        """Test UNF for datetime series."""
        s = pd.Series(pd.date_range('2024-01-01', periods=5, freq='D'))
        unf = series_unf(s)
        assert unf.startswith("UNF:6:")

    def test_categorical_series(self):
        """Test UNF for categorical series."""
        s = pd.Series(['A', 'B', 'C', 'A', 'B'], dtype='category')
        unf = series_unf(s)
        assert unf.startswith("UNF:6:")
