"""Fixtures for MapMe tests."""

from __future__ import annotations

import json
from pathlib import Path

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def load_user_fixture() -> dict:
    """Load the sample user API response."""
    with (FIXTURES_DIR / "user_sample.json").open(encoding="utf-8") as file:
        return json.load(file)
