"""The MapMe integration."""

from __future__ import annotations

import logging
from pathlib import Path

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import CONF_NAME, CONF_SCAN_INTERVAL, CONF_USERS, CONF_USER_ID, DEFAULT_SCAN_INTERVAL, DOMAIN
from .coordinator import MapMeDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]

YAML_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): cv.positive_int,
        vol.Required(CONF_USERS): vol.All(
            cv.ensure_list,
            [
                vol.Schema(
                    {
                        vol.Required(CONF_USER_ID): cv.string,
                        vol.Optional(CONF_NAME): cv.string,
                        vol.Optional(CONF_SCAN_INTERVAL): cv.positive_int,
                    }
                )
            ],
        ),
    }
)

CARD_URL = "/mapmesh/mapmesh-card.js"


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up MapMe from YAML."""
    if DOMAIN not in config:
        return True

    hass.data.setdefault(DOMAIN, {})
    yaml_config = YAML_SCHEMA(config[DOMAIN])
    default_interval = yaml_config[CONF_SCAN_INTERVAL]
    seen: set[str] = set()

    for user_cfg in yaml_config[CONF_USERS]:
        user_id = user_cfg[CONF_USER_ID].strip()
        if user_id in seen:
            _LOGGER.error("Duplicate user_id in mapmesh YAML: %s", user_id)
            continue
        seen.add(user_id)

        entry_data: dict = {CONF_USER_ID: user_id}
        if CONF_NAME in user_cfg:
            entry_data[CONF_NAME] = user_cfg[CONF_NAME]
        scan_interval = user_cfg.get(CONF_SCAN_INTERVAL, default_interval)
        entry_data[CONF_SCAN_INTERVAL] = int(scan_interval)

        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN,
                context={"source": config_entries.SOURCE_IMPORT},
                data=entry_data,
            )
        )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up MapMe from a config entry."""
    coordinator = MapMeDataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    await _register_lovelace_resource(hass)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    coordinator: MapMeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    coordinator.update_scan_interval()
    await coordinator.async_request_refresh()


async def _register_lovelace_resource(hass: HomeAssistant) -> None:
    """Register the Lovelace card resource once."""
    domain_data = hass.data.setdefault(DOMAIN, {})
    if domain_data.get("lovelace_registered"):
        return

    card_path = Path(__file__).parent / "www" / "mapmesh-card.js"
    if not card_path.is_file():
        _LOGGER.warning("MapMe Lovelace card not found at %s", card_path)
        return

    hass.http.register_static_path(CARD_URL, str(card_path))

    if "lovelace" not in hass.data:
        domain_data["lovelace_registered"] = True
        return

    lovelace_data = hass.data["lovelace"]
    resources = lovelace_data.resources
    if resources is None:
        domain_data["lovelace_registered"] = True
        return

    if not resources.loaded:
        await resources.async_get_info()

    if not any(item.get("url", "").startswith(CARD_URL) for item in resources.async_items()):
        await resources.async_create_item({"res_type": "module", "url": CARD_URL})

    domain_data["lovelace_registered"] = True
