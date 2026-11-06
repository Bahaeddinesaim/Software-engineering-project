"""Reproducible training and trusted artifact persistence."""

import hashlib
import json
import platform
from datetime import UTC, datetime
from pathlib import Path

import joblib
import pandas as pd
import sklearn
from sklearn.dummy import DummyClassifier
from sklearn.model_selection import train_test_split

from telcoguard import __version__
from telcoguard.data.validation import CATEGORIES, FEATURES, NUMERIC, split_features_target
from telcoguard.ml.evaluation import evaluate
from telcoguard.ml.preprocessing import build_pipeline


def train(data_path: Path, output_dir: Path, seed: int = 42) -> dict:
    """Split first, fit only on training rows, evaluate and persist the complete pipeline."""
    features, target = split_features_target(pd.read_csv(data_path))
    x_train, x_test, y_train, y_test = train_test_split(
        features,
        target,
        test_size=0.2,
        random_state=seed,
        stratify=target,
    )
    pipeline = build_pipeline(seed)
    pipeline.fit(x_train, y_train)
    metrics = evaluate(y_test, pipeline.predict(x_test), pipeline.predict_proba(x_test)[:, 1])
    dummy = DummyClassifier(strategy="prior").fit(x_train, y_train)
    metadata = {
        "model_version": __version__,
        "trained_at": datetime.now(UTC).isoformat(),
        "python_version": platform.python_version(),
        "sklearn_version": sklearn.__version__,
        "dataset_sha256": hashlib.sha256(data_path.read_bytes()).hexdigest(),
        "configuration": {
            "seed": seed,
            "test_size": 0.2,
            "threshold": 0.5,
            "classifier": "LogisticRegression",
            "max_iter": 2000,
        },
        "features": FEATURES,
        "numeric": NUMERIC,
        "categories": CATEGORIES,
        "train_rows": len(x_train),
        "test_rows": len(x_test),
        "class_distribution": {str(k): int(v) for k, v in target.value_counts().items()},
        "metrics": metrics,
        "dummy_metrics": evaluate(y_test, dummy.predict(x_test), dummy.predict_proba(x_test)[:, 1]),
        "probability": "Uncalibrated logistic regression estimate; not a causal guarantee",
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    artifact = {"pipeline": pipeline, "metadata": metadata}
    temporary = output_dir / "pipeline.tmp"
    joblib.dump(artifact, temporary)
    temporary.replace(output_dir / "pipeline.joblib")
    (output_dir / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return metadata
