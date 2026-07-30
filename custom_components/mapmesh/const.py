"""Constants for the MapMe integration."""

DOMAIN = "mapmesh"

CONF_USER_ID = "user_id"
CONF_NAME = "name"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_USERS = "users"

DEFAULT_SCAN_INTERVAL = 900

API_BASE_URL = "https://mapme.sh/api/user"

SENSOR_PROFILE = "profile"
SENSOR_RANK = "rank"
SENSOR_POINTS = "points"
SENSOR_TOTAL_SAMPLES = "total_samples"
SENSOR_UNIQUE_HEXES = "unique_hexes"
SENSOR_PIONEER_HEXES = "pioneer_hexes"
SENSOR_ACTIVE_DAYS = "active_days"
SENSOR_UNIQUE_REPEATERS = "unique_repeaters"

CORE_SENSORS = (
    SENSOR_RANK,
    SENSOR_POINTS,
    SENSOR_TOTAL_SAMPLES,
    SENSOR_UNIQUE_HEXES,
    SENSOR_PIONEER_HEXES,
    SENSOR_ACTIVE_DAYS,
    SENSOR_UNIQUE_REPEATERS,
)
