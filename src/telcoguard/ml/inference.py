"""Trusted local artifact loading and response formatting."""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.utils.validation import check_is_fitted

from telcoguard.data.validation import FEATURES


class Predictor:
    """Load only operator-controlled joblib files; never accept uploaded artifacts."""

    def __init__(self, path: Path):
        artifact = joblib.load(path)
        self.pipeline = artifact["pipeline"]
        self.metadata = artifact["metadata"]
        if self.metadata["features"] != FEATURES:
            raise ValueError("Incompatible artifact feature schema")
        if not isinstance(self.pipeline, Pipeline):
            raise ValueError("Artifact must contain a fitted sklearn Pipeline")
        check_is_fitted(self.pipeline)
        if list(self.pipeline.feature_names_in_) != FEATURES:
            raise ValueError("Incompatible fitted pipeline feature schema")
        if list(self.pipeline.classes_) != [0, 1]:
            raise ValueError("Artifact must predict binary classes [0, 1]")

    def predict(self, record: dict, threshold: float = 0.5) -> dict:
        """Predict churn with fixed illustrative operational risk thresholds."""
        normalized = {name: np.nan if value is None else value for name, value in record.items()}
        frame = pd.DataFrame([normalized], columns=FEATURES)
        probability = float(self.pipeline.predict_proba(frame)[0, 1])
        if not np.isfinite(probability) or not 0 <= probability <= 1:
            raise ValueError("Invalid model probability")
        prediction = int(probability >= threshold)
        return {
            "prediction": prediction,
            "churn_label": "Yes" if prediction else "No",
            "churn_probability": probability,
            "risk_level": "high"
            if probability >= 0.7
            else "medium"
            if probability >= 0.3
            else "low",
            "model_version": self.metadata["model_version"],
        }
