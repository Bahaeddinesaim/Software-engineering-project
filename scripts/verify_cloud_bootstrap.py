"""Verify real-data startup in a temporary directory with no deployed artifacts."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from telcoguard.dashboard.bootstrap import prepare_demo
from telcoguard.dashboard.data import load_dataset
from telcoguard.ml.inference import Predictor


def main() -> None:
    """Download the IBM CSV, train, reload and infer from an initially empty directory."""
    with TemporaryDirectory(prefix="telcoguard-cloud-") as temporary:
        root = Path(temporary)
        data = root / "data/raw/telco.csv"
        model = root / "models/pipeline.joblib"
        prepare_demo(data, model)
        predictor = Predictor(model)
        frame = load_dataset(str(data), data.stat().st_mtime)
        record = json.loads(Path("examples/customer.json").read_text())
        result = predictor.predict(record)
        modified = model.stat().st_mtime_ns
        prepare_demo(data, model)
        assert model.stat().st_mtime_ns == modified
        report = {
            "status": "PASS",
            "rows": len(frame),
            "features_and_target": len(frame.columns),
            "model_preserved_on_second_run": True,
            "prediction": result,
            "dataset_sha256": predictor.metadata["dataset_sha256"],
            "scope": "Local empty-directory startup, not remote Cloud execution",
        }
        Path("reports/cloud-bootstrap.json").write_text(json.dumps(report, indent=2))
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
