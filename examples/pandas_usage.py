"""Pandas integration examples for the UNF library."""

import pandas as pd
from unf import series_unf, dataframe_unf, dataframe_column_unfs
from unf.unf import UNFConfig


def example_series_unf():
    """Calculate UNF for pandas Series."""
    print("=== Series UNF ===")

    # Numeric series
    s_numeric = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0], name='values')
    unf = series_unf(s_numeric)
    print(f"Numeric series: {list(s_numeric)}")
    print(f"UNF: {unf}\n")

    # String series
    s_string = pd.Series(['Alice', 'Bob', 'Charlie'], name='names')
    unf = series_unf(s_string)
    print(f"String series: {list(s_string)}")
    print(f"UNF: {unf}\n")

    # Series with missing values
    s_missing = pd.Series([1.0, None, 3.0, pd.NA, 5.0], name='with_missing')
    unf = series_unf(s_missing)
    print(f"Series with missing: {list(s_missing)}")
    print(f"UNF: {unf}\n")


def example_dataframe_unf():
    """Calculate UNF for pandas DataFrame."""
    print("=== DataFrame UNF ===")

    # Create a sample DataFrame
    df = pd.DataFrame({
        'student_id': [1001, 1002, 1003, 1004, 1005],
        'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
        'age': [20, 21, 20, 22, 21],
        'gpa': [3.8, 3.6, 3.9, 3.7, 3.85],
        'enrolled': [True, True, False, True, True]
    })

    print("DataFrame:")
    print(df)
    print()

    # Calculate overall DataFrame UNF
    df_unf = dataframe_unf(df)
    print(f"DataFrame UNF: {df_unf}\n")


def example_column_unfs():
    """Get individual column UNFs from a DataFrame."""
    print("=== Individual Column UNFs ===")

    df = pd.DataFrame({
        'id': [1, 2, 3, 4],
        'category': ['A', 'B', 'A', 'C'],
        'value': [10.5, 20.3, 15.7, 18.9]
    })

    print("DataFrame:")
    print(df)
    print()

    # Get UNF for each column
    col_unfs = dataframe_column_unfs(df)
    print("Column UNFs:")
    for col_name, col_unf in col_unfs.items():
        print(f"  {col_name}: {col_unf}")
    print()


def example_order_independence():
    """Demonstrate that column order doesn't affect DataFrame UNF."""
    print("=== Column Order Independence ===")

    # Create DataFrames with same data but different column orders
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

    print(f"DataFrame 1 (a,b,c): {unf1}")
    print(f"DataFrame 2 (c,a,b): {unf2}")
    print(f"DataFrame 3 (b,c,a): {unf3}")
    print(f"All equal: {unf1 == unf2 == unf3}\n")


def example_custom_precision():
    """Use custom precision for numeric data."""
    print("=== Custom Precision ===")

    df = pd.DataFrame({
        'pi': [3.14159265358979323846],
        'e': [2.71828182845904523536]
    })

    print("DataFrame:")
    print(df)
    print()

    # Default precision (7 digits)
    unf_default = dataframe_unf(df)
    print(f"Default (N=7): {unf_default}")

    # Higher precision (9 digits)
    config_high = UNFConfig(precision=9)
    unf_high = dataframe_unf(df, config_high)
    print(f"High precision (N=9): {unf_high}")

    # Lower precision (3 digits)
    config_low = UNFConfig(precision=3)
    unf_low = dataframe_unf(df, config_low)
    print(f"Low precision (N=3): {unf_low}\n")


def example_datetime_data():
    """Handle datetime data in DataFrame."""
    print("=== DateTime Data ===")

    df = pd.DataFrame({
        'event_id': [1, 2, 3, 4],
        'timestamp': pd.date_range('2024-01-01', periods=4, freq='D'),
        'value': [100, 150, 125, 175]
    })

    print("DataFrame:")
    print(df)
    print()

    unf = dataframe_unf(df)
    print(f"DataFrame UNF: {unf}\n")


def example_real_world():
    """A realistic example with mixed data types."""
    print("=== Real World Example ===")

    # Create a sample dataset
    df = pd.DataFrame({
        'transaction_id': [1001, 1002, 1003, 1004, 1005],
        'date': pd.date_range('2024-01-01', periods=5),
        'customer': ['Alice', 'Bob', 'Alice', 'Charlie', 'Bob'],
        'amount': [125.50, 200.00, 75.25, 150.00, 300.75],
        'category': ['Food', 'Electronics', 'Food', 'Clothing', 'Electronics'],
        'refunded': [False, False, True, False, False]
    })

    print("Transaction DataFrame:")
    print(df)
    print()

    # Calculate UNFs
    overall_unf = dataframe_unf(df)
    column_unfs = dataframe_column_unfs(df)

    print(f"Overall UNF: {overall_unf}")
    print("\nColumn UNFs:")
    for col, unf in column_unfs.items():
        print(f"  {col}: {unf}")
    print()


if __name__ == "__main__":
    example_series_unf()
    example_dataframe_unf()
    example_column_unfs()
    example_order_independence()
    example_custom_precision()
    example_datetime_data()
    example_real_world()
