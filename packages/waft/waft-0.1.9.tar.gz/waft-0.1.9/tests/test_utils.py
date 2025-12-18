"""Unit tests for the functions in src/waft/utils.py."""

from textual.widgets.option_list import Option  # type: ignore

from waft.datatypes import DisplayedTrack, YoutubeResult  # type: ignore
from waft.utils import create_options_from_results  # type: ignore
from waft.utils import create_options_from_suggestions, format_milliseconds


def test_format_milliseconds_1():
    """Unit test for test_format_milliseconds().

    when milliseconds = 30000.
    """
    assert format_milliseconds(30000) == "0:30"


def test_format_milliseconds_2():
    """Unit test for test_format_milliseconds().

    when milliseconds = 3600000.
    """
    assert format_milliseconds(3600000) == "1:00:00"


def test_format_milliseconds_3():
    """Unit test for test_format_milliseconds().

    when milliseconds = 0.
    """
    assert format_milliseconds(0) == "0:00"


def test_create_options_from_results_single_track():
    """Unit test for create_options_from_results().

    when a single track is inputted.
    """
    track = DisplayedTrack(
        title="Song A",
        artist="Artist A",
        album="Album A",
        duration=90_000,
        track_id="123",
    )
    results = [track]

    options = create_options_from_results(results)
    opt = options[0]

    assert isinstance(options, list)
    assert len(options) == 1
    assert isinstance(opt, Option)


def test_create_options_from_results_multiple_tracks():
    """Unit test for create_options_from_results().

    when multiple tracks are inputted.
    """
    tracks = [
        DisplayedTrack("Song A", "Artist A", "Album A", 90_000, "123"),
        DisplayedTrack("Song B", "Artist B", "Album B", 120_000, "456"),
    ]
    options = create_options_from_results(tracks)
    assert len(options) == 2
    for opt in options:
        assert isinstance(opt, Option)


def test_create_options_from_suggestions_single_video():
    """Unit test for create_options_from_suggestions().

    when a single video is inputted.
    """
    suggestion = YoutubeResult(
        video_title="Video 1", channel="Channel 1", url="https://youtube.com/vid1"
    )
    options = create_options_from_suggestions([suggestion])
    opt = options[0]

    assert isinstance(options, list)
    assert len(options) == 1
    assert isinstance(opt, Option)


def test_create_options_from_suggestions_multiple_videos():
    """Unit test for create_options_from_suggestions().

    when multiple videos are inputted.
    """
    suggestions = [
        YoutubeResult("Video 1", "Channel 1", "url1"),
        YoutubeResult("Video 2", "Channel 2", "url2"),
    ]
    options = create_options_from_suggestions(suggestions)
    assert len(options) == 2
    for opt in options:
        assert isinstance(opt, Option)
