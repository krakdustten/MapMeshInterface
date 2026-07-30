"""Tests for MapMe models."""

from custom_components.mapmesh.models import parse_user_response, profile_attributes
from tests.conftest import load_user_fixture


def test_parse_user_response() -> None:
    """Test parsing API response."""
    data = parse_user_response(load_user_fixture())

    assert data.pubkey == "2577e905519e6071f776f32bc3d371a7b27b7c18cbd80462a7e64ef07319ac47"
    assert data.name == "Dylan G"
    assert data.rank == 54
    assert data.points == 53847
    assert data.total_samples == 51462
    assert data.unique_hexes == 7675
    assert data.pioneer_hexes == 2981
    assert data.active_days == 88
    assert data.unique_repeaters == 189
    assert data.road_trip_peak == 1423
    assert data.grinder_peak == 2519
    assert len(data.badges) == 5


def test_profile_attributes_contract() -> None:
    """Test profile attributes include card contract fields."""
    data = parse_user_response(load_user_fixture())
    attrs = profile_attributes(data)

    assert attrs["name"] == "Dylan G"
    assert attrs["hardware"] == "Heltec V3v1.14.1-467959c"
    assert attrs["rank"] == 54
    assert attrs["points"] == 53847
    assert attrs["total_samples"] == 51462
    assert attrs["unique_hexes"] == 7675
    assert attrs["rx_hexes"] == 683
    assert attrs["active_days"] == 88
    assert attrs["unique_repeaters"] == 189
    assert attrs["pioneer_hexes"] == 2981
    assert attrs["days_since_first"] == 118
    assert attrs["road_trip_peak"] == 1423
    assert attrs["grinder_peak"] == 2519
    assert len(attrs["badges"]) == 5
    assert attrs["badges"][0]["id"] == "trailblazer"
    assert attrs["badges"][0]["color"] == "#fbbf24"
