"""Exercise the Streamlit demonstration with isolated deterministic resources."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from telcoguard.dashboard import app

ENTRY = str(Path(__file__).resolve().parents[2] / "streamlit_app.py")


@pytest.fixture
def dashboard(frame, model_dir, monkeypatch):
    root = model_dir.parent
    raw = root / "data/raw"
    raw.mkdir(parents=True)
    frame.to_csv(raw / "telco.csv", index=False)
    monkeypatch.setattr(app, "ROOT", root)
    monkeypatch.delenv("TELCOGUARD_MODEL_PATH", raising=False)
    return AppTest.from_file(ENTRY, default_timeout=30)


def test_dashboard_navigation_and_prediction(dashboard):
    dashboard.run()
    assert not dashboard.exception
    dashboard.button[0].click().run()
    assert dashboard.radio[0].value == "Simulateur"
    assert not dashboard.exception
    dashboard.button[0].click().run()
    assert not dashboard.exception
    result = dashboard.session_state["prediction_result"]["result"]
    assert 0 <= result["churn_probability"] <= 1
    dashboard.selectbox[0].select("Client fidèle").run()
    assert "prediction_result" not in dashboard.session_state
    assert dashboard.number_input[0].value == 60
    dashboard.button[0].click().run()
    assert not dashboard.exception
    dashboard.radio[0].set_value("Le modèle").run()
    assert not dashboard.exception


def test_explorer_and_empty_selection(dashboard):
    dashboard.run()
    dashboard.radio[0].set_value("Explorer les données").run()
    assert not dashboard.exception
    dashboard.multiselect[0].set_value([]).run()
    assert not dashboard.exception
    assert any("Aucun profil" in element.value for element in dashboard.info)


def test_missing_dashboard_resources(tmp_path, monkeypatch):
    monkeypatch.setattr(app, "ROOT", tmp_path)
    monkeypatch.setenv("TELCOGUARD_AUTO_SETUP", "false")
    dashboard = AppTest.from_file(ENTRY, default_timeout=30).run()
    assert not dashboard.exception
    assert dashboard.info
    for page in app.NAVIGATION[1:]:
        dashboard.radio[0].set_value(page).run()
        assert not dashboard.exception


def test_fresh_dashboard_initializes_itself(frame, tmp_path, monkeypatch):
    monkeypatch.setattr(app, "ROOT", tmp_path)
    monkeypatch.setenv("TELCOGUARD_AUTO_SETUP", "true")
    monkeypatch.setenv("TELCOGUARD_API_KEY", "")

    def local_download(path):
        path.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(path, index=False)
        return path

    monkeypatch.setattr("telcoguard.dashboard.bootstrap.download_data", local_download)
    dashboard = AppTest.from_file(ENTRY, default_timeout=30).run()
    assert not dashboard.exception
    assert (tmp_path / "models/pipeline.joblib").exists()
    dashboard.button[0].click().run()
    dashboard.button[0].click().run()
    assert not dashboard.exception
    assert 0 <= dashboard.session_state["prediction_result"]["result"]["churn_probability"] <= 1


def test_dashboard_initialization_error(tmp_path, monkeypatch):
    monkeypatch.setattr(app, "ROOT", tmp_path)
    monkeypatch.setenv("TELCOGUARD_AUTO_SETUP", "true")

    def unavailable(*args):
        raise RuntimeError("offline")

    monkeypatch.setattr(app, "prepare_demo", unavailable)
    dashboard = AppTest.from_file(ENTRY, default_timeout=30).run()
    assert not dashboard.exception
    assert dashboard.error and "préparation automatique" in dashboard.error[0].value
