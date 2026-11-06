"""Validate the actual IBM schema and perform non-learning cleanup."""

import numpy as np
import pandas as pd

NUMERIC = ["SeniorCitizen", "tenure", "MonthlyCharges", "TotalCharges"]
CATEGORIES = {
    "gender": ["Female", "Male"],
    "Partner": ["Yes", "No"],
    "Dependents": ["Yes", "No"],
    "PhoneService": ["Yes", "No"],
    "MultipleLines": ["Yes", "No", "No phone service"],
    "InternetService": ["DSL", "Fiber optic", "No"],
    **{
        name: ["Yes", "No", "No internet service"]
        for name in [
            "OnlineSecurity",
            "OnlineBackup",
            "DeviceProtection",
            "TechSupport",
            "StreamingTV",
            "StreamingMovies",
        ]
    },
    "Contract": ["Month-to-month", "One year", "Two year"],
    "PaperlessBilling": ["Yes", "No"],
    "PaymentMethod": [
        "Electronic check",
        "Mailed check",
        "Bank transfer (automatic)",
        "Credit card (automatic)",
    ],
}
FEATURES = list(CATEGORIES) + NUMERIC
COLUMNS = ["customerID", *FEATURES, "Churn"]


def validate_dataset(frame: pd.DataFrame) -> pd.DataFrame:
    """Reject schema drift and malformed values; preserve missing predictors for imputation."""
    if set(frame.columns) != set(COLUMNS) or len(frame.columns) != len(COLUMNS):
        raise ValueError("Dataset must contain exactly the 21 IBM columns")
    if frame.empty:
        raise ValueError("Dataset is empty")
    clean = frame.copy()
    for column in clean.select_dtypes(include=["object", "string"]).columns:
        empty = clean[column].map(lambda value: isinstance(value, str) and not value.strip())
        clean.loc[empty, column] = np.nan
    clean = clean.drop_duplicates()
    if clean.customerID.isna().any() or clean.customerID.duplicated().any():
        raise ValueError("Missing or conflicting customer identifiers")
    if clean.Churn.isna().any() or not clean.Churn.isin(["Yes", "No"]).all():
        raise ValueError("Invalid Churn target")
    for column, allowed in CATEGORIES.items():
        if not clean[column].dropna().isin(allowed).all():
            raise ValueError(f"Unexpected category in {column}")
    for column in NUMERIC:
        clean[column] = pd.to_numeric(clean[column], errors="raise").astype(float)
        values = clean[column].dropna()
        if not np.isfinite(values).all() or (values < 0).any():
            raise ValueError(f"Invalid numeric values in {column}")
    if not clean.SeniorCitizen.dropna().isin([0, 1]).all():
        raise ValueError("SeniorCitizen must be binary")
    if (clean.tenure.dropna() % 1 != 0).any():
        raise ValueError("tenure must contain whole months")
    return clean


def split_features_target(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Drop identifiers and encode the binary target without learning statistics."""
    clean = validate_dataset(frame)
    return clean[FEATURES], clean.Churn.map({"No": 0, "Yes": 1})
