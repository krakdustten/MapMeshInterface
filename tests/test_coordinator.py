"""Tests for MapMe coordinator."""

from __future__ import annotations

from datetime import timedelta
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.mapmesh.const import CONF_SCAN_INTERVAL, CONF_USER_ID, DOMAIN
from custom_components.mapmesh.coordinator import MapMeDataUpdateCoordinator, get_scan_interval
from custom_components.mapmesh.models import parse_user_response
from tests.conftest import load_user_fixture

USER_ID = "2577e905519e6071f776f32bc3d371a7b27b7c18cbd80462a7e64ef07319ac47"


@pytest.fixture
def config_entry(hass: HomeAssistant) -> ConfigEntry:
    """Create a config entry."""
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
    return entry


def test_get_scan_interval_default(config_entry: ConfigEntry) -> None:
    """Test default scan interval."""
    assert get_scan_interval(config_entry) == timedelta(seconds=900)


def test_get_scan_interval_from_data(config_entry: ConfigEntry) -> None:
    """Test scan interval from entry data."""
    config_entry.data = {CONF_USER_ID: USER_ID, CONF_SCAN_INTERVAL: 300}
    assert get_scan_interval(config_entry) == timedelta(seconds=300)


def test_get_scan_interval_from_options(config_entry: ConfigEntry) -> None:
    """Test scan interval from options overrides data."""
    config_entry.data = {CONF_USER_ID: USER_ID, CONF_SCAN_INTERVAL: 300}
    config_entry.options = {CONF_SCAN_INTERVAL: 120}
    assert get_scan_interval(config_entry) == timedelta(seconds=120)


@pytest.mark.asyncio
async def test_coordinator_update_success(
    hass: HomeAssistant, config_entry: ConfigEntry
) -> None:
    """Test coordinator fetches data."""
    user_data = parse_user_response(load_user_fixture())
    with patch(
        "custom_components.mapmesh.coordinator.MapMeApiClient.async_get_user",
        AsyncMock(return_value=user_data),
    ):
        coordinator = MapMeDataUpdateCoordinator(hass, config_entry)
        await coordinator.async_config_entry_first_refresh()
        assert coordinator.data is not None
        assert coordinator.data.points == 53847


@pytest.mark.asyncio
async def test_coordinator_update_failed(
    hass: HomeAssistant, config_entry: ConfigEntry
) -> None:
    """Test coordinator handles API errors."""
    from custom_components.mapmesh.api import MapMeApiError

    with patch(
        "custom_components.mapmesh.coordinator.MapMeApiClient.async_get_user",
        AsyncMock(side_effect=MapMeApiError("boom")),
    ):
        coordinator = MapMeDataUpdateCoordinator(hass, config_entry)
        with pytest.raises(UpdateFailed):
            await coordinator.async_config_entry_first_refresh()
