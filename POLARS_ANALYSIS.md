# Polars vs Pandas for UNF Calculation

## Executive Summary

**Yes, using polars instead of pandas could eliminate the need for the NaN → None "hack"**, but with an important caveat: polars preserves the semantic distinction between `null` (missing data) and `NaN` (undefined floating-point value).

## Key Findings

### 1. Polars Automatically Converts NaN to None When Reading Data

When reading Stata files via `pyreadstat` → pandas → polars conversion:
- Pandas represents missing values as `NaN` (IEEE 754 floating-point special value)
- Polars **automatically converts these to `None`** during `pl.from_pandas()` conversion
- The resulting `to_list()` contains proper Python `None` objects

**Test Results:**
```python
# Reading mmtalent_df.dta
df_pandas, meta = pyreadstat.read_dta('tests/mmtalent_df.dta', apply_value_formats=False)
df_polars = pl.from_pandas(df_pandas)

# At missing value positions:
pandas_list[14] = nan           # Python float NaN
polars_list[14] = None          # Python None object
```

Both produce identical UNF values that match R reference implementation: `UNF:6:PYILaPsjS5hqF2dDKIYWfg==`

### 2. Polars Maintains NaN vs Null Distinction

Polars distinguishes between:
- **`null`**: True missing data (represented as Python `None`)
- **`NaN`**: IEEE 754 "Not a Number" floating-point value

```python
s_none = pl.Series('test', [1.0, 2.0, None, 4.0])
s_nan = pl.Series('test', [1.0, 2.0, float('nan'), 4.0])

s_none.to_list()  # [1.0, 2.0, None, 4.0]
s_nan.to_list()   # [1.0, 2.0, nan, 4.0]  # NaN is preserved!
```

### 3. Internal Representation Difference

**Pandas:**
- Uses in-band encoding: NaN is a special bit pattern within the data array
- Only works for float types
- Cannot distinguish between missing and NaN

**Polars:**
- Uses out-of-band encoding: separate validity bitmask
- Works for all data types (integers, strings, dates, etc.)
- Maintains clear separation: null ≠ NaN

## Implications for UNF Library

### Current Implementation (with NaN hack)

```python
# In calculate_unf() function (src/unf/unf.py:155-168)
for value in data:
    if isinstance(value, float):
        import math
        if math.isnan(value):
            cleaned_data.append(None)  # Convert NaN → None
        else:
            cleaned_data.append(value)
    else:
        cleaned_data.append(value)
```

### With Polars (no hack needed)

If users pass polars Series/DataFrame data:
```python
# Polars automatically provides None for missing values
polars_list = df_polars['column'].to_list()
unf = calculate_unf(polars_list)  # Works correctly without NaN hack
```

### The Caveat: Direct NaN Input

If a user explicitly creates data with `float('nan')` instead of `None`:
```python
data = [1.0, 2.0, float('nan'), 4.0]  # Direct list, no polars
```

This would **still need the NaN hack** because:
1. Polars only converts NaN → None during `from_pandas()` or file reading operations
2. Direct Python lists with NaN values remain as NaN
3. The UNF spec requires missing values to be encoded as null (`\x00\x00\x00`), not as `+nan`

## Recommendations

### Option 1: Keep Current Approach (Recommended)
- Maintain the NaN → None conversion in `calculate_unf()`
- Works with any input (pandas, polars, plain lists, numpy)
- Ensures correct UNF calculation regardless of data source
- Simple and robust

### Option 2: Add Polars-Specific Functions
Create polars-aware functions that leverage polars' proper null handling:

```python
def calculate_unf_from_polars(series: pl.Series, config=None):
    """Calculate UNF from polars Series (no NaN hack needed)."""
    return calculate_unf(series.to_list(), config)

def calculate_unf_from_polars_dataframe(df: pl.DataFrame, config=None):
    """Calculate UNFs for all columns in polars DataFrame."""
    return {col: calculate_unf(df[col].to_list(), config) for col in df.columns}
```

Benefits:
- Documents that polars handles nulls correctly
- Potentially better performance (if polars operations are added)
- Clear semantic distinction between null and NaN

### Option 3: Switch Internal Processing to Polars
Use polars for all internal file reading and data processing:

```python
def calculate_unf_from_stata(filepath, config=None):
    # Read with pyreadstat, convert to polars immediately
    df_pandas, meta = pyreadstat.read_dta(filepath, apply_value_formats=False)
    df_polars = pl.from_pandas(df_pandas)

    # Process using polars (NaN → None happens automatically)
    return {col: calculate_unf(df_polars[col].to_list(), config)
            for col in df_polars.columns}
```

Benefits:
- Automatic null handling
- Better performance for large datasets
- Type safety (polars has stricter typing than pandas)
- Support for more data types (polars handles integers with nulls)

Drawbacks:
- Adds polars as a required dependency (currently optional)
- Users might prefer pandas (more common in data science)
- Need to maintain compatibility with pandas ecosystem

## Performance Considerations

Polars is generally faster than pandas for:
- Large dataset operations
- File reading (parquet, CSV)
- Aggregations and transformations

For UNF calculation specifically:
- Most time is spent in normalization and hashing
- Data format conversion overhead is minimal
- Performance difference likely negligible for typical use cases

## Conclusion

**Should you switch to polars?**

For the **core UNF library**: **No, keep the current NaN → None hack**
- It's simple, explicit, and works with all input types
- No additional dependencies required
- Users can provide data from any source

For **optional integrations**: **Yes, add polars support**
- Create `calculate_unf_from_polars()` convenience functions
- Document that polars handles nulls correctly
- Make polars an optional dependency like pandas

For **internal file processing**: **Consider it for future**
- If performance becomes an issue
- If you need better integer/null handling
- If you want to support more file formats efficiently

The NaN hack is actually a feature, not a bug—it ensures correctness regardless of input source. Polars just happens to do the same conversion automatically when reading from pandas or files.

## References

- [Polars Missing Data Documentation](https://docs.pola.rs/user-guide/expressions/missing-data/)
- [NaN vs Null in pandas & Polars](https://www.dontusethiscode.com/blog/2025-01-08_null_vs_nan.html)
- Polars uses Apache Arrow's null representation (separate validity bitmask)
- Pandas inherits NumPy's NaN-based missing value encoding

## Test Evidence

All tests conducted with:
- Polars 1.34.0
- Pandas (via pyreadstat)
- Test file: `tests/mmtalent_df.dta` (3,797 observations, 22 variables)
- Variable `wgt`: 1,796 missing values

Results: ✅ Both pandas and polars produce identical UNF values matching R reference implementation.
