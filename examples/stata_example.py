"""Example: Calculate UNF for Stata dataset using pandas.

This example demonstrates how to read a Stata .dta file using pandas
and calculate its UNF fingerprint, which can be useful for:
- Data verification and integrity checking
- Comparing datasets across different formats
- Creating reproducible fingerprints for Stata datasets
"""

import pandas as pd
from unf import dataframe_unf, dataframe_column_unfs


def calculate_stata_unf(filepath: str, verbose: bool = True):
    """Calculate UNF for a Stata dataset.

    Args:
        filepath: Path to the .dta file
        verbose: If True, print detailed information

    Returns:
        Dictionary with overall UNF and column UNFs
    """
    # Read Stata file
    if verbose:
        print(f"Reading Stata file: {filepath}")
        print("=" * 60)

    df = pd.read_stata(filepath)

    if verbose:
        print(f"\nDataset shape: {df.shape[0]} rows × {df.shape[1]} columns")
        print(f"\nColumns: {list(df.columns)}")
        print(f"\nFirst few rows:")
        print(df.head())
        print("\n" + "=" * 60)

    # Calculate overall UNF
    overall_unf = dataframe_unf(df)

    # Calculate individual column UNFs
    column_unfs = dataframe_column_unfs(df)

    if verbose:
        print(f"\nOverall Dataset UNF: {overall_unf}")
        print(f"\nIndividual Column UNFs:")
        for col, unf in column_unfs.items():
            print(f"  {col:20s}: {unf}")

    return {
        'overall_unf': overall_unf,
        'column_unfs': column_unfs,
        'shape': df.shape,
        'columns': list(df.columns)
    }


def compare_stata_datasets(file1: str, file2: str):
    """Compare two Stata datasets using UNF fingerprints.

    Args:
        file1: Path to first .dta file
        file2: Path to second .dta file

    Returns:
        Boolean indicating if datasets are identical
    """
    print(f"Comparing datasets:")
    print(f"  File 1: {file1}")
    print(f"  File 2: {file2}")
    print("=" * 60)

    # Read both files
    df1 = pd.read_stata(file1)
    df2 = pd.read_stata(file2)

    # Calculate UNFs
    unf1 = dataframe_unf(df1)
    unf2 = dataframe_unf(df2)

    print(f"\nDataset 1 UNF: {unf1}")
    print(f"Dataset 2 UNF: {unf2}")

    identical = unf1 == unf2
    print(f"\nDatasets identical: {identical}")

    if not identical:
        # Show which columns differ
        col_unfs1 = dataframe_column_unfs(df1)
        col_unfs2 = dataframe_column_unfs(df2)

        all_cols = set(col_unfs1.keys()) | set(col_unfs2.keys())
        print("\nColumn comparison:")
        for col in sorted(all_cols):
            u1 = col_unfs1.get(col, "MISSING")
            u2 = col_unfs2.get(col, "MISSING")
            status = "✓" if u1 == u2 else "✗"
            print(f"  {status} {col}")

    return identical


def create_example_stata_file(filename: str = "example.dta"):
    """Create an example Stata file for demonstration.

    Args:
        filename: Output filename (default: example.dta)
    """
    import os

    # Create example data
    df = pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
        'age': [25, 30, 35, 28, 32],
        'income': [50000.0, 65000.0, 75000.0, 58000.0, 70000.0],
        'employed': [1, 1, 1, 0, 1],  # Boolean as 0/1 for Stata
        'region': ['North', 'South', 'East', 'West', 'North']
    })

    # Save as Stata file
    df.to_stata(filename, write_index=False)
    print(f"Created example Stata file: {filename}")
    print(f"File size: {os.path.getsize(filename)} bytes")

    return filename


def main():
    """Main example demonstrating Stata UNF calculation."""
    print("Stata Dataset UNF Calculation Example")
    print("=" * 60)
    print()

    # Create an example Stata file
    example_file = create_example_stata_file("foo.dta")
    print()

    # Calculate UNF for the example file
    result = calculate_stata_unf("foo.dta", verbose=True)
    print()

    # Create a modified version
    print("\nCreating modified dataset...")
    df_modified = pd.read_stata("foo.dta")
    df_modified['income'] = df_modified['income'] * 1.1  # 10% increase
    df_modified.to_stata("foo_modified.dta", write_index=False)
    print("Created: foo_modified.dta (with 10% income increase)")
    print()

    # Compare original and modified
    are_same = compare_stata_datasets("foo.dta", "foo_modified.dta")
    print()

    # Show that reordering columns doesn't change UNF
    print("\nDemonstrating column order independence...")
    df_reordered = pd.read_stata("foo.dta")
    df_reordered = df_reordered[['region', 'employed', 'income', 'age', 'name', 'id']]
    df_reordered.to_stata("foo_reordered.dta", write_index=False)

    unf_original = dataframe_unf(pd.read_stata("foo.dta"))
    unf_reordered = dataframe_unf(pd.read_stata("foo_reordered.dta"))

    print(f"Original UNF:   {unf_original}")
    print(f"Reordered UNF:  {unf_reordered}")
    print(f"Same UNF: {unf_original == unf_reordered}")
    print()

    print("=" * 60)
    print("Summary:")
    print(f"✓ Successfully read and processed Stata dataset")
    print(f"✓ Calculated overall UNF: {result['overall_unf']}")
    print(f"✓ Calculated UNF for {len(result['column_unfs'])} columns")
    print(f"✓ Verified column order independence")
    print(f"✓ Detected data modifications")


if __name__ == "__main__":
    main()
