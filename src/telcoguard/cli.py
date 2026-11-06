"""Command-line entry point for reproducible data and model operations."""

import argparse
import json
import logging
from pathlib import Path

import pandas as pd

from telcoguard.data.loader import download_data
from telcoguard.data.validation import validate_dataset
from telcoguard.ml.training import train


def main() -> None:
    """Dispatch acquisition, preparation, EDA and training commands."""
    parser = argparse.ArgumentParser(description="TelcoGuard data and ML pipeline")
    parser.add_argument("command", choices=["download", "prepare", "eda", "train"])
    parser.add_argument("--data", type=Path, default=Path("data/raw/telco.csv"))
    parser.add_argument("--output", type=Path, default=Path("models"))
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    if args.command == "download":
        download_data(args.data, force=args.force)
    elif args.command == "train":
        print(json.dumps(train(args.data, args.output), indent=2))
    else:
        frame = validate_dataset(pd.read_csv(args.data))
        args.output.mkdir(parents=True, exist_ok=True)
        if args.command == "prepare":
            frame.drop(columns="customerID").to_csv(args.output / "cleaned.csv", index=False)
        else:
            report = {
                "rows": len(frame),
                "columns": len(frame.columns),
                "missing": frame.isna().sum().to_dict(),
                "class_counts": frame.Churn.value_counts().to_dict(),
                "numeric_summary": frame.describe().to_dict(),
            }
            (args.output / "eda.json").write_text(json.dumps(report, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
