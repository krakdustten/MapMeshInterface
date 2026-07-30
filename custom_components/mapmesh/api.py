"""MapMe API client."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp

from .const import API_BASE_URL
from .models import MapMeUserData, parse_user_response

_LOGGER = logging.getLogger(__name__)


class MapMeApiError(Exception):
    """Base exception for MapMe API errors."""


class MapMeNotFoundError(MapMeApiError):
    """Raised when a user is not found."""


class MapMeApiClient:
    """Thin async client for the MapMe user API."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        """Initialize the client."""
        self._session = session

    async def async_get_user(self, user_id: str) -> MapMeUserData:
        """Fetch and parse a user profile."""
        url = f"{API_BASE_URL}/{user_id}"
        try:
            async with self._session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 404:
                    raise MapMeNotFoundError(f"User not found: {user_id}")
                response.raise_for_status()
                data: dict[str, Any] = await response.json()
        except aiohttp.ClientError as err:
            raise MapMeApiError(f"Error fetching user {user_id}: {err}") from err

        return parse_user_response(data)
