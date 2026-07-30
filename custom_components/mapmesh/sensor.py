"""Sensor platform for MapMe."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_NAME,
    CORE_SENSORS,
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
from .coordinator import MapMeDataUpdateCoordinator
from .models import MapMeUserData, profile_attributes

SENSOR_DEFINITIONS: dict[str, dict[str, str | None]] = {
    SENSOR_PROFILE: {
        "translation_key": "profile",
        "state_class": None,
        "icon": "mdi:account",
    },
    SENSOR_RANK: {
        "translation_key": "rank",
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:podium",
    },
    SENSOR_POINTS: {
        "translation_key": "points",
        "state_class": SensorStateClass.TOTAL,
        "icon": "mdi:star",
    },
    SENSOR_TOTAL_SAMPLES: {
        "translation_key": "total_samples",
        "state_class": SensorStateClass.TOTAL,
        "icon": "mdi:chart-line",
    },
    SENSOR_UNIQUE_HEXES: {
        "translation_key": "unique_hexes",
        "state_class": SensorStateClass.TOTAL,
        "icon": "mdi:hexagon-multiple",
    },
    SENSOR_PIONEER_HEXES: {
        "translation_key": "pioneer_hexes",
        "state_class": SensorStateClass.TOTAL,
        "icon": "mdi:rocket-launch",
    },
    SENSOR_ACTIVE_DAYS: {
        "translation_key": "active_days",
        "state_class": SensorStateClass.TOTAL,
        "icon": "mdi:calendar-check",
    },
    SENSOR_UNIQUE_REPEATERS: {
        "translation_key": "unique_repeaters",
        "state_class": SensorStateClass.TOTAL,
        "icon": "mdi:radio-tower",
    },
}


def _metric_value(data: MapMeUserData, sensor_key: str) -> int:
    return {
        SENSOR_RANK: data.rank,
        SENSOR_POINTS: data.points,
        SENSOR_TOTAL_SAMPLES: data.total_samples,
        SENSOR_UNIQUE_HEXES: data.unique_hexes,
        SENSOR_PIONEER_HEXES: data.pioneer_hexes,
        SENSOR_ACTIVE_DAYS: data.active_days,
        SENSOR_UNIQUE_REPEATERS: data.unique_repeaters,
    }[sensor_key]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up MapMe sensors from a config entry."""
    coordinator: MapMeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[MapMeSensor] = [
        MapMeSensor(coordinator, entry, SENSOR_PROFILE),
    ]
    entities.extend(
        MapMeSensor(coordinator, entry, sensor_key) for sensor_key in CORE_SENSORS
    )
    async_add_entities(entities)


class MapMeSensor(CoordinatorEntity[MapMeDataUpdateCoordinator], SensorEntity):
    """Representation of a MapMe sensor."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self,
        coordinator: MapMeDataUpdateCoordinator,
        entry: ConfigEntry,
        sensor_key: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._sensor_key = sensor_key
        definition = SENSOR_DEFINITIONS[sensor_key]

        self._attr_translation_key = definition["translation_key"]
        self._attr_unique_id = f"{entry.data['user_id']}_{sensor_key}"
        self._attr_icon = definition["icon"]
        state_class = definition["state_class"]
        if state_class is not None:
            self._attr_state_class = state_class

        display_name = entry.data.get(CONF_NAME) or (
            coordinator.data.name if coordinator.data else entry.data["user_id"][:8]
        )
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.data["user_id"])},
            name=display_name,
            manufacturer="MapMe",
            model=coordinator.data.hardware if coordinator.data else "MapMe User",
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if self.coordinator.data:
            self._attr_device_info = DeviceInfo(
                identifiers={(DOMAIN, self._entry.data["user_id"])},
                name=self._entry.data.get(CONF_NAME) or self.coordinator.data.name,
                manufacturer="MapMe",
                model=self.coordinator.data.hardware,
            )
        self.async_write_ha_state()

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None
        if self._sensor_key == SENSOR_PROFILE:
            return self.coordinator.data.points
        return _metric_value(self.coordinator.data, self._sensor_key)

    @property
    def extra_state_attributes(self) -> dict | None:
        """Return profile attributes for the card."""
        if self._sensor_key != SENSOR_PROFILE or not self.coordinator.data:
            return None
        return profile_attributes(self.coordinator.data)
