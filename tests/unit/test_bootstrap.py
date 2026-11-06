"""Fresh-deployment setup and protection of existing artifacts."""

from unittest.mock import Mock

import pytest

from telcoguard.dashboard.bootstrap import prepare_demo


def test_existing_files_are_preserved(tmp_path, monkeypatch):
    data = tmp_path / "telco.csv"
    model = tmp_path / "pipeline.joblib"
    data.write_text("existing data")
    model.write_text("existing artifact")
    download = Mock()
    training = Mock()
    monkeypatch.setattr("telcoguard.dashboard.bootstrap.download_data", download)
    monkeypatch.setattr("telcoguard.dashboard.bootstrap.train", training)
    prepare_demo(data, model)
    download.assert_not_called()
    training.assert_not_called()
    assert model.read_text() == "existing artifact"


def test_custom_model_is_not_generated(tmp_path, monkeypatch):
    data = tmp_path / "telco.csv"
    data.touch()
    prepare_demo(data, None)
    with pytest.raises(ValueError, match="default"):
        prepare_demo(data, tmp_path / "custom.joblib")
