"""Unit tests for the functions in src/waft/youtube.py."""

from unittest.mock import Mock, patch

from waft.datatypes import DisplayedTrack, YoutubeResult  # type: ignore
from waft.youtube import (parse_results_from_json,  # type: ignore
                          search_youtube)


def test_parse_results_from_json_remove_non_videos():
    """Unit test for parse_results_from_json().

    when there is a non video inputted.
    """
    response = {
        "items": [
            {
                "id": {"kind": "youtube#channel"},
                "snippet": {
                    "title": "Channel",
                    "channelTitle": "Someone",
                },
            },
            {
                "id": {
                    "kind": "youtube#video",
                    "videoId": "abc123",
                },
                "snippet": {
                    "title": "Song Title",
                    "channelTitle": "Artist Channel",
                },
            },
        ]
    }

    results = parse_results_from_json(response)

    assert len(results) == 1
    assert isinstance(results[0], YoutubeResult)
    assert results[0].video_title == "Song Title"
    assert results[0].channel == "Artist Channel"
    assert results[0].url == "https://www.youtube.com/watch?v=abc123"


def test_parse_results_from_json_multiple_videos():
    """Unit test for parse_results_from_json().

    when multiple videos are inputted.
    """
    response = {
        "items": [
            {
                "id": {"kind": "youtube#video", "videoId": "id1"},
                "snippet": {
                    "title": "Video 1",
                    "channelTitle": "Channel 1",
                },
            },
            {
                "id": {"kind": "youtube#video", "videoId": "id2"},
                "snippet": {
                    "title": "Video 2",
                    "channelTitle": "Channel 2",
                },
            },
        ]
    }

    results = parse_results_from_json(response)

    assert len(results) == 2
    assert results[0].url.endswith("id1")
    assert results[1].url.endswith("id2")


def test_parse_results_from_json_no_videos():
    """Unit test for parse_results_from_json().

    when no videos are inputted.
    """
    response = {
        "items": [
            {
                "id": {"kind": "youtube#channel"},
                "snippet": {
                    "title": "Some Channel",
                    "channelTitle": "Channel Name",
                },
            },
            {
                "id": {"kind": "youtube#playlist"},
                "snippet": {
                    "title": "Some Playlist",
                    "channelTitle": "Playlist Owner",
                },
            },
        ]
    }

    results = parse_results_from_json(response)

    assert not results


@patch("waft.youtube.parse_results_from_json")
@patch("waft.youtube.googleapiclient.discovery.build")
def test_search_youtube_success(mock_build, mock_parse):
    """Unit test for search_youtube().

    when it should succeed.
    """
    track = DisplayedTrack(
        title="Doxy",
        artist="Miles Davis",
        album="Relaxin'",
        duration=300000,
        track_id="1234",
    )

    mock_parse.return_value = ["parsed_result"]

    mock_request = Mock()
    mock_request.execute.return_value = {"items": []}

    mock_search = Mock()
    mock_search.list.return_value = mock_request

    mock_youtube = Mock()
    mock_youtube.search.return_value = mock_search

    mock_build.return_value = mock_youtube

    results = search_youtube(track, api_key="fake_key")

    mock_build.assert_called_once_with("youtube", "v3", developerKey="fake_key")

    mock_search.list.assert_called_once_with(
        part="snippet",
        maxResults=25,
        q="Doxy Miles Davis Relaxin'",
    )

    mock_request.execute.assert_called_once()
    mock_parse.assert_called_once_with({"items": []})
    assert results == ["parsed_result"]
