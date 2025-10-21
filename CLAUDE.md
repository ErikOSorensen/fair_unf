# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python library implementing Universal Numerical Fingerprint (UNF) version 6, a cryptographic hashing algorithm for datasets used by Dataverse and other data management systems. The library calculates deterministic fingerprints for data that are independent of column ordering.

## Development Commands

### Project Setup
- This project uses `uv` for dependency management
- Initialize environment: `uv sync --dev`
- The project requires Python >= 3.12

### Running Tests
- Run all tests: `uv run pytest`
- Run with coverage: `uv run pytest --cov=unf --cov-report=html`
- Run specific test file: `uv run pytest tests/test_unf.py -v`
- Run specific test: `uv run pytest tests/test_unf.py::TestCalculateUNF::test_simple_numeric_vector -v`

### Building and Publishing
- Build package: `uv build`
- The built package will be in `dist/`

### Running Examples
- Basic usage: `uv run python examples/basic_usage.py`

## Architecture

### Module Structure

The library is organized into three main modules:

1. **`src/unf/normalize.py`** - Data type normalization
   - Implements normalization rules for different data types (numeric, string, boolean, dates, etc.)
   - Each data type has its own normalization function following UNF v6 spec
   - Key challenge: Numeric normalization must handle IEEE 754 edge cases (±0.0, ±inf, NaN)
   - Uses Python's `Decimal` for precise rounding to avoid floating-point errors

2. **`src/unf/unf.py`** - Core UNF calculation
   - `UNFConfig`: Configuration class for UNF parameters (precision, hash bits, etc.)
   - `calculate_unf()`: Main function to calculate UNF for a single vector (column)
   - `combine_unfs()`: Combines multiple UNFs in a sort-based, order-independent way
   - `calculate_dataset_unf()`: Convenience function for multi-column datasets
   - Uses SHA256 hashing with configurable truncation and base64 encoding

3. **`src/unf/__init__.py`** - Public API
   - Exports the main functions and classes users interact with

### Key Design Principles

1. **Order Independence**: Dataset UNFs are calculated by sorting individual variable UNFs before combining them, ensuring column order doesn't affect the result

2. **Missing Value Handling**: Missing values (None) are encoded as three null bytes (`\x00\x00\x00`) and treated specially during normalization

3. **Normalization Pipeline**: Each value goes through:
   - Type-specific normalization → UTF-8 encoding → Termination with `\n\x00` → Concatenation → SHA256 → Truncation → Base64

4. **IEEE 754 Compliance**: Special handling for:
   - Positive zero (`+0.e+`) vs negative zero (`-0.e+`)
   - Infinity values (`+inf`, `-inf`)
   - NaN (`+nan`)

### Testing Strategy

- **`tests/test_normalize.py`**: Unit tests for each normalization function
  - Tests edge cases (zeros, infinities, NaN, missing values)
  - Validates format specifications (exponential notation, precision)

- **`tests/test_unf.py`**: Integration tests for UNF calculation
  - Tests determinism (same input → same UNF)
  - Tests order independence for datasets
  - Tests configuration parameters
  - Real-world usage examples

## Important Implementation Notes

### Numeric Normalization (`normalize.py:13-79`)
- Uses `Decimal` for precise rounding to avoid floating-point precision issues
- Must distinguish between +0.0 and -0.0 using `math.copysign()`
- Exponential notation format: `[sign][digit].[digits]e[sign][exponent]`
- Trailing zeros are removed after decimal point, but decimal point is kept

### UNF Calculation (`unf.py:87-133`)
- Non-missing values are terminated with `\n\x00` (newline + null byte)
- Missing values are just `\x00\x00\x00` (no terminator)
- Hash truncation: default 128 bits, but supports 192, 196, or 256
- Header format: `UNF:6:` with optional parameters like `UNF:6:N9,X256:`

### Combining UNFs (`unf.py:136-177`)
- UNFs are sorted lexicographically (POSIX locale) before hashing
- This makes dataset UNF independent of column order
- Each UNF string is treated as a value and gets the same normalization treatment

## Common Development Tasks

When adding support for new data types:
1. Add normalization function in `normalize.py`
2. Update `normalize_value()` in `unf.py` to handle the new type
3. Export the function in `__init__.py` if it should be public
4. Add comprehensive tests in `tests/test_normalize.py`

When debugging UNF mismatches:
1. Calculate UNFs for individual variables to isolate the issue
2. Check normalization output for each value
3. Verify sign handling for zeros in numeric data
4. Check UTF-8 encoding for string data
5. Compare with Dataverse output if available

## UNF v6 Specification Compliance

This implementation follows the Dataverse UNF v6 specification:
- Default parameters match Dataverse (N=7, X=128, H=128)
- Only UNF version 6 is supported
- Timezone handling for dates may differ (expected per spec)
- See: https://guides.dataverse.org/en/latest/developers/unf/unf-v6.html
