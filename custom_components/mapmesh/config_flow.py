"""Config flow for MapMe."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import MapMeApiClient, MapMeApiError, MapMeNotFoundError
from .const import (
    CONF_NAME,
    CONF_SCAN_INTERVAL,
    CONF_USER_ID,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USER_ID): str,
        vol.Optional(CONF_NAME): str,
    }
)

OPTIONS_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
            int, vol.Range(min=60, max=86400)
        ),
    }
)


async def validate_user(hass: HomeAssistant, user_id: str) -> dict[str, Any]:
    """Validate user_id by fetching from the API."""
    client = MapMeApiClient(async_get_clientsession(hass))
    try:
        data = await client.async_get_user(user_id.strip())
    except MapMeNotFoundError as err:
        raise InvalidUser from err
    except MapMeApiError as err:
        raise CannotConnect from err
    return {
        CONF_USER_ID: data.pubkey,
        CONF_NAME: data.name,
    }


class MapMeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for MapMe."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            user_id = user_input[CONF_USER_ID].strip()
            await self.async_set_unique_id(user_id)
            self._abort_if_unique_id_configured()

            try:
                info = await validate_user(self.hass, user_id)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidUser:
                errors["base"] = "invalid_user"
            else:
                return self._create_entry(info, user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_import(self, user_input: dict[str, Any]) -> ConfigFlowResult:
        """Handle import from YAML."""
        user_id = user_input[CONF_USER_ID].strip()
        await self.async_set_unique_id(user_id)
        self._abort_if_unique_id_configured()

        try:
            info = await validate_user(self.hass, user_id)
        except CannotConnect:
            return self.async_abort(reason="cannot_connect")
        except InvalidUser:
            return self.async_abort(reason="invalid_user")

        if CONF_NAME not in user_input and info.get(CONF_NAME):
            user_input = {**user_input, CONF_NAME: info[CONF_NAME]}

        return self._create_entry(info, user_input)

    def _create_entry(
        self, info: dict[str, Any], user_input: dict[str, Any]
    ) -> ConfigFlowResult:
        """Create a config entry from validated input."""
        entry_data: dict[str, Any] = {CONF_USER_ID: info[CONF_USER_ID]}
        if user_input.get(CONF_NAME):
            entry_data[CONF_NAME] = user_input[CONF_NAME]
        elif info.get(CONF_NAME):
            entry_data[CONF_NAME] = info[CONF_NAME]

        if CONF_SCAN_INTERVAL in user_input:
            entry_data[CONF_SCAN_INTERVAL] = int(user_input[CONF_SCAN_INTERVAL])

        title = entry_data.get(CONF_NAME, info[CONF_USER_ID][:8])
        return self.async_create_entry(title=title, data=entry_data)

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> MapMeOptionsFlow:
        """Get the options flow."""
        return MapMeOptionsFlow(config_entry)


class MapMeOptionsFlow(config_entries.OptionsFlow):
    """Handle options for MapMe."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = self.config_entry.options.get(
            CONF_SCAN_INTERVAL,
            self.config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        )

        schema = vol.Schema(
            {
                vol.Required(CONF_SCAN_INTERVAL, default=current): vol.All(
                    int, vol.Range(min=60, max=86400)
                ),
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidUser(HomeAssistantError):
    """Error to indicate the user is invalid."""
