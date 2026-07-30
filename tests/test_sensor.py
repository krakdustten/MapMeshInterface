"""Tests for MapMe sensors."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from custom_components.mapmesh.const import (
    CONF_USER_ID,
    DOMAIN,
    SENSOR_ACTIVE_DAYS,
    SENSOR_PIONEER_HEXES,
    SENSOR_POINTS,
    SENSOR_PROFILE,
    SENSOR_RANK,
    SENSOR_TOTAL_SAMPLES,
    SENSOR_UNIQUE_HEXES,
    SENSOR_UNIQUE_REPEATERS,
)
from custom_components.mapmesh.models import parse_user_response
from tests.conftest import load_user_fixture

USER_ID = "2577e905519e6071f776f32bc3d371a7b27b7c18cbd80462a7e64ef07319ac47"


@pytest.fixture
async def setup_integration(hass: HomeAssistant) -> ConfigEntry:
    """Set up the MapMe integration."""
    user_data = parse_user_response(load_user_fixture())
    with patch(
        "custom_components.mapmesh.coordinator.MapMeApiClient.async_get_user",
        AsyncMock(return_value=user_data),
    ):
        entry = ConfigEntry(
            version=1,
            domain=DOMAIN,
            title="Dylan G",
            data={CONF_USER_ID: USER_ID},
            source="user",
            entry_id="test_entry",
            unique_id=USER_ID,
        )
        entry.add_to_hass(hass)
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        return entry


@pytest.mark.asyncio
async def test_profile_sensor(hass: HomeAssistant, setup_integration: ConfigEntry) -> None:
    """Test profile sensor state and attributes."""
    state = hass.states.get(f"sensor.dylan_g_{SENSOR_PROFILE}")
    assert state is not None
    assert state.state == "53847"
    assert state.attributes["name"] == "Dylan G"
    assert state.attributes["rank"] == 54
    assert len(state.attributes["badges"]) == 5


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("entity_suffix", "expected"),
    [
        (SENSOR_RANK, "54"),
        (SENSOR_POINTS, "53847"),
        (SENSOR_TOTAL_SAMPLES, "51462"),
        (SENSOR_UNIQUE_HEXES, "7675"),
        (SENSOR_PIONEER_HEXES, "2981"),
        (SENSOR_ACTIVE_DAYS, "88"),
        (SENSOR_UNIQUE_REPEATERS, "189"),
    ],
)
async def test_metric_sensors(
    hass: HomeAssistant,
    setup_integration: ConfigEntry,
    entity_suffix: str,
    expected: str,
) -> None:
    """Test core metric sensors."""
    state = hass.states.get(f"sensor.dylan_g_{entity_suffix}")
    assert state is not None
    assert state.state == expected
