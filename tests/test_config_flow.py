"""Tests for MapMe config flow."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.mapmesh.const import CONF_NAME, CONF_SCAN_INTERVAL, CONF_USER_ID, DOMAIN
from tests.conftest import load_user_fixture

USER_ID = "2577e905519e6071f776f32bc3d371a7b27b7c18cbd80462a7e64ef07319ac47"
OTHER_USER_ID = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"


@pytest.mark.asyncio
async def test_config_flow_user_success(hass: HomeAssistant) -> None:
    """Test successful config flow."""
    with patch(
        "custom_components.mapmesh.config_flow.validate_user",
        AsyncMock(return_value={CONF_USER_ID: USER_ID, CONF_NAME: "Dylan G"}),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        assert result["type"] == FlowResultType.FORM

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_USER_ID: USER_ID}
        )
        assert result["type"] == FlowResultType.CREATE_ENTRY
        assert result["title"] == "Dylan G"
        assert result["data"][CONF_USER_ID] == USER_ID


@pytest.mark.asyncio
async def test_config_flow_invalid_user(hass: HomeAssistant) -> None:
    """Test invalid user error."""
    from custom_components.mapmesh.config_flow import InvalidUser

    with patch(
        "custom_components.mapmesh.config_flow.validate_user",
        AsyncMock(side_effect=InvalidUser()),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_USER_ID: "bad"}
        )
        assert result["type"] == FlowResultType.FORM
        assert result["errors"]["base"] == "invalid_user"


@pytest.mark.asyncio
async def test_config_flow_duplicate_user(hass: HomeAssistant) -> None:
    """Test duplicate user abort."""
    with patch(
        "custom_components.mapmesh.config_flow.validate_user",
        AsyncMock(return_value={CONF_USER_ID: USER_ID, CONF_NAME: "Dylan G"}),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_USER_ID: USER_ID}
        )
        assert result["type"] == FlowResultType.CREATE_ENTRY

        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_USER_ID: USER_ID}
        )
        assert result["type"] == FlowResultType.ABORT
        assert result["reason"] == "already_configured"


@pytest.mark.asyncio
async def test_config_flow_second_distinct_user(hass: HomeAssistant) -> None:
    """Test adding a second distinct user succeeds."""
    with patch(
        "custom_components.mapmesh.config_flow.validate_user",
        AsyncMock(
            side_effect=[
                {CONF_USER_ID: USER_ID, CONF_NAME: "Dylan G"},
                {CONF_USER_ID: OTHER_USER_ID, CONF_NAME: "Other User"},
            ]
        ),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_USER_ID: USER_ID}
        )
        assert result["type"] == FlowResultType.CREATE_ENTRY

        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_USER_ID: OTHER_USER_ID}
        )
        assert result["type"] == FlowResultType.CREATE_ENTRY
        assert result["data"][CONF_USER_ID] == OTHER_USER_ID


@pytest.mark.asyncio
async def test_config_flow_import(hass: HomeAssistant) -> None:
    """Test YAML import flow."""
    with patch(
        "custom_components.mapmesh.config_flow.validate_user",
        AsyncMock(return_value={CONF_USER_ID: USER_ID, CONF_NAME: "Dylan G"}),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_IMPORT},
            data={CONF_USER_ID: USER_ID, CONF_SCAN_INTERVAL: 600},
        )
        assert result["type"] == FlowResultType.CREATE_ENTRY
        assert result["data"][CONF_SCAN_INTERVAL] == 600
