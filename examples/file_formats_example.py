"""Comprehensive example: Calculate UNF for various file formats.

This example demonstrates how to calculate UNF fingerprints for datasets
stored in different file formats (CSV, Parquet, Stata, Excel, JSON, etc.)
using the file_unf function with automatic format detection.
"""

import pandas as pd
from unf import file_unf
from unf.file_io import csv_unf, parquet_unf, stata_unf, excel_unf, json_unf
from pathlib import Path
import tempfile


def create_sample_dataset():
    """Create a sample dataset for demonstration."""
    return pd.DataFrame({
        'student_id': [1001, 1002, 1003, 1004, 1005],
        'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
        'age': [20, 21, 20, 22, 21],
        'gpa': [3.8, 3.6, 3.9, 3.7, 3.85],
        'enrolled': [True, True, False, True, True],
        'major': ['Physics', 'Math', 'CS', 'Biology', 'Chemistry']
    })


def demonstrate_auto_detection():
    """Demonstrate automatic format detection."""
    print("=" * 70)
    print("AUTOMATIC FORMAT DETECTION")
    print("=" * 70)
    print()

    df = create_sample_dataset()

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create files in different formats
        formats = {}

        # CSV
        csv_file = tmp_path / "data.csv"
        df.to_csv(csv_file, index=False)
        formats['CSV'] = csv_file

        # Try Parquet (may not be available)
        try:
            import pyarrow
            parquet_file = tmp_path / "data.parquet"
            df.to_parquet(parquet_file, index=False)
            formats['Parquet'] = parquet_file
        except ImportError:
            print("⚠ Parquet support not available (install pyarrow)")

        # Stata
        stata_file = tmp_path / "data.dta"
        df.to_stata(stata_file, write_index=False)
        formats['Stata'] = stata_file

        # JSON
        json_file = tmp_path / "data.json"
        df.to_json(json_file, orient='records')
        formats['JSON'] = json_file

        # Try Excel (may not be available)
        try:
            import openpyxl
            excel_file = tmp_path / "data.xlsx"
            df.to_excel(excel_file, index=False)
            formats['Excel'] = excel_file
        except ImportError:
            print("⚠ Excel support not available (install openpyxl)")

        print()
        print(f"Created {len(formats)} test files")
        print()

        # Calculate UNF for each format (auto-detect)
        print("Format-specific UNFs (auto-detected):")
        print("-" * 70)
        unfs = {}
        for format_name, filepath in formats.items():
            unf = file_unf(filepath)
            unfs[format_name] = unf
            print(f"{format_name:10s}: {unf}")

        print()

        # Verify all formats produce the same UNF
        unique_unfs = set(unfs.values())
        if len(unique_unfs) == 1:
            print("✓ All formats produce the SAME UNF!")
            print(f"  Common UNF: {list(unique_unfs)[0]}")
        else:
            print("✗ Warning: Different UNFs detected")
            for format_name, unf in unfs.items():
                print(f"  {format_name}: {unf}")

        print()


def demonstrate_explicit_format():
    """Demonstrate explicit format specification."""
    print("=" * 70)
    print("EXPLICIT FORMAT SPECIFICATION")
    print("=" * 70)
    print()

    df = create_sample_dataset()

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Save CSV with non-standard extension
        custom_file = tmp_path / "data.txt"
        df.to_csv(custom_file, index=False)

        print("File: data.txt (CSV format with .txt extension)")
        print()

        # This would fail with auto-detect
        try:
            unf_auto = file_unf(custom_file)
            print(f"Auto-detect UNF: {unf_auto}")
        except ValueError as e:
            print(f"Auto-detect failed: {e}")
            print()

        # Explicitly specify format
        unf_explicit = file_unf(custom_file, format="csv")
        print(f"Explicit format UNF: {unf_explicit}")
        print()


def demonstrate_custom_options():
    """Demonstrate custom pandas read options."""
    print("=" * 70)
    print("CUSTOM PANDAS OPTIONS")
    print("=" * 70)
    print()

    df = create_sample_dataset()

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Save CSV with custom separator
        tsv_file = tmp_path / "data.tsv"
        df.to_csv(tsv_file, index=False, sep="\t")

        print("File: data.tsv (tab-separated)")
        print()

        # Read with custom separator
        unf = file_unf(tsv_file, sep="\t")
        print(f"UNF (with sep='\\t'): {unf}")
        print()

        # Save CSV with different encoding
        csv_file = tmp_path / "data_latin1.csv"
        df.to_csv(csv_file, index=False, encoding='latin1')

        print("File: data_latin1.csv (latin1 encoding)")
        print()

        # Read with custom encoding
        unf = file_unf(csv_file, encoding='latin1')
        print(f"UNF (with encoding='latin1'): {unf}")
        print()


def demonstrate_metadata():
    """Demonstrate metadata extraction."""
    print("=" * 70)
    print("METADATA EXTRACTION")
    print("=" * 70)
    print()

    df = create_sample_dataset()

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        csv_file = tmp_path / "data.csv"
        df.to_csv(csv_file, index=False)

        # Get UNF with metadata
        result = file_unf(csv_file, return_metadata=True)

        print("Metadata for data.csv:")
        print("-" * 70)
        print(f"  UNF:      {result['unf']}")
        print(f"  Format:   {result['format']}")
        print(f"  Shape:    {result['shape'][0]} rows × {result['shape'][1]} columns")
        print(f"  Columns:  {', '.join(result['columns'])}")
        print(f"  Filepath: {result['filepath']}")
        print()


def demonstrate_format_comparison():
    """Demonstrate comparing different file formats."""
    print("=" * 70)
    print("FORMAT COMPARISON")
    print("=" * 70)
    print()

    # Original data
    df_original = create_sample_dataset()

    # Modified data (10% GPA increase)
    df_modified = df_original.copy()
    df_modified['gpa'] = df_modified['gpa'] * 1.1

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Save original in CSV
        csv_original = tmp_path / "original.csv"
        df_original.to_csv(csv_original, index=False)

        # Save modified in Stata
        dta_modified = tmp_path / "modified.dta"
        df_modified.to_stata(dta_modified, write_index=False)

        print("Comparing:")
        print(f"  File 1: original.csv (CSV format)")
        print(f"  File 2: modified.dta (Stata format, with 10% GPA increase)")
        print()

        unf1 = file_unf(csv_original)
        unf2 = file_unf(dta_modified)

        print(f"  UNF 1: {unf1}")
        print(f"  UNF 2: {unf2}")
        print()

        if unf1 == unf2:
            print("✓ Files are identical")
        else:
            print("✗ Files differ (as expected due to GPA modification)")

        print()


def demonstrate_format_specific_functions():
    """Demonstrate format-specific functions."""
    print("=" * 70)
    print("FORMAT-SPECIFIC FUNCTIONS")
    print("=" * 70)
    print()

    df = create_sample_dataset()

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        print("Using format-specific functions:")
        print("-" * 70)

        # CSV
        csv_file = tmp_path / "data.csv"
        df.to_csv(csv_file, index=False)
        unf = csv_unf(csv_file)
        print(f"csv_unf():     {unf}")

        # Parquet
        try:
            import pyarrow
            parquet_file = tmp_path / "data.parquet"
            df.to_parquet(parquet_file, index=False)
            unf = parquet_unf(parquet_file)
            print(f"parquet_unf(): {unf}")
        except ImportError:
            print(f"parquet_unf(): [pyarrow not available]")

        # Stata
        stata_file = tmp_path / "data.dta"
        df.to_stata(stata_file, write_index=False)
        unf = stata_unf(stata_file)
        print(f"stata_unf():   {unf}")

        # JSON
        json_file = tmp_path / "data.json"
        df.to_json(json_file, orient='records')
        unf = json_unf(json_file)
        print(f"json_unf():    {unf}")

        # Excel
        try:
            import openpyxl
            excel_file = tmp_path / "data.xlsx"
            df.to_excel(excel_file, index=False)
            unf = excel_unf(excel_file)
            print(f"excel_unf():   {unf}")
        except ImportError:
            print(f"excel_unf():   [openpyxl not available]")

        print()


def main():
    """Run all demonstrations."""
    print()
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "UNF FILE FORMAT EXAMPLES" + " " * 29 + "║")
    print("╚" + "═" * 68 + "╝")
    print()

    demonstrate_auto_detection()
    demonstrate_explicit_format()
    demonstrate_custom_options()
    demonstrate_metadata()
    demonstrate_format_comparison()
    demonstrate_format_specific_functions()

    print("=" * 70)
    print("All demonstrations completed successfully!")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
