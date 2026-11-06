"""CLI dispatch with isolated paths and real local data."""

import json
import sys
from unittest.mock import Mock

import pytest

from telcoguard.cli import main


@pytest.mark.parametrize("command", ["prepare", "eda", "train"])
def test_local_commands(frame, tmp_path, monkeypatch, command):
    path = tmp_path / "input.csv"
    frame.to_csv(path, index=False)
    output = tmp_path / "output"
    monkeypatch.setattr(
        sys, "argv", ["telcoguard", command, "--data", str(path), "--output", str(output)]
    )
    main()
    if command == "prepare":
        assert "customerID" not in (output / "cleaned.csv").read_text()
    elif command == "eda":
        assert json.loads((output / "eda.json").read_text())["rows"] == 80
    else:
        assert (output / "pipeline.joblib").exists()


def test_download_command(tmp_path, monkeypatch):
    download = Mock()
    monkeypatch.setattr("telcoguard.cli.download_data", download)
    monkeypatch.setattr(sys, "argv", ["telcoguard", "download", "--force"])
    main()
    assert download.call_args.kwargs == {"force": True}
