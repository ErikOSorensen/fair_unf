"""Tests for UNF calculation functions."""

import pytest
from ufn import calculate_unf, combine_unfs
from ufn.unf import UNFConfig, calculate_dataset_unf


class TestUNFConfig:
    """Tests for UNF configuration."""

    def test_default_config(self):
        config = UNFConfig()
        assert config.version == 6
        assert config.precision == 7
        assert config.max_chars == 128
        assert config.hash_bits == 128
        assert config.truncate is False

    def test_default_header(self):
        config = UNFConfig()
        assert config.get_header() == "UNF:6:"

    def test_custom_precision_header(self):
        config = UNFConfig(precision=9)
        assert config.get_header() == "UNF:6:N9:"

    def test_multiple_params_header(self):
        config = UNFConfig(precision=9, max_chars=256, hash_bits=256)
        header = config.get_header()
        assert "UNF:6:" in header
        assert "N9" in header
        assert "X256" in header
        assert "H256" in header

    def test_invalid_version(self):
        with pytest.raises(ValueError):
            UNFConfig(version=5)

    def test_invalid_hash_bits(self):
        with pytest.raises(ValueError):
            UNFConfig(hash_bits=100)


class TestCalculateUNF:
    """Tests for calculate_unf function."""

    def test_simple_numeric_vector(self):
        data = [1.0, 2.0, 3.0]
        result = calculate_unf(data)
        assert result.startswith("UNF:6:")
        assert len(result) > 10  # Should have base64 hash

    def test_vector_with_missing_values(self):
        data = [1.0, None, 3.0]
        result = calculate_unf(data)
        assert result.startswith("UNF:6:")

    def test_string_vector(self):
        data = ["hello", "world", "test"]
        result = calculate_unf(data)
        assert result.startswith("UNF:6:")

    def test_boolean_vector(self):
        data = [True, False, True, True]
        result = calculate_unf(data)
        assert result.startswith("UNF:6:")

    def test_mixed_types(self):
        data = [1.0, "hello", True, None]
        result = calculate_unf(data)
        assert result.startswith("UNF:6:")

    def test_empty_vector(self):
        data = []
        result = calculate_unf(data)
        assert result.startswith("UNF:6:")

    def test_custom_config(self):
        data = [1.0, 2.0, 3.0]
        config = UNFConfig(precision=9)
        result = calculate_unf(data, config)
        assert result.startswith("UNF:6:N9:")

    def test_deterministic(self):
        """UNF should be deterministic for the same data."""
        data = [1.0, 2.0, 3.0]
        result1 = calculate_unf(data)
        result2 = calculate_unf(data)
        assert result1 == result2

    def test_order_matters(self):
        """Different order should give different UNF."""
        data1 = [1.0, 2.0, 3.0]
        data2 = [3.0, 2.0, 1.0]
        result1 = calculate_unf(data1)
        result2 = calculate_unf(data2)
        assert result1 != result2


class TestCombineUNFs:
    """Tests for combine_unfs function."""

    def test_combine_two_unfs(self):
        unf1 = calculate_unf([1.0, 2.0, 3.0])
        unf2 = calculate_unf([4.0, 5.0, 6.0])
        result = combine_unfs([unf1, unf2])
        assert result.startswith("UNF:6:")

    def test_combine_is_order_independent(self):
        """Combined UNF should be same regardless of input order."""
        unf1 = calculate_unf([1.0, 2.0, 3.0])
        unf2 = calculate_unf([4.0, 5.0, 6.0])
        unf3 = calculate_unf([7.0, 8.0, 9.0])

        result1 = combine_unfs([unf1, unf2, unf3])
        result2 = combine_unfs([unf3, unf1, unf2])
        result3 = combine_unfs([unf2, unf3, unf1])

        assert result1 == result2 == result3

    def test_combine_empty(self):
        result = combine_unfs([])
        assert result == "UNF:6:"

    def test_combine_single(self):
        unf1 = calculate_unf([1.0, 2.0, 3.0])
        result = combine_unfs([unf1])
        assert result.startswith("UNF:6:")


class TestCalculateDatasetUNF:
    """Tests for calculate_dataset_unf function."""

    def test_simple_dataset(self):
        # Dataset with 3 variables (columns)
        data = [
            [1.0, 2.0, 3.0],  # Variable 1
            [4.0, 5.0, 6.0],  # Variable 2
            [7.0, 8.0, 9.0],  # Variable 3
        ]
        result = calculate_dataset_unf(data)
        assert result.startswith("UNF:6:")

    def test_dataset_order_independent(self):
        """Dataset UNF should be same regardless of column order."""
        var1 = [1.0, 2.0, 3.0]
        var2 = [4.0, 5.0, 6.0]
        var3 = [7.0, 8.0, 9.0]

        result1 = calculate_dataset_unf([var1, var2, var3])
        result2 = calculate_dataset_unf([var3, var1, var2])
        result3 = calculate_dataset_unf([var2, var3, var1])

        assert result1 == result2 == result3

    def test_empty_dataset(self):
        result = calculate_dataset_unf([])
        assert result == "UNF:6:"

    def test_mixed_types_dataset(self):
        data = [
            [1.0, 2.0, 3.0],
            ["a", "b", "c"],
            [True, False, True],
        ]
        result = calculate_dataset_unf(data)
        assert result.startswith("UNF:6:")


class TestUNFExamples:
    """Integration tests with more realistic examples."""

    def test_real_world_numeric_data(self):
        """Test with realistic numeric data."""
        data = [3.14159, 2.71828, 1.41421, 1.73205]
        result = calculate_unf(data)
        assert result.startswith("UNF:6:")
        # Result should be consistent
        assert calculate_unf(data) == result

    def test_real_world_string_data(self):
        """Test with realistic string data."""
        data = ["Alice", "Bob", "Charlie", "David"]
        result = calculate_unf(data)
        assert result.startswith("UNF:6:")

    def test_real_world_mixed_dataset(self):
        """Test with a realistic mixed-type dataset."""
        dataset = [
            [1, 2, 3, 4, 5],  # ID column
            ["Alice", "Bob", "Charlie", "David", "Eve"],  # Name column
            [25, 30, 35, 40, 45],  # Age column
            [True, False, True, False, True],  # Active column
        ]
        result = calculate_dataset_unf(dataset)
        assert result.startswith("UNF:6:")
