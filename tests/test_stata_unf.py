"""Test UNF calculation for Stata files against Dataverse reference values."""

import pandas as pd
from unf import calculate_unf, calculate_dataset_unf

# Expected values from Dataverse
EXPECTED_DATASET_UNF = "UNF:6:73FOyDaPCFxYO/zEkSHncw=="
EXPECTED_VARIABLE_UNFS = {
    "observationid": "UNF:6:xbAKHI/iMSs0zDNtkWWQLg==",
    "treatment": "UNF:6:RWcf2vRAjmUSJ/0XomvX7w==",
    "completion_state": "UNF:6:TQnqiqB21U1pgnr6ZJJQ+Q==",
    "start_date": "UNF:6:07QBeRufQcIfsfC10DU8lQ==",
    "duration_in_seconds": "UNF:6:TywpngXlSfNh3mQJ+LRlRA==",
    "wgt": "UNF:6:PYILaPsjS5hqF2dDKIYWfg==",
    "gender": "UNF:6:lld9J2nXVYmloSVGgo7YlQ==",
    "age": "UNF:6:HQa8FD5B4hAtmBupIp2j3w==",
    "state_fips": "UNF:6:keZwEy8wJ7e4+u4ftkMiAQ==",
    "region": "UNF:6:0tdeG7DBI0/0JkFDhVrWA==",
    "education": "UNF:6:29DLIc01cQOkFZrzcTwaEg==",
    "income": "UNF:6:T8QUBP15K62dz3tlSvH4JQ==",
    "luck_fair": "UNF:6:ByDgcDhXzZ+ZUpWKY+fHZw==",
    "talent_fair": "UNF:6:B4HfpjGCnBJA4cr3eEeD+w==",
    "effort_fair": "UNF:6:skZimeYrOpYSgrbGAvK4YA==",
    "luck_control": "UNF:6:nZFm3H6v10iKt8hAqQj5XQ==",
    "talent_control": "UNF:6:GoE9BbWLpC09klCSCl2GLQ==",
    "effort_control": "UNF:6:++HshktDRF6Jfkw==",
    "redist_pref": "UNF:6:TIRSzDS2LrQfVDw4QQXA5g==",
    "polpref": "UNF:6:fnsPXUvuvPqo2qxa67PhO5w==",
    "payment_low_worker": "UNF:6:pJQoJA0Pv7NmPLkrM131jA==",
    "payment_high_worker": "UNF:6:7PN0Cuv7pC2J5g3W2sY3Wg==",
}

def test_stata_file_unf():
    """Test that our library matches Dataverse UNF for Stata file."""
    # Read the Stata file
    df = pd.read_stata("tests/mmtalent_df.dta")

    print(f"\nDataset shape: {df.shape}")
    print(f"\nColumns: {list(df.columns)}")
    print(f"\nFirst few rows:")
    print(df.head())
    print(f"\nData types:")
    print(df.dtypes)

    # Calculate dataset UNF
    dataset_unf = calculate_dataset_unf(df)
    print(f"\n{'='*60}")
    print(f"Dataset UNF Comparison:")
    print(f"Expected: {EXPECTED_DATASET_UNF}")
    print(f"Actual:   {dataset_unf}")
    print(f"Match:    {dataset_unf == EXPECTED_DATASET_UNF}")

    # Calculate individual variable UNFs
    print(f"\n{'='*60}")
    print(f"Variable UNF Comparisons:")
    print(f"{'='*60}")

    mismatches = []
    for col in df.columns:
        expected = EXPECTED_VARIABLE_UNFS.get(col, "N/A")
        actual = calculate_unf(df[col].tolist())
        match = actual == expected

        print(f"\n{col}:")
        print(f"  Expected: {expected}")
        print(f"  Actual:   {actual}")
        print(f"  Match:    {match}")

        if not match and expected != "N/A":
            mismatches.append(col)
            # Print first few values for debugging
            print(f"  Sample values: {df[col].head(10).tolist()}")

    if mismatches:
        print(f"\n{'='*60}")
        print(f"MISMATCHES: {len(mismatches)} variables don't match")
        print(f"Variables: {', '.join(mismatches)}")
    else:
        print(f"\n{'='*60}")
        print(f"SUCCESS: All UNFs match!")

if __name__ == "__main__":
    test_stata_file_unf()
