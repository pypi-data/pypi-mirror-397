"""Unit tests for the functions in src/waft/metadata.py."""

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

from eyed3.id3.frames import ImageFrame  # type: ignore

from waft.datatypes import DisplayedTrack  # type: ignore
from waft.metadata import write_metadata  # type: ignore


@patch("waft.metadata.urlopen")
@patch("waft.metadata.eyed3.load")
@patch("waft.metadata.music_tag.load_file")
def test_write_metadata_success(mock_load_file, mock_eyed3_load, mock_urlopen):
    """Unit test for write_metadata().

    when it should succeed.
    """
    path = Path("test_song")
    image_url = "http://example.com/cover.jpg"

    track = DisplayedTrack(
        title="Test Title",
        artist="Test Artist",
        album="Test Album",
        duration=123456,
        track_id="1234",
    )

    mock_tags = MagicMock()
    mock_load_file.return_value = mock_tags

    mock_response = Mock()
    mock_response.read.return_value = b"fake-image-bytes"
    mock_urlopen.return_value = mock_response

    mock_audiofile = Mock()
    mock_audiofile.tag = Mock()
    mock_audiofile.tag.images = Mock()
    mock_eyed3_load.return_value = mock_audiofile

    write_metadata(path, track, image_url)

    mock_load_file.assert_called_once_with("test_song.mp3")

    mock_tags.__setitem__.assert_any_call("tracktitle", "Test Title")
    mock_tags.__setitem__.assert_any_call("artist", "Test Artist")
    mock_tags.__setitem__.assert_any_call("album", "Test Album")
    mock_tags.save.assert_called_once()

    mock_urlopen.assert_called_once_with(image_url)
    mock_response.read.assert_called_once()

    mock_eyed3_load.assert_called_once_with("test_song.mp3")

    mock_audiofile.tag.images.set.assert_called_once_with(
        ImageFrame.FRONT_COVER,
        b"fake-image-bytes",
        "image/jpeg",
    )

    mock_audiofile.tag.save.assert_called_once_with(version=(2, 3, 0))
