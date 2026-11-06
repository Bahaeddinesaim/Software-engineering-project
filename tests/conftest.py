"""Deterministic miniature fixtures; never used as the delivered training dataset."""

import pandas as pd
import pytest

from telcoguard.config import Settings
from telcoguard.data.validation import CATEGORIES
from telcoguard.ml.training import train


@pytest.fixture
def frame():
    """Generate diverse test-only rows without network or customer information."""
    records = []
    for i in range(80):
        record = {name: values[i % len(values)] for name, values in CATEGORIES.items()}
        record.update(
            customerID=f"test-{i}",
            SeniorCitizen=i % 2,
            tenure=i % 73,
            MonthlyCharges=20.0 + i,
            TotalCharges=" " if i == 0 else str(i * 50.0),
            Churn="Yes" if i % 3 == 0 else "No",
        )
        records.append(record)
    return pd.DataFrame(records)


@pytest.fixture
def model_dir(frame, tmp_path):
    """Train a small genuine estimator on isolated test fixtures."""
    path = tmp_path / "test.csv"
    frame.to_csv(path, index=False)
    train(path, tmp_path / "models")
    return tmp_path / "models"


@pytest.fixture
def settings(model_dir):
    return Settings(_env_file=None, api_key="t" * 40, model_path=model_dir / "pipeline.joblib")


@pytest.fixture
def record(frame):
    return frame.drop(columns=["customerID", "Churn"]).iloc[1].to_dict() | {"TotalCharges": 50.0}
