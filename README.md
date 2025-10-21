# UNF - Universal Numerical Fingerprint

A Python library for calculating Universal Numerical Fingerprint (UNF) version 6 signatures for datasets, compatible with the Dataverse implementation.

## What is UNF?

Universal Numerical Fingerprint (UNF) is a cryptographic hash that creates unique, verifiable signatures for datasets. UNF is used by [Dataverse](https://dataverse.org/) and other data management systems to:

- Verify data integrity
- Detect changes in datasets
- Create reproducible fingerprints regardless of column order
- Support data citation and versioning

This implementation follows the [UNF v6 specification](https://guides.dataverse.org/en/latest/developers/unf/unf-v6.html).

## Installation

```bash
uv add unf
```

Or with pip:

```bash
pip install unf
```

For pandas integration:

```bash
pip install unf[pandas]
```

## Quick Start

```python
from unf import calculate_unf, calculate_dataset_unf, combine_unfs

# Calculate UNF for a single variable (column)
data = [1.0, 2.0, 3.0, 4.0, 5.0]
unf = calculate_unf(data)
print(unf)  # UNF:6:vcKELUSS4s4k1snF4OTB9A==

# Calculate UNF for a dataset (multiple variables)
dataset = [
    [1, 2, 3, 4, 5],           # Variable 1: ID
    ["A", "B", "C", "D", "E"],  # Variable 2: Category
    [1.5, 2.5, 3.5, 4.5, 5.5],  # Variable 3: Values
]
dataset_unf = calculate_dataset_unf(dataset)
print(dataset_unf)

# Combine existing UNFs (order-independent)
unf1 = calculate_unf([1, 2, 3])
unf2 = calculate_unf([4, 5, 6])
combined = combine_unfs([unf1, unf2])
print(combined)
```

### Pandas Integration

```python
import pandas as pd
from unf import series_unf, dataframe_unf, dataframe_column_unfs

# Calculate UNF for a pandas Series
series = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
unf = series_unf(series)

# Calculate UNF for a pandas DataFrame
df = pd.DataFrame({
    'id': [1, 2, 3],
    'name': ['Alice', 'Bob', 'Charlie'],
    'score': [85.5, 90.0, 88.5]
})
df_unf = dataframe_unf(df)

# Get UNFs for individual columns
column_unfs = dataframe_column_unfs(df)
# {'id': 'UNF:6:...', 'name': 'UNF:6:...', 'score': 'UNF:6:...'}
```

## Features

### Supported Data Types

- **Numeric**: Integers and floating-point numbers with configurable precision
- **Strings**: UTF-8 encoded text with optional truncation
- **Booleans**: Treated as numeric 0/1 values
- **Dates**: ISO 8601 formatted dates
- **Date-times**: ISO 8601 formatted timestamps with UTC conversion
- **Missing values**: Properly handled as null markers

### Special Numeric Handling

The library correctly handles:
- Positive and negative zeros
- Infinity (+inf, -inf)
- NaN (Not a Number)
- IEEE 754 "round to nearest, ties to even" rounding

### Configuration Options

```python
from unf.unf import UNFConfig

# Custom configuration
config = UNFConfig(
    precision=9,        # Significant digits (default: 7)
    max_chars=256,      # String truncation (default: 128)
    hash_bits=256,      # Hash truncation (default: 128)
    truncate=False      # Round vs truncate (default: False)
)

unf = calculate_unf(data, config)
# UNF:6:N9,X256,H256:...
```

## API Reference

### Core Functions

#### `calculate_unf(data, config=None)`

Calculate UNF for a single variable (column).

**Parameters:**
- `data`: Sequence of values (list, tuple, etc.)
- `config`: Optional `UNFConfig` instance

**Returns:** UNF fingerprint string

#### `calculate_dataset_unf(data, config=None)`

Calculate UNF for a complete dataset (multiple variables).

**Parameters:**
- `data`: Sequence of variables, where each variable is a sequence of values
- `config`: Optional `UNFConfig` instance

**Returns:** Dataset-level UNF fingerprint string

#### `combine_unfs(unfs, config=None)`

Combine multiple UNF fingerprints (order-independent).

**Parameters:**
- `unfs`: Sequence of UNF strings
- `config`: Optional `UNFConfig` instance

**Returns:** Combined UNF fingerprint string

### Normalization Functions

Individual normalization functions are available for specific use cases:

```python
from unf import (
    normalize_numeric,
    normalize_string,
    normalize_boolean,
    normalize_date,
    normalize_datetime,
)
```

## Development

This project uses `uv` for dependency management.

### Setup

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/yourusername/unf.git
cd unf

# Install dependencies
uv sync --dev
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=unf --cov-report=html

# Run specific test file
uv run pytest tests/test_unf.py -v
```

### Project Structure

```
unf/
  src/unf/
    __init__.py        # Public API
    unf.py             # Core UNF calculation
    normalize.py       # Data type normalization
  tests/
    test_unf.py        # UNF calculation tests
    test_normalize.py  # Normalization tests
  pyproject.toml       # Project configuration
  README.md
```

## Compatibility

This library is designed to be compatible with the Dataverse UNF implementation. While we strive for compatibility, please note:

- Only UNF version 6 is supported
- Default parameters match Dataverse defaults
- Timezone handling may differ for some data formats (this is expected behavior reflecting semantic differences)

## References

- [UNF v6 Specification](https://guides.dataverse.org/en/latest/developers/unf/unf-v6.html)
- [Original UNF Paper](https://www.mitpressjournals.org/doi/abs/10.1162/08989400360925386) by Micah Altman
- [Dataverse Project](https://dataverse.org/)

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
