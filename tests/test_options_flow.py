"""Tests for MapMe options flow."""

from __future__ import annotations

from datetime import timedelta
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.mapmesh.const import CONF_SCAN_INTERVAL, CONF_USER_ID, DOMAIN
from custom_components.mapmesh.coordinator import get_scan_interval
from custom_components.mapmesh.models import parse_user_response
from tests.conftest import load_user_fixture

USER_ID = "2577e905519e6071f776f32bc3d371a7b27b7c18cbd80462a7e64ef07319ac47"
OTHER_USER_ID = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"


@pytest.mark.asyncio
async def test_options_flow_updates_interval(hass: HomeAssistant) -> None:
    """Test options flow updates scan interval for one entry."""
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
            entry_id="entry_a",
            unique_id=USER_ID,
        )
        entry.add_to_hass(hass)
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        result = await hass.config_entries.options.async_init(entry.entry_id)
        result = await hass.config_entries.options.async_configure(
            result["flow_id"], {CONF_SCAN_INTERVAL: 300}
        )
        assert result["type"] == FlowResultType.CREATE_ENTRY

        updated = hass.config_entries.async_get_entry(entry.entry_id)
        assert updated is not None
        assert updated.options[CONF_SCAN_INTERVAL] == 300
        coordinator = hass.data[DOMAIN][entry.entry_id]
        assert get_scan_interval(updated) == timedelta(seconds=300)
        assert coordinator.update_interval == timedelta(seconds=300)


@pytest.mark.asyncio
async def test_options_flow_only_affects_target_entry(hass: HomeAssistant) -> None:
    """Test changing one entry's interval does not affect another."""
    user_data = parse_user_response(load_user_fixture())
    with patch(
        "custom_components.mapmesh.coordinator.MapMeApiClient.async_get_user",
        AsyncMock(return_value=user_data),
    ):
        entry_a = ConfigEntry(
            version=1,
            domain=DOMAIN,
            title="Dylan G",
            data={CONF_USER_ID: USER_ID, CONF_SCAN_INTERVAL: 900},
            source="user",
            entry_id="entry_a",
            unique_id=USER_ID,
        )
        entry_b = ConfigEntry(
            version=1,
            domain=DOMAIN,
            title="Other",
            data={CONF_USER_ID: OTHER_USER_ID, CONF_SCAN_INTERVAL: 900},
            source="user",
            entry_id="entry_b",
            unique_id=OTHER_USER_ID,
        )
        entry_a.add_to_hass(hass)
        entry_b.add_to_hass(hass)
        await hass.config_entries.async_setup(entry_a.entry_id)
        await hass.config_entries.async_setup(entry_b.entry_id)
        await hass.async_block_till_done()

        result = await hass.config_entries.options.async_init(entry_a.entry_id)
        await hass.config_entries.options.async_configure(
            result["flow_id"], {CONF_SCAN_INTERVAL: 120}
        )
        await hass.async_block_till_done()

        coordinator_a = hass.data[DOMAIN][entry_a.entry_id]
        coordinator_b = hass.data[DOMAIN][entry_b.entry_id]
        assert coordinator_a.update_interval == timedelta(seconds=120)
        assert coordinator_b.update_interval == timedelta(seconds=900)
