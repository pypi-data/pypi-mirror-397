"""Unit tests for the functions in src/waft/model.py."""

from pathlib import Path

from waft.messages import SearchRequest  # type: ignore
from waft.messages import Authenticating, UpdateStatus, UrlSelected
from waft.model import ApplicationModel, update  # type: ignore


def make_base_model() -> ApplicationModel:
    """Create a base model for testing.

    Creates a base model to test against.
    """
    return ApplicationModel(
        active_token="token",
        api_key="api",
        authenticating=False,
        developer_key="dev",
        downloads_folder=Path("/tmp"),
        search_query=("", ""),
        search_results=[],
        selection=None,
        suggestion_results=[],
        status_message="",
        valid_credentials=False,
    )


def test_update_update_status():
    """Unit test for update().

    when an UpdateStatus message is sent.
    """
    model = make_base_model()
    message = UpdateStatus(text="Testing...")

    new_model = update(model, message)

    assert isinstance(new_model, ApplicationModel)
    assert new_model.status_message == "Testing..."
    assert model.status_message == ""
    assert new_model is not model


def test_update_authenticating():
    """Unit test for update().

    when an Authenticating message is sent.
    """
    model = make_base_model()
    message = Authenticating(state=True)

    new_model = update(model, message)

    assert isinstance(new_model, ApplicationModel)
    assert new_model.authenticating is True
    assert model.authenticating is False
    assert new_model is not model


def test_update_search_request():
    """Unit test for update().

    when a SearchRequest message is sent.
    """
    model = make_base_model()
    message = SearchRequest(query="Test", mode="spotify")

    new_model = update(model, message)

    assert isinstance(new_model, ApplicationModel)
    assert new_model.search_query == ("Test", "spotify")
    assert model.search_query == ("", "")
    assert new_model is not model


def test_update_other():
    """Unit test for update().

    when any other message is sent.
    """
    model = make_base_model()
    message = UrlSelected(index=0)

    new_model = update(model, message)

    assert isinstance(new_model, ApplicationModel)
    assert new_model is model
