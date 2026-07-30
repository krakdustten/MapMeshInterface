"""Tests for MapMe API client."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest
from aiohttp import ClientResponseError
from aiohttp.client_reqrep import RequestInfo
from multidict import CIMultiDict, CIMultiDictProxy
from yarl import URL

from custom_components.mapmesh.api import MapMeApiClient, MapMeApiError, MapMeNotFoundError
from tests.conftest import load_user_fixture

USER_ID = "2577e905519e6071f776f32bc3d371a7b27b7c18cbd80462a7e64ef07319ac47"


async def _async_get_user_success() -> None:
    """Test successful API fetch."""
    response = AsyncMock()
    response.status = 200
    response.json = AsyncMock(return_value=load_user_fixture())
    response.raise_for_status = AsyncMock()

    session = MagicMock()
    context = MagicMock()
    context.__aenter__ = AsyncMock(return_value=response)
    context.__aexit__ = AsyncMock(return_value=None)
    session.get.return_value = context

    client = MapMeApiClient(session)
    data = await client.async_get_user(USER_ID)

    assert data.name == "Dylan G"
    assert data.points == 53847


def test_async_get_user_success() -> None:
    """Test successful API fetch."""
    asyncio.run(_async_get_user_success())


async def _async_get_user_not_found() -> None:
    """Test 404 response."""
    response = AsyncMock()
    response.status = 404

    session = MagicMock()
    context = MagicMock()
    context.__aenter__ = AsyncMock(return_value=response)
    context.__aexit__ = AsyncMock(return_value=None)
    session.get.return_value = context

    client = MapMeApiClient(session)
    with pytest.raises(MapMeNotFoundError):
        await client.async_get_user(USER_ID)


def test_async_get_user_not_found() -> None:
    """Test 404 response."""
    asyncio.run(_async_get_user_not_found())


async def _async_get_user_connection_error() -> None:
    """Test connection errors."""
    session = MagicMock()
    session.get.side_effect = ClientResponseError(
        RequestInfo(URL("https://mapme.sh"), "GET", CIMultiDictProxy(CIMultiDict())),
        (),
        status=500,
    )

    client = MapMeApiClient(session)
    with pytest.raises(MapMeApiError):
        await client.async_get_user(USER_ID)


def test_async_get_user_connection_error() -> None:
    """Test connection errors."""
    asyncio.run(_async_get_user_connection_error())
