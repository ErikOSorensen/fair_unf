"""Basic usage examples for the UNF library."""

from unf import calculate_unf, calculate_dataset_unf, combine_unfs
from unf.unf import UNFConfig


def example_simple_vector():
    """Calculate UNF for a simple numeric vector."""
    print("=== Simple Numeric Vector ===")
    data = [1.0, 2.0, 3.0, 4.0, 5.0]
    unf = calculate_unf(data)
    print(f"Data: {data}")
    print(f"UNF: {unf}\n")


def example_mixed_types():
    """Calculate UNF for mixed data types."""
    print("=== Mixed Data Types ===")
    data = [1, "hello", True, 3.14, None]
    unf = calculate_unf(data)
    print(f"Data: {data}")
    print(f"UNF: {unf}\n")


def example_dataset():
    """Calculate UNF for a complete dataset."""
    print("=== Dataset with Multiple Variables ===")
    dataset = [
        [1, 2, 3, 4, 5],                          # ID column
        ["Alice", "Bob", "Charlie", "Dave", "Eve"], # Name column
        [25, 30, 35, 40, 45],                      # Age column
        [True, False, True, False, True],          # Active status
    ]

    # Calculate individual UNFs
    print("Individual variable UNFs:")
    for i, variable in enumerate(dataset):
        unf = calculate_unf(variable)
        print(f"  Variable {i+1}: {unf}")

    # Calculate dataset UNF
    dataset_unf = calculate_dataset_unf(dataset)
    print(f"\nDataset UNF: {dataset_unf}\n")


def example_order_independence():
    """Demonstrate that dataset UNF is order-independent."""
    print("=== Order Independence ===")
    var1 = [1, 2, 3]
    var2 = [4, 5, 6]
    var3 = [7, 8, 9]

    unf1 = calculate_dataset_unf([var1, var2, var3])
    unf2 = calculate_dataset_unf([var3, var1, var2])
    unf3 = calculate_dataset_unf([var2, var3, var1])

    print(f"Dataset [var1, var2, var3]: {unf1}")
    print(f"Dataset [var3, var1, var2]: {unf2}")
    print(f"Dataset [var2, var3, var1]: {unf3}")
    print(f"All equal: {unf1 == unf2 == unf3}\n")


def example_custom_config():
    """Use custom configuration for UNF calculation."""
    print("=== Custom Configuration ===")
    data = [3.14159265358979323846]

    # Default precision (7 digits)
    unf_default = calculate_unf(data)
    print(f"Default (N=7): {unf_default}")

    # Higher precision (9 digits)
    config_high = UNFConfig(precision=9)
    unf_high = calculate_unf(data, config_high)
    print(f"High precision (N=9): {unf_high}")

    # Lower precision (3 digits)
    config_low = UNFConfig(precision=3)
    unf_low = calculate_unf(data, config_low)
    print(f"Low precision (N=3): {unf_low}\n")


def example_missing_values():
    """Handle missing (None) values."""
    print("=== Missing Values ===")
    data_complete = [1.0, 2.0, 3.0, 4.0, 5.0]
    data_missing = [1.0, None, 3.0, None, 5.0]

    unf_complete = calculate_unf(data_complete)
    unf_missing = calculate_unf(data_missing)

    print(f"Complete data: {data_complete}")
    print(f"UNF: {unf_complete}")
    print(f"\nData with missing: {data_missing}")
    print(f"UNF: {unf_missing}")
    print(f"Different: {unf_complete != unf_missing}\n")


def example_combining_unfs():
    """Combine existing UNF fingerprints."""
    print("=== Combining UNFs ===")

    # Calculate UNFs for individual variables
    unf1 = calculate_unf([1, 2, 3])
    unf2 = calculate_unf([4, 5, 6])
    unf3 = calculate_unf([7, 8, 9])

    print(f"UNF1: {unf1}")
    print(f"UNF2: {unf2}")
    print(f"UNF3: {unf3}")

    # Combine them (order-independent)
    combined = combine_unfs([unf1, unf2, unf3])
    combined_reversed = combine_unfs([unf3, unf2, unf1])

    print(f"\nCombined [1,2,3]: {combined}")
    print(f"Combined [3,2,1]: {combined_reversed}")
    print(f"Equal: {combined == combined_reversed}\n")


if __name__ == "__main__":
    example_simple_vector()
    example_mixed_types()
    example_dataset()
    example_order_independence()
    example_custom_config()
    example_missing_values()
    example_combining_unfs()
