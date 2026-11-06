"""Leakage-safe preprocessing fitted inside the training pipeline."""

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from telcoguard.data.validation import CATEGORIES, NUMERIC


def build_pipeline(seed: int = 42) -> Pipeline:
    """Construct an unfitted logistic regression with numeric and categorical transforms."""
    numeric = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median", keep_empty_features=True)),
            ("scale", StandardScaler()),
        ]
    )
    categorical = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent", keep_empty_features=True)),
            ("encode", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    transform = ColumnTransformer(
        [
            ("numeric", numeric, NUMERIC),
            ("categorical", categorical, list(CATEGORIES)),
        ]
    )
    return Pipeline(
        [
            ("preprocess", transform),
            ("classifier", LogisticRegression(max_iter=2000, random_state=seed)),
        ]
    )
