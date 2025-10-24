# UNF Comparison Table

Comparison of UNF calculations across Python, R, and Dataverse for `mmtalent_df.dta`

## Methodology

- **Python**: Uses `pyreadstat` with `apply_value_formats=False` to preserve numeric codes
- **R**: Uses `haven::read_dta()` with `as.numeric()` conversion for labeled variables
- **Dataverse**: Published UNF values from https://dataverse.harvard.edu/

## Results Table

| Variable | Type | Missing | Python vs R | Python vs Dataverse |
|----------|------|---------|-------------|--------------------|
| observationid | integer | 0 | ✗ | ✗ |
| treatment | labeled[4] | 1702 | ✓ | ✓ |
| completion_state | labeled[5] | 0 | ✓ | ✓ |
| start_date | string | 0 | ✓ | ✓ |
| duration_in_seconds | float | 1796 | ✗ | ✗ |
| wgt | float | 1796 | ✓ | ✓ |
| gender | labeled[2] | 97 | ✓ | ✓ |
| age | string | 97 | ✗ | ✗ |
| state_fips | string | 99 | ✗ | ✗ |
| region | string | 0 | ✓ | ✗ |
| education | labeled[8] | 97 | ✓ | ✓ |
| income | labeled[5] | 97 | ✓ | ✓ |
| luck_fair | string | 1745 | ✗ | ✗ |
| talent_fair | string | 1745 | ✗ | ✗ |
| effort_fair | string | 1745 | ✗ | ✗ |
| luck_control | string | 1775 | ✗ | ✗ |
| talent_control | string | 1775 | ✗ | ✗ |
| effort_control | string | 1775 | ✗ | ✗ |
| redist_pref | labeled[5] | 1787 | ✓ | ✓ |
| polpref | labeled[5] | 1796 | ✓ | ✗ |
| payment_low_worker | string | 1702 | ✓ | ✓ |
| payment_high_worker | string | 1702 | ✓ | ✓ |

## Summary

- **Python vs R (as numeric)**: 12/22 matches (54.5%)
- **Python vs Dataverse**: 10/22 matches (45.5%)
