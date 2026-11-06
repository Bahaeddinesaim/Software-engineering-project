"""Prepare the academic demo from real IBM data on a fresh deployment."""

from pathlib import Path
from threading import Lock

from telcoguard.data.loader import download_data
from telcoguard.ml.training import train

_setup_lock = Lock()


def prepare_demo(data_path: Path, model_path: Path | None) -> None:
    """Create missing resources once per server; never overwrite an existing model."""
    with _setup_lock:
        if not data_path.exists():
            download_data(data_path)
        if model_path is not None and not model_path.exists():
            if model_path.name != "pipeline.joblib":
                raise ValueError("Automatic setup requires the default pipeline.joblib filename")
            train(data_path, model_path.parent)
