"""Verify a real Uvicorn subprocess using an ephemeral secret and local port."""

import json
import os
import secrets
import socket
import subprocess
import sys
import time
from pathlib import Path

import httpx


def main() -> None:
    """Exercise HTTP startup and prediction, then stop only the created process."""
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    secret = secrets.token_urlsafe(32)
    environment = os.environ.copy()
    environment["TELCOGUARD_API_KEY"] = secret
    output = Path("reports")
    output.mkdir(exist_ok=True)
    with (output / "uvicorn.log").open("w", encoding="utf-8") as log:
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "telcoguard.api.main:app",
                "--host",
                "127.0.0.1",
                "--port",
                str(port),
            ],
            env=environment,
            stdout=log,
            stderr=log,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        try:
            with httpx.Client(base_url=f"http://127.0.0.1:{port}", timeout=5) as client:
                for _ in range(100):
                    if process.poll() is not None:
                        raise RuntimeError(
                            "Uvicorn stopped before readiness; inspect reports/uvicorn.log"
                        )
                    try:
                        health = client.get("/health")
                        if health.status_code == 200:
                            break
                    except httpx.HTTPError:
                        pass
                    time.sleep(0.1)
                else:
                    raise RuntimeError("Uvicorn did not become ready")
                record = json.loads(Path("examples/customer.json").read_text())
                prediction = client.post("/predict", json=record, headers={"X-API-Key": secret})
                missing_key = client.post("/predict", json=record)
                wrong_key = client.post("/predict", json=record, headers={"X-API-Key": "bad"})
                invalid = client.post(
                    "/predict", json=record | {"tenure": -1}, headers={"X-API-Key": secret}
                )
                swagger = client.get("/docs")
                schema = client.get("/openapi.json")
                statuses = {
                    "health": health.status_code,
                    "predict": prediction.status_code,
                    "missing_key": missing_key.status_code,
                    "wrong_key": wrong_key.status_code,
                    "invalid_payload": invalid.status_code,
                    "swagger": swagger.status_code,
                    "openapi": schema.status_code,
                }
                assert statuses == {
                    "health": 200,
                    "predict": 200,
                    "missing_key": 401,
                    "wrong_key": 401,
                    "invalid_payload": 422,
                    "swagger": 200,
                    "openapi": 200,
                }, statuses
                (output / "live_api.json").write_text(json.dumps(statuses, indent=2))
                (output / "example_prediction.json").write_text(
                    json.dumps(prediction.json(), indent=2)
                )
                print(json.dumps(statuses))
        finally:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


if __name__ == "__main__":
    main()
