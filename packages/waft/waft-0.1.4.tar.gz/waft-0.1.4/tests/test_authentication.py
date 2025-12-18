"""Unit tests for the functions in src/waft/authentication.py."""

import asyncio
from unittest.mock import Mock, patch

import pytest  # type: ignore
import requests  # type: ignore

from waft.authentication import (  # type: ignore
    authenticate_spotify_access_token, get_spotify_access_token)


@patch("waft.authentication.requests.post")
def test_get_spotify_access_token_success(mock_post):
    """Unit test for get_spotify_access_token().

    when a value should be returned.
    """
    mock_resp = Mock()
    mock_resp.raise_for_status.return_value = None
    mock_resp.json.return_value = {"access_token": "fake_token_123"}
    mock_post.return_value = mock_resp

    token = asyncio.run(get_spotify_access_token("client_id", "client_secret"))
    assert token == "fake_token_123"
    mock_post.assert_called_once()


@patch("waft.authentication.requests.post")
def test_get_spotify_access_token_fail(mock_post):
    """Unit test for get_spotify_access_token().

    when it should fail
    """
    mock_resp = Mock()
    mock_resp.raise_for_status.side_effect = requests.HTTPError("400 Bad Request")
    mock_post.return_value = mock_resp

    token = asyncio.run(get_spotify_access_token("client_id", "client_secret"))
    assert token is None


@patch("waft.authentication.requests.post")
def test_get_spotify_access_token_http_error(mock_post):
    """Unit test for get_spotify_access_token().

    when a HttpError should be raised.
    """
    mock_resp = Mock()
    mock_resp.raise_for_status.return_value = None
    mock_resp.json.return_value = {}  # missing key
    mock_post.return_value = mock_resp

    with pytest.raises(KeyError):
        asyncio.run(get_spotify_access_token("client_id", "client_secret"))


@patch("waft.authentication.requests.get")
def test_authenticate_spotify_access_token_success(mock_get):
    """Unit test for authenticate_spotify_access_token().

    when a value should be returned.
    """
    mock_resp = Mock()
    mock_resp.raise_for_status.return_value = None
    mock_resp.json.return_value = {"tracks": {"items": [{"name": "Song"}]}}
    mock_get.return_value = mock_resp

    result = authenticate_spotify_access_token("valid_token")
    assert result is True


@patch("waft.authentication.requests.get")
def test_authenticate_spotify_access_token_fail(mock_get):
    """Unit test for authenticate_spotify_access_token().

    when it should fail.
    """
    mock_resp = Mock()
    mock_resp.raise_for_status.return_value = None
    mock_resp.json.return_value = {"tracks": {"items": []}}
    mock_get.return_value = mock_resp

    result = authenticate_spotify_access_token("valid_token")
    assert result is False


@patch("waft.authentication.requests.get")
def test_authenticate_spotify_access_token_http_error(mock_get):
    """Unit test for authenticate_spotify_access_token().

    when a HttpError should be raised.
    """
    mock_resp = Mock()
    mock_resp.raise_for_status.side_effect = requests.HTTPError("401 Unauthorized")
    mock_get.return_value = mock_resp

    with pytest.raises(requests.HTTPError):
        authenticate_spotify_access_token("invalid_token")


@patch("waft.authentication.requests.get")
def test_authenticate_spotify_access_token_request_exception(mock_get):
    """Unit test for authenticate_spotify_access_token().

    when a RequestException should be raised.
    """
    mock_get.side_effect = requests.RequestException("Connection error")

    with pytest.raises(requests.RequestException):
        authenticate_spotify_access_token("token123")
