"""Regression tests for root and standalone test-collection contracts."""

import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _offline_environment() -> dict[str, str]:
    """Keep collection checks deterministic and free of provider credentials."""
    environment = os.environ.copy()
    for name in (
        "GOOGLE_API_KEY",
        "OPENAI_API_KEY",
        "OPENAI_ACCESS_TOKEN",
        "ANTHROPIC_API_KEY",
    ):
        environment.pop(name, None)
    return environment


def test_root_collection_accepts_strict_markers() -> None:
    """Every marker used by root tests must be declared before strict collection."""
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests",
            "--collect-only",
            "-q",
            "-o",
            "addopts=",
            "-p",
            "no:cacheprovider",
            "--no-cov",
            "--strict-markers",
        ],
        cwd=PROJECT_ROOT,
        env=_offline_environment(),
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Unknown pytest.mark" not in result.stdout + result.stderr


def test_helper_support_classes_are_not_collected_as_tests() -> None:
    """Pydantic/data-access helpers must not trigger pytest class collection warnings."""
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/session/memory/test_json_stability.py",
            "tests/unit/test_accessors_registry.py",
            "--collect-only",
            "-q",
            "-o",
            "addopts=",
            "-p",
            "no:cacheprovider",
            "--no-cov",
            "-W",
            "error::pytest.PytestCollectionWarning",
        ],
        cwd=PROJECT_ROOT,
        env=_offline_environment(),
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "PytestCollectionWarning" not in result.stdout + result.stderr
