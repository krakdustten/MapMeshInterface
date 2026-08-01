"""Packaging sanity tests."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
COMPONENT = ROOT / "custom_components" / "mapmesh"


def test_manifest_valid() -> None:
    """Test manifest.json has required fields."""
    manifest = json.loads((COMPONENT / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["domain"] == "mapmesh"
    assert manifest["config_flow"] is True
    assert manifest["iot_class"] == "cloud_polling"


def test_hacs_json_valid() -> None:
    """Test hacs.json is valid."""
    hacs = json.loads((ROOT / "hacs.json").read_text(encoding="utf-8"))
    assert hacs["name"] == "MapMe"
    assert hacs["filename"] == "mapmesh"
    assert hacs["content_in_root"] is False


def test_card_file_exists() -> None:
    """Test Lovelace card files exist."""
    assert (COMPONENT / "www" / "mapmesh-card.js").is_file()
    assert (COMPONENT / "www" / "mapmesh-card-logic.js").is_file()
