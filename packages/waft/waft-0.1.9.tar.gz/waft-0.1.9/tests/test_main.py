"""Test waft package functionality."""

from waft.application import Application


def test_application_exists():
    """Test that Application class can be imported."""
    assert Application is not None


def test_application_instantiation():
    """Test that Application can be instantiated."""
    app = Application()
    assert app is not None
