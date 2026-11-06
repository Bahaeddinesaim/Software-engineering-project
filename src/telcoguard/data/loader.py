"""Bounded, validated acquisition of the public IBM CSV."""

import hashlib
import io
import json
import logging
import time
from pathlib import Path

import httpx
import pandas as pd

from telcoguard.data.validation import validate_dataset

SOURCE_URL = (
    "https://raw.githubusercontent.com/IBM/"
    "telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv"
)
logger = logging.getLogger(__name__)


def download_data(path: Path, *, force: bool = False) -> Path:
    """Download with three attempts; validate before replacing a local file."""
    if path.exists() and not force:
        validate_dataset(pd.read_csv(path))
        logger.info("dataset_cached")
        return path
    for attempt in range(3):
        try:
            response = httpx.get(SOURCE_URL, timeout=30, follow_redirects=True)
            response.raise_for_status()
            break
        except httpx.HTTPError as exc:
            if attempt == 2:
                raise RuntimeError("IBM dataset download failed after 3 attempts") from exc
            time.sleep(2**attempt)
    content = response.content
    frame = pd.read_csv(io.BytesIO(content))
    validate_dataset(frame)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_bytes(content)
    temporary.replace(path)
    path.with_suffix(".source.json").write_text(
        json.dumps(
            {
                "url": SOURCE_URL,
                "sha256": hashlib.sha256(content).hexdigest(),
                "rows": len(frame),
                "columns": list(frame.columns),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    logger.info("dataset_downloaded rows=%d columns=%d", *frame.shape)
    return path
