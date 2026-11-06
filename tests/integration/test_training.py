"""Dataset-to-artifact round trip and reproducibility."""

import json

import joblib
import numpy as np
import pytest
from sklearn.model_selection import train_test_split

from telcoguard.data.validation import FEATURES, NUMERIC, split_features_target
from telcoguard.ml.inference import Predictor
from telcoguard.ml.training import train


def test_roundtrip_reproducibility(frame, tmp_path, model_dir, record):
    metadata = json.loads((model_dir / "metadata.json").read_text())
    assert metadata["train_rows"] == 64 and metadata["test_rows"] == 16
    assert metadata["features"] == FEATURES
    assert metadata["metrics"]["roc_auc"] >= 0
    first = Predictor(model_dir / "pipeline.joblib").predict(record)
    path = tmp_path / "repeat.csv"
    frame.to_csv(path, index=False)
    second_meta = train(path, tmp_path / "repeat")
    second = Predictor(tmp_path / "repeat/pipeline.joblib").predict(record)
    assert first == second and metadata["metrics"] == second_meta["metrics"]
    pipeline = joblib.load(model_dir / "pipeline.joblib")["pipeline"]
    median = (
        pipeline.named_steps["preprocess"]
        .named_transformers_["numeric"]
        .named_steps["imputer"]
        .statistics_
    )
    features, target = split_features_target(frame)
    x_train, _, _, _ = train_test_split(
        features, target, test_size=0.2, random_state=42, stratify=target
    )
    np.testing.assert_allclose(median, x_train[NUMERIC].median().to_numpy())


def test_invalid_artifact(model_dir):
    path = model_dir / "pipeline.joblib"
    artifact = joblib.load(path)
    artifact["metadata"]["features"] = []
    joblib.dump(artifact, path)
    with pytest.raises(ValueError, match="schema"):
        Predictor(path)


def test_invalid_pipeline(model_dir):
    path = model_dir / "pipeline.joblib"
    artifact = joblib.load(path)
    artifact["pipeline"] = "not a pipeline"
    joblib.dump(artifact, path)
    with pytest.raises(ValueError, match="Pipeline"):
        Predictor(path)
