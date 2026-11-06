"""REST contract, security, model lifecycle and safe failures."""

from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from telcoguard.api.main import create_app
from telcoguard.config import Settings

HEADERS = {"X-API-Key": "t" * 40}


def test_success(settings, record):
    with TestClient(create_app(settings)) as client:
        assert client.get("/health").json() == {"status": "healthy", "model_loaded": True}
        response = client.post("/predict", json=record, headers=HEADERS)
        assert response.status_code == 200
        assert 0 <= response.json()["churn_probability"] <= 1
        assert client.get("/docs").status_code == 200
        assert "APIKeyHeader" in client.get("/openapi.json").json()["components"]["securitySchemes"]
        record["TotalCharges"] = None
        assert client.post("/predict", json=record, headers=HEADERS).status_code == 200


@pytest.mark.parametrize("headers", [{}, {"X-API-Key": "bad"}])
def test_auth(settings, record, headers):
    with TestClient(create_app(settings)) as client:
        assert client.post("/predict", json=record, headers=headers).status_code == 401


@pytest.mark.parametrize(
    "updates",
    [
        {"tenure": -1},
        {"tenure": "12"},
        {"gender": "other"},
        {"MonthlyCharges": -3},
        {"extra": "secret"},
        {"TotalCharges": ""},
        {"SeniorCitizen": 9},
    ],
)
def test_invalid(settings, record, updates):
    with TestClient(create_app(settings)) as client:
        response = client.post("/predict", json=record | updates, headers=HEADERS)
        assert response.status_code == 422
        assert "secret" not in response.text


def test_empty(settings):
    with TestClient(create_app(settings)) as client:
        assert client.post("/predict", json={}, headers=HEADERS).status_code == 422


def test_missing_model(settings, record, tmp_path):
    settings.model_path = tmp_path / "missing.joblib"
    with TestClient(create_app(settings)) as client:
        assert client.get("/health").status_code == 503
        assert client.get("/health").json()["model_loaded"] is False
        assert client.post("/predict", json=record, headers=HEADERS).status_code == 503


def test_no_auth_configuration(record, tmp_path):
    settings = Settings(_env_file=None, api_key=None, model_path=tmp_path / "missing")
    with TestClient(create_app(settings)) as client:
        assert client.get("/health").status_code == 503
        assert client.post("/predict", json=record, headers=HEADERS).status_code == 503


def test_controlled_error(settings, record, caplog):
    app = create_app(settings)
    with TestClient(app) as client:
        app.state.predictor = Mock(predict=Mock(side_effect=RuntimeError("sensitive")))
        response = client.post("/predict", json=record, headers=HEADERS)
        assert response.status_code == 500 and response.json()["detail"] == "Prediction failed"
    assert "sensitive" not in caplog.text and HEADERS["X-API-Key"] not in caplog.text
