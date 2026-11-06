"""Schema, cleaning and download behavior."""

from unittest.mock import Mock

import httpx
import numpy as np
import pandas as pd
import pytest

from telcoguard.data.loader import download_data
from telcoguard.data.validation import FEATURES, split_features_target, validate_dataset


def test_clean_and_encode(frame):
    clean = validate_dataset(pd.concat([frame, frame.iloc[[0]]]))
    assert len(clean) == 80
    assert np.isnan(clean.iloc[0].TotalCharges)
    x, y = split_features_target(frame)
    assert list(x) == FEATURES and "customerID" not in x and "Churn" not in x
    assert set(y) == {0, 1}


@pytest.mark.parametrize(
    "column,value",
    [
        ("Churn", "Maybe"),
        ("Churn", None),
        ("gender", "unknown"),
        ("MonthlyCharges", "oops"),
        ("tenure", -1),
        ("tenure", 1.5),
        ("TotalCharges", float("inf")),
        ("SeniorCitizen", 2),
        ("customerID", None),
    ],
)
def test_invalid_values(frame, column, value):
    frame[column] = frame[column].astype(object)
    frame.loc[0, column] = value
    with pytest.raises((ValueError, TypeError)):
        validate_dataset(frame)


def test_missing_schema_empty_and_conflicting_ids(frame):
    for invalid in [frame.drop(columns="Churn"), frame.iloc[:0], frame.assign(customerID="same")]:
        with pytest.raises(ValueError):
            validate_dataset(invalid)


def test_download_cache_retry(frame, tmp_path, monkeypatch):
    response = httpx.Response(
        200,
        content=frame.to_csv(index=False).encode(),
        request=httpx.Request("GET", "https://example.com"),
    )
    get = Mock(side_effect=[httpx.ConnectError("offline"), response])
    monkeypatch.setattr("telcoguard.data.loader.httpx.get", get)
    monkeypatch.setattr("telcoguard.data.loader.time.sleep", lambda _: None)
    path = tmp_path / "raw.csv"
    assert download_data(path) == path
    assert path.with_suffix(".source.json").exists()
    download_data(path)
    assert get.call_count == 2
    get.side_effect = httpx.ConnectError("offline")
    with pytest.raises(RuntimeError, match="3 attempts"):
        download_data(path, force=True)
    assert path.exists()


def test_download_rejects_bad_schema(tmp_path, monkeypatch):
    response = httpx.Response(200, text="bad\n1", request=httpx.Request("GET", "https://x.test"))
    monkeypatch.setattr("telcoguard.data.loader.httpx.get", lambda *a, **k: response)
    with pytest.raises(ValueError):
        download_data(tmp_path / "bad.csv")
    assert not (tmp_path / "bad.csv").exists()
