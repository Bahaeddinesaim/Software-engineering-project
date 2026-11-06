"""Prepare a de-identified dataset without learned transformations."""

from pathlib import Path

import pandas as pd

from telcoguard.data.validation import validate_dataset

if __name__ == "__main__":
    output = Path("data/processed/cleaned.csv")
    output.parent.mkdir(parents=True, exist_ok=True)
    validate_dataset(pd.read_csv("data/raw/telco.csv")).drop(columns="customerID").to_csv(
        output, index=False
    )
