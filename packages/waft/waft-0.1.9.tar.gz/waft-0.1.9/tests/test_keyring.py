# pylint: disable=protected-access
"""Unit tests for the functions in src/waft/keyring.py."""

from unittest.mock import patch

from securecredentials.exceptions import (  # type: ignore
    MasterDatabaseNotFoundError, UserDatabaseNotFoundError)

from waft.keyring import (retrieve_credentials,  # type: ignore
                          store_credentials)


@patch("waft.keyring.SecureCredentials")
def test_retrieve_credentials_success(mock_secure):
    """Unit test for retrieve_credentials().

    when it should succeed.
    """
    mock_secure._load_master_key.return_value = None

    mock_secure.get_secure.side_effect = [
        "spotify_id",
        "spotify_secret",
        "youtube_key",
    ]

    creds = retrieve_credentials()

    assert creds == ("spotify_id", "spotify_secret", "youtube_key")


@patch("waft.keyring.SecureCredentials")
def test_retrieve_credentials_master_database_not_found_error(mock_secure):
    """Unit test for retrieve_credentials().

    when the MasterDatabase can't be found.
    """
    mock_secure._load_master_key.side_effect = MasterDatabaseNotFoundError

    mock_secure.generate_master_key.return_value = "master_key"
    mock_secure.get_secure.side_effect = [
        "spotify_id",
        "spotify_secret",
        "youtube_key",
    ]

    creds = retrieve_credentials()

    mock_secure.store_master_key.assert_called_once_with(
        master_key="master_key",
        user_confirmation=False,
    )
    assert creds == ("spotify_id", "spotify_secret", "youtube_key")


@patch("waft.keyring.SecureCredentials")
def test_retrieve_credentials_user_database_not_found_error(mock_secure):
    """Unit test for retrieve_credentials().

    when the UserDatabase can't be found.
    """
    mock_secure._load_master_key.return_value = None

    mock_secure.get_secure.side_effect = UserDatabaseNotFoundError

    creds = retrieve_credentials()

    assert creds is None


@patch("waft.keyring.SecureCredentials")
def test_store_credentials_success(mock_secure):
    """Unit test for store_credentials().

    when it should succeed.
    """
    store_credentials(
        client_id="spotify_id",
        client_secret="spotify_secret",
        youtube_api_key="youtube_key",
    )

    mock_secure.set_secure.assert_any_call(field="SPOTIFY ID", plaintext="spotify_id")
    mock_secure.set_secure.assert_any_call(
        field="SPOTIFY SECRET", plaintext="spotify_secret"
    )
    mock_secure.set_secure.assert_any_call(field="YOUTUBE KEY", plaintext="youtube_key")

    assert mock_secure.set_secure.call_count == 3
