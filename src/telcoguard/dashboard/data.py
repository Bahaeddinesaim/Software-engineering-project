"""Load local demonstration resources without exposing individual customer identifiers."""

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from telcoguard.data.validation import validate_dataset
from telcoguard.ml.inference import Predictor


@st.cache_data(show_spinner=False)
def load_dataset(path: str, modified: float) -> pd.DataFrame:
    """Cache validated, de-identified rows; invalidate when the source changes."""
    return validate_dataset(pd.read_csv(path)).drop(columns="customerID")


@st.cache_resource(show_spinner=False)
def load_predictor(path: str, modified: float) -> Predictor:
    """Cache an operator-controlled model and refresh it after retraining."""
    return Predictor(Path(path))


def read_report(path: Path) -> dict:
    """Read an optional JSON report without making the UI fail on missing files."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def contract_rates(frame: pd.DataFrame) -> pd.DataFrame:
    """Compute observed churn rates and counts in the selected cohort."""
    return (
        frame.assign(churn=frame.Churn.eq("Yes"))
        .groupby("Contract", observed=True)
        .agg(taux=("churn", "mean"), clients=("churn", "size"))
        .reset_index()
    )
