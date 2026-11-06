"""Preprocessing, configuration and probability semantics."""

from unittest.mock import Mock

import numpy as np
import pytest
from pydantic import ValidationError

from telcoguard.config import Settings
from telcoguard.data.validation import split_features_target
from telcoguard.ml.inference import Predictor
from telcoguard.ml.preprocessing import build_pipeline


def test_preprocess_missing_unknown(frame):
    x, y = split_features_target(frame)
    pipeline = build_pipeline().fit(x, y)
    x.loc[0, "gender"] = "unseen"
    assert np.isfinite(pipeline.predict_proba(x)).all()
    assert pipeline.named_steps["preprocess"].transform(x).shape[0] == 80


@pytest.mark.parametrize(
    "value,risk,prediction",
    [(0.2, "low", 0), (0.3, "medium", 0), (0.5, "medium", 1), (0.7, "high", 1)],
)
def test_format(model_dir, record, value, risk, prediction):
    predictor = Predictor(model_dir / "pipeline.joblib")
    predictor.pipeline = Mock(predict_proba=Mock(return_value=np.array([[1 - value, value]])))
    result = predictor.predict(record)
    assert result["risk_level"] == risk and result["prediction"] == prediction


def test_invalid_probability(model_dir, record):
    predictor = Predictor(model_dir / "pipeline.joblib")
    predictor.pipeline = Mock(predict_proba=Mock(return_value=np.array([[0, np.nan]])))
    with pytest.raises(ValueError):
        predictor.predict(record)


def test_settings(monkeypatch):
    monkeypatch.setenv("TELCOGUARD_API_KEY", "a" * 40)
    settings = Settings(_env_file=None)
    assert settings.api_key.get_secret_value() == "a" * 40
    assert "a" * 40 not in repr(settings)
    with pytest.raises(ValidationError) as error:
        Settings(api_key="short", _env_file=None)
    assert "short" not in str(error.value)
    with pytest.raises(ValidationError):
        Settings(threshold=1, _env_file=None)
