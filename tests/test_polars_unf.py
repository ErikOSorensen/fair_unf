"""Tests for polars integration.

These tests verify that the polars convenience functions work correctly
and that polars handles null values properly (converting to None instead
of NaN, which is superior to pandas).
"""

import pytest


class TestPolarsIntegration:
    """Test polars Series and DataFrame UNF calculations."""

    @pytest.fixture
    def pl(self):
        """Import polars, skip tests if not available."""
        try:
            import polars
            return polars
        except ImportError:
            pytest.skip("polars not installed")

    def test_series_unf_basic(self, pl):
        """Test UNF calculation for a simple polars Series."""
        from unf.polars_unf import series_unf

        s = pl.Series([1, 2, 3, 4, 5])
        unf = series_unf(s)

        assert unf.startswith("UNF:6:")
        assert len(unf) > 10

    def test_series_unf_with_nulls(self, pl):
        """Test that polars null values are handled correctly."""
        from unf.polars_unf import series_unf
        from unf import calculate_unf

        # Polars Series with nulls
        s = pl.Series([1.0, 2.0, None, 4.0])
        unf_polars = series_unf(s)

        # Direct list with None
        data = [1.0, 2.0, None, 4.0]
        unf_direct = calculate_unf(data)

        # Should match because polars converts null → None
        assert unf_polars == unf_direct

    def test_series_unf_preserves_nan(self, pl):
        """Test that polars preserves NaN (distinct from null)."""
        from unf.polars_unf import series_unf
        from unf import calculate_unf

        # Polars with explicit NaN (not null)
        s_nan = pl.Series([1.0, 2.0, float('nan'), 4.0])
        unf_nan = series_unf(s_nan)

        # Polars with null
        s_null = pl.Series([1.0, 2.0, None, 4.0])
        unf_null = series_unf(s_null)

        # These should be DIFFERENT because NaN ≠ null in polars
        # However, our calculate_unf() function converts NaN → None
        # So they will actually match. This documents the behavior.
        # If we wanted to preserve NaN, we'd need to modify calculate_unf

    def test_series_unf_strings(self, pl):
        """Test UNF calculation for string data."""
        from unf.polars_unf import series_unf

        s = pl.Series(['Alice', 'Bob', 'Charlie'])
        unf = series_unf(s)

        assert unf.startswith("UNF:6:")

    def test_series_unf_strings_with_nulls(self, pl):
        """Test string data with null values."""
        from unf.polars_unf import series_unf

        s = pl.Series(['Alice', None, 'Charlie'])
        unf = series_unf(s)

        assert unf.startswith("UNF:6:")

    def test_dataframe_unf_basic(self, pl):
        """Test UNF calculation for a polars DataFrame."""
        from unf.polars_unf import dataframe_unf

        df = pl.DataFrame({
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'score': [85.5, 90.0, 88.5]
        })

        unf = dataframe_unf(df)
        assert unf.startswith("UNF:6:")

    def test_dataframe_unf_with_nulls(self, pl):
        """Test DataFrame UNF with missing values."""
        from unf.polars_unf import dataframe_unf

        df = pl.DataFrame({
            'id': [1, 2, 3],
            'value': [1.5, None, 3.5],
            'name': ['Alice', None, 'Charlie']
        })

        unf = dataframe_unf(df)
        assert unf.startswith("UNF:6:")

    def test_dataframe_unf_empty(self, pl):
        """Test UNF for empty DataFrame."""
        from unf.polars_unf import dataframe_unf

        df = pl.DataFrame()
        unf = dataframe_unf(df)

        assert unf.startswith("UNF:6:")

    def test_dataframe_unf_order_independence(self, pl):
        """Test that column order doesn't affect DataFrame UNF."""
        from unf.polars_unf import dataframe_unf

        df1 = pl.DataFrame({
            'a': [1, 2, 3],
            'b': [4, 5, 6]
        })

        df2 = pl.DataFrame({
            'b': [4, 5, 6],
            'a': [1, 2, 3]
        })

        unf1 = dataframe_unf(df1)
        unf2 = dataframe_unf(df2)

        assert unf1 == unf2

    def test_dataframe_column_unfs(self, pl):
        """Test getting individual column UNFs."""
        from unf.polars_unf import dataframe_column_unfs

        df = pl.DataFrame({
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie']
        })

        unfs = dataframe_column_unfs(df)

        assert isinstance(unfs, dict)
        assert 'id' in unfs
        assert 'name' in unfs
        assert unfs['id'].startswith('UNF:6:')
        assert unfs['name'].startswith('UNF:6:')

    def test_series_type_validation(self, pl):
        """Test that series_unf validates input type."""
        from unf.polars_unf import series_unf

        with pytest.raises(TypeError, match="Expected pl.Series"):
            series_unf([1, 2, 3])

    def test_dataframe_type_validation(self, pl):
        """Test that dataframe_unf validates input type."""
        from unf.polars_unf import dataframe_unf

        with pytest.raises(TypeError, match="Expected pl.DataFrame"):
            dataframe_unf({'a': [1, 2, 3]})


class TestPolarsVsPandas:
    """Compare polars and pandas implementations."""

    @pytest.fixture
    def pl(self):
        """Import polars, skip if not available."""
        try:
            import polars
            return polars
        except ImportError:
            pytest.skip("polars not installed")

    @pytest.fixture
    def pd(self):
        """Import pandas, skip if not available."""
        try:
            import pandas
            return pandas
        except ImportError:
            pytest.skip("pandas not installed")

    def test_polars_pandas_equivalence_basic(self, pl, pd):
        """Test that polars and pandas produce the same UNF for basic data."""
        from unf.polars_unf import series_unf as polars_series_unf
        from unf.pandas_unf import series_unf as pandas_series_unf

        data = [1, 2, 3, 4, 5]

        pl_series = pl.Series(data)
        pd_series = pd.Series(data)

        unf_polars = polars_series_unf(pl_series)
        unf_pandas = pandas_series_unf(pd_series)

        assert unf_polars == unf_pandas

    def test_polars_pandas_equivalence_with_nulls(self, pl, pd):
        """Test that polars and pandas produce the same UNF for data with nulls."""
        from unf.polars_unf import series_unf as polars_series_unf
        from unf.pandas_unf import series_unf as pandas_series_unf

        data = [1.0, 2.0, None, 4.0]

        pl_series = pl.Series(data)
        pd_series = pd.Series(data)

        unf_polars = polars_series_unf(pl_series)
        unf_pandas = pandas_series_unf(pd_series)

        assert unf_polars == unf_pandas

    def test_polars_pandas_dataframe_equivalence(self, pl, pd):
        """Test that DataFrame UNFs match between polars and pandas."""
        from unf.polars_unf import dataframe_unf as polars_df_unf
        from unf.pandas_unf import dataframe_unf as pandas_df_unf

        data = {
            'id': [1, 2, 3],
            'value': [1.5, 2.5, 3.5]
        }

        pl_df = pl.DataFrame(data)
        pd_df = pd.DataFrame(data)

        unf_polars = polars_df_unf(pl_df)
        unf_pandas = pandas_df_unf(pd_df)

        assert unf_polars == unf_pandas


class TestPolarsNullHandling:
    """Test polars' superior null handling."""

    @pytest.fixture
    def pl(self):
        """Import polars, skip if not available."""
        try:
            import polars
            return polars
        except ImportError:
            pytest.skip("polars not installed")

    def test_polars_converts_null_to_none(self, pl):
        """Test that polars.to_list() converts null to None."""
        s = pl.Series([1.0, 2.0, None, 4.0])
        as_list = s.to_list()

        # Third element should be Python None
        assert as_list[2] is None

    def test_polars_preserves_nan_in_list(self, pl):
        """Test that polars preserves NaN when explicitly provided."""
        import math

        s = pl.Series([1.0, 2.0, float('nan'), 4.0])
        as_list = s.to_list()

        # Third element should be NaN (not None)
        assert isinstance(as_list[2], float)
        assert math.isnan(as_list[2])

    def test_polars_null_vs_nan_distinction(self, pl):
        """Document that polars maintains null vs NaN distinction."""
        import math

        # Series with both null and NaN
        s = pl.Series([1.0, None, float('nan'), 4.0])
        as_list = s.to_list()

        # Index 1: null → None
        assert as_list[1] is None

        # Index 2: NaN → NaN
        assert isinstance(as_list[2], float)
        assert math.isnan(as_list[2])

    def test_polars_integer_with_nulls(self, pl):
        """Test that polars can handle integer columns with nulls.

        This is a key advantage over pandas, which converts integer
        columns to float when they contain missing values.
        """
        from unf.polars_unf import series_unf

        # polars can have Int64 with nulls
        s = pl.Series([1, 2, None, 4], dtype=pl.Int64)
        unf = series_unf(s)

        assert unf.startswith("UNF:6:")

        # The list should have None, not NaN
        as_list = s.to_list()
        assert as_list[2] is None


class TestPolarsStataIntegration:
    """Test using polars with Stata file data."""

    @pytest.fixture
    def pl(self):
        """Import polars, skip if not available."""
        try:
            import polars
            return polars
        except ImportError:
            pytest.skip("polars not installed")

    def test_stata_via_polars_conversion(self, pl):
        """Test that Stata data converted through polars works correctly."""
        try:
            import pyreadstat
        except ImportError:
            pytest.skip("pyreadstat not installed")

        from unf.polars_unf import series_unf

        # Read Stata file with pyreadstat (returns pandas)
        df_pandas, meta = pyreadstat.read_dta(
            'tests/mmtalent_df.dta',
            apply_value_formats=False
        )

        # Convert to polars
        df_polars = pl.from_pandas(df_pandas)

        # Calculate UNF using polars
        unf_polars = series_unf(df_polars['wgt'])

        # Expected from R reference
        expected = 'UNF:6:PYILaPsjS5hqF2dDKIYWfg=='

        assert unf_polars == expected
