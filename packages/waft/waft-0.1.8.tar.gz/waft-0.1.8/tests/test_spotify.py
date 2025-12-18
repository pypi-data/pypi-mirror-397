"""Unit tests for the functions in src/waft/spotify.py."""

from unittest.mock import Mock, patch

import pytest  # type: ignore
import requests  # type: ignore

from waft.datatypes import DisplayedTrack  # type: ignore
from waft.datatypes import Album, Artist, FullMetadata, Track
from waft.spotify import parse_album_data  # type: ignore
from waft.spotify import (get_metadata, parse_artists_data, parse_track_data,
                          parse_tracks_from_json, spotify_search)


def test_parse_tracks_from_json_single_artist():
    """Unit test for parse_tracks_from_json().

    when a single artist is inputted.
    """
    json_data = {
        "tracks": {
            "items": [
                {
                    "name": "Song A",
                    "id": "123",
                    "duration_ms": 100000,
                    "album": {"name": "Album A"},
                    "artists": [{"name": "Artist A"}],
                }
            ]
        }
    }

    result = parse_tracks_from_json(json_data)
    track = result[0]

    assert len(result) == 1
    assert track.title == "Song A"
    assert track.artist == "Artist A"
    assert track.album == "Album A"
    assert track.duration == 100000
    assert track.track_id == "123"


def test_parse_tracks_from_json_multiple_artists():
    """Unit test for parse_tracks_from_json().

    when multiple artists are inputted.
    """
    json_data = {
        "tracks": {
            "items": [
                {
                    "name": "Song A",
                    "id": "123",
                    "duration_ms": 100000,
                    "album": {"name": "Album A"},
                    "artists": [
                        {"name": "Artist A"},
                        {"name": "Artist B"},
                    ],
                }
            ]
        }
    }

    result = parse_tracks_from_json(json_data)
    track = result[0]

    assert track.artist == "Artist A and Others"


def test_parse_tracks_from_json_key_error():
    """Unit test for parse_tracks_from_json().

    when a KeyError Exception should be raised.
    """
    with pytest.raises(KeyError):
        parse_tracks_from_json({})


def test_parse_tracks_from_json_type_error():
    """Unit test for parse_tracks_from_json().

    when a TypeError Exception should be raised.
    """
    with pytest.raises(TypeError):
        parse_tracks_from_json([])


@patch("waft.spotify.requests.get")
def test_spotify_search_success(mock_get):
    """Unit test for spotify_search().

    when a value should be returned.
    """
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "tracks": {
            "items": [
                {
                    "name": "Song",
                    "id": "id1",
                    "duration_ms": 123,
                    "album": {"name": "Album"},
                    "artists": [{"name": "Artist"}],
                }
            ]
        }
    }

    mock_get.return_value = mock_response

    results = spotify_search("Song", "token123", limit=1)

    assert len(results) == 1
    assert isinstance(results[0], DisplayedTrack)


@patch("waft.spotify.requests.get")
def test_spotify_search_http_error(mock_get):
    """Unit test for spotify_search().

    when an HttpError Exception should be raised.
    """
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = requests.HTTPError
    mock_get.return_value = mock_response

    with pytest.raises(requests.HTTPError):
        spotify_search("Song", "token123", limit=1)


def test_parse_album_data_success():
    """Unit test for parse_album_data().

    when a value should be returned.
    """
    json_data = {
        "album": {
            "name": "Album X",
            "images": [{"url": "http://image.url"}],
        }
    }

    album = parse_album_data(json_data)

    assert isinstance(album, Album)
    assert album.album_name == "Album X"
    assert album.image_url == "http://image.url"


def test_parse_album_data_key_error():
    """Unit test for parse_album_data().

    when a KeyError Exception should be raised.
    """
    with pytest.raises(KeyError):
        parse_album_data({})


def test_parse_artists_data_multiple_artists():
    """Unit test for parse_artists_data().

    when multiple artists are inputted.
    """
    json_data = {
        "artists": [
            {"name": "Artist A"},
            {"name": "Artist B"},
        ]
    }

    artists = parse_artists_data(json_data)

    assert len(artists) == 2
    assert all(isinstance(a, Artist) for a in artists)
    assert artists[0].artist_name == "Artist A"


def test_parse_artists_data_key_error():
    """Unit test for parse_artists_data().

    when a KeyError Exception should be raised.
    """
    with pytest.raises(KeyError):
        parse_artists_data({})


def test_parse_track_data_success():
    """Unit test for parse_track_data().

    when a value should be returned correctly.
    """
    json_data = {
        "duration_ms": 300000,
        "explicit": False,
        "name": "Track Name",
        "track_number": 5,
        "album": {"release_date": "2020-01-01"},
    }

    track = parse_track_data(json_data)

    assert isinstance(track, Track)
    assert track.name == "Track Name"
    assert track.duration_ms == 300000
    assert track.explicit is False
    assert track.release_date == "2020-01-01"
    assert track.track_number == 5


def test_parse_track_data_key_error():
    """Unit test for parse_track_data().

    when a KeyError Exception should be raised.
    """
    with pytest.raises(KeyError):
        parse_track_data({})


@patch("waft.spotify.requests.get")
def test_get_metadata_success(mock_get):
    """Unit test for get_metadata().

    when a value should be returned correctly.
    """
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "duration_ms": 100000,
        "explicit": True,
        "name": "Test Song",
        "track_number": 1,
        "album": {
            "name": "Test Album",
            "release_date": "2022-01-01",
            "images": [{"url": "http://img"}],
        },
        "artists": [{"name": "Artist A"}],
    }

    mock_get.return_value = mock_response

    metadata = get_metadata("track123", "token123")

    assert isinstance(metadata, FullMetadata)
    assert metadata.album.album_name == "Test Album"
    assert metadata.track.name == "Test Song"
    assert metadata.artists[0].artist_name == "Artist A"


def test_get_metadata_value_error_track():
    """Unit test for get_metadata().

    when a ValueError Exception should be raised.
    """
    with pytest.raises(ValueError):
        get_metadata("", "token")


def test_get_metadata_value_error_token():
    """Unit test for get_metadata().

    when a ValueError Exception should be raised.
    """
    with pytest.raises(ValueError):
        get_metadata("track123", "")


@patch("waft.spotify.requests.get")
def test_get_metadata_http_error(mock_get):
    """Unit test for get_metadata().

    when a HttpError Exception should be raised.
    """
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
    mock_get.return_value = mock_response

    with pytest.raises(requests.HTTPError):
        get_metadata("track123", "token123")


@patch("waft.spotify.requests.get")
def test_get_metadata_request_request_exception(mock_get):
    """Unit test for get_metadata().

    when a RequestException should be raised.
    """
    mock_get.side_effect = requests.RequestException("Connection error")

    with pytest.raises(requests.RequestException):
        get_metadata("track123", "token123")
