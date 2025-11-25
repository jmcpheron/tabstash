"""Pytest configuration and shared fixtures."""

from pathlib import Path

import pytest


@pytest.fixture
def fixtures_dir() -> Path:
    """Return the path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def tabs_fixtures_dir(fixtures_dir: Path) -> Path:
    """Return the path to tab fixtures directory."""
    return fixtures_dir / "tabs"
