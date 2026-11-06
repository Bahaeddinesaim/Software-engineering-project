"""Run the required local quality gates and preserve their actual output."""

import json
import subprocess
import sys
from pathlib import Path

import yaml


def main() -> None:
    """Validate workflow structure and run each gate, failing if any gate fails."""
    output = Path("reports/checks")
    output.mkdir(parents=True, exist_ok=True)
    workflow = yaml.load(Path(".github/workflows/ci.yml").read_text(), Loader=yaml.BaseLoader)
    assert set(workflow["on"]) == {"push", "pull_request"}
    assert workflow["permissions"]["contents"] == "read"
    job = workflow["jobs"]["verify"]
    assert job["strategy"]["matrix"]["python"] == ["3.11", "3.12"]
    commands = [step["run"] for step in job["steps"] if "run" in step]
    assert any("--cov-fail-under=75" in command for command in commands)
    assert any("sphinx-build -W" in command for command in commands)
    assert "poetry build" in commands
    results = {
        "workflow_structure": {
            "status": "PASS",
            "scope": "YAML parsing and structural assertions; not a remote execution",
        }
    }
    checks = {
        "poetry_check": ["-m", "poetry", "check", "--lock", "--strict"],
        "ruff_check": ["-m", "ruff", "check", "."],
        "ruff_format": ["-m", "ruff", "format", "--check", "."],
        "pytest": ["-m", "pytest"],
        "poetry_build": ["-m", "poetry", "build"],
        "sphinx": ["-m", "sphinx", "-W", "-E", "-b", "html", "docs", "docs/_build/html"],
        "live_api": ["scripts/verify_live_api.py"],
    }
    for name, arguments in checks.items():
        process = subprocess.run(
            [sys.executable, *arguments],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        transcript = "\n".join(
            line.rstrip() for line in (process.stdout + process.stderr).splitlines()
        )
        (output / f"{name}.log").write_text(transcript + "\n", encoding="utf-8")
        results[name] = {
            "status": "PASS" if process.returncode == 0 else "FAIL",
            "exit_code": process.returncode,
        }
        print(f"{name}: {results[name]['status']}", flush=True)
    (output.parent / "checks.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    if any(result["status"] != "PASS" for result in results.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
