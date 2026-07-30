"""Data update coordinator for MapMe."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import MapMeApiClient, MapMeApiError
from .const import CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, DOMAIN
from .models import MapMeUserData

_LOGGER = logging.getLogger(__name__)


def get_scan_interval(entry: ConfigEntry) -> timedelta:
    """Return the scan interval for a config entry."""
    seconds = entry.options.get(
        CONF_SCAN_INTERVAL,
        entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
    )
    return timedelta(seconds=int(seconds))


class MapMeDataUpdateCoordinator(DataUpdateCoordinator[MapMeUserData]):
    """Coordinator that polls MapMe for a single user."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.config_entry = entry
        self.user_id: str = entry.data["user_id"]
        self._api = MapMeApiClient(async_get_clientsession(hass))

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{self.user_id}",
            update_interval=get_scan_interval(entry),
        )

    async def _async_update_data(self) -> MapMeUserData:
        """Fetch data from the MapMe API."""
        try:
            return await self._api.async_get_user(self.user_id)
        except MapMeApiError as err:
            raise UpdateFailed(str(err)) from err

    def update_scan_interval(self) -> None:
        """Apply the current config entry scan interval."""
        self.update_interval = get_scan_interval(self.config_entry)
