"""Tests for MapMe YAML setup."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.core import HomeAssistant

from custom_components.mapmesh import async_setup
from custom_components.mapmesh.const import CONF_NAME, CONF_SCAN_INTERVAL, CONF_USER_ID, DOMAIN
from tests.conftest import load_user_fixture

USER_ID = "2577e905519e6071f776f32bc3d371a7b27b7c18cbd80462a7e64ef07319ac47"
OTHER_USER_ID = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"


@pytest.mark.asyncio
async def test_yaml_import_single_user(hass: HomeAssistant) -> None:
    """Test YAML imports a user via config flow."""
    hass.data[DOMAIN] = {}
    with patch(
        "custom_components.mapmesh.config_flow.validate_user",
        AsyncMock(return_value={CONF_USER_ID: USER_ID, CONF_NAME: "Dylan G"}),
    ):
        assert await async_setup(
            hass,
            {
                DOMAIN: {
                    CONF_SCAN_INTERVAL: 900,
                    "users": [
                        {
                            CONF_USER_ID: USER_ID,
                            CONF_NAME: "Dylan",
                            CONF_SCAN_INTERVAL: 600,
                        }
                    ],
                }
            },
        )
        await hass.async_block_till_done()

        entries = hass.config_entries.async_entries(DOMAIN)
        assert len(entries) == 1
        assert entries[0].data[CONF_USER_ID] == USER_ID
        assert entries[0].data[CONF_SCAN_INTERVAL] == 600


@pytest.mark.asyncio
async def test_yaml_import_multiple_users(hass: HomeAssistant) -> None:
    """Test YAML imports multiple users."""
    hass.data[DOMAIN] = {}
    with patch(
        "custom_components.mapmesh.config_flow.validate_user",
        AsyncMock(
            side_effect=[
                {CONF_USER_ID: USER_ID, CONF_NAME: "Dylan G"},
                {CONF_USER_ID: OTHER_USER_ID, CONF_NAME: "Other"},
            ]
        ),
    ):
        assert await async_setup(
            hass,
            {
                DOMAIN: {
                    "users": [
                        {CONF_USER_ID: USER_ID},
                        {CONF_USER_ID: OTHER_USER_ID},
                    ]
                }
            },
        )
        await hass.async_block_till_done()

        entries = hass.config_entries.async_entries(DOMAIN)
        assert len(entries) == 2


@pytest.mark.asyncio
async def test_yaml_import_skips_duplicate(hass: HomeAssistant) -> None:
    """Test YAML duplicate user_id is skipped on second import attempt."""
    hass.data[DOMAIN] = {}
    with patch(
        "custom_components.mapmesh.config_flow.validate_user",
        AsyncMock(return_value={CONF_USER_ID: USER_ID, CONF_NAME: "Dylan G"}),
    ):
        yaml_config = {
            DOMAIN: {
                "users": [
                    {CONF_USER_ID: USER_ID},
                    {CONF_USER_ID: USER_ID},
                ]
            }
        }
        assert await async_setup(hass, yaml_config)
        await hass.async_block_till_done()

        entries = hass.config_entries.async_entries(DOMAIN)
        assert len(entries) == 1
