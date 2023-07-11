import gzip
import os
from pathlib import Path
from unittest import mock
from unittest.mock import patch

import pytest
import responses
from responses.registries import OrderedRegistry

import tests.data as data
import tests.data.artists
import tests.data.playlists
import tests.data.tracks
import tests.data.users
from paddle.downloader import main, run
from paddle.downloader.config import SpotifyConfig, Config

auth_url = "https://accounts.spotify.com/api/token"
base_url = "https://api.spotify.com/v1/"
default_category = "latin"
default_category_id = "CATEGORY_ID1"
default_playlist_id = "PLAYLIST_ID1"


@pytest.fixture(autouse=True)
def env_vars():
    fake_envs = {
        "SPOTIFY_CLIENT_ID": "spotify-client-id",
        "SPOTIFY_CLIENT_SECRET": "spotify-client-secret",
    }
    with mock.patch.dict(os.environ, fake_envs):
        yield


@pytest.fixture
def mocked_responses():
    with responses.RequestsMock(registry=OrderedRegistry) as rs:
        auth = rs.post(
            auth_url,
            json={"access_token": "XYZ"},
        )
        yield rs
        assert auth.call_count == 1, "Access token should be requested exactly once"


def read_tables(tmp_path: Path) -> dict[str, list[str]]:
    result = {}
    for file in tmp_path.glob("*.csv.gz"):
        table_name = file.stem.split(".")[0]
        with gzip.open(tmp_path / file, "rt") as f:
            lines = f.read().splitlines()
            result[table_name] = lines
    return result


def test_playlists_pagination(mocked_responses: responses.RequestsMock, tmp_path: Path):
    # return a playlist pagination response with two pages
    mocked_responses.get(
        f"{base_url}browse/categories/{default_category}/playlists",
        json={
            "playlists": {
                "href": f"https://api.spotify.com/v1/browse/categories/{default_category_id}/playlists?country=DE&offset=0&limit=1",
                "items": [tests.data.playlists.dummy_playlists[0]],
                "limit": 1,
                "next": f"https://api.spotify.com/v1/browse/categories/{default_category_id}/playlists?country=DE&offset=1&limit=1",
                "offset": 0,
                "previous": None,
                "total": 2,
            }
        },
    )
    # first playlist detail page
    mocked_responses.get(
        f"{base_url}playlists/{default_playlist_id}",
        json=data.create_default_playlist(
            tracks=data.create_items_no_pagination(
                items=[
                    tests.data.tracks.dummy_track_1,
                    tests.data.tracks.dummy_track_2,
                ],
                href=f"https://api.spotify.com/v1/playlists/{default_playlist_id}/tracks?offset=0&limit=1",
            ),
        ),
    )
    # second playlists page
    mocked_responses.get(
        f"{base_url}browse/categories/{default_category_id}/playlists",
        json={
            "playlists": {
                "href": f"https://api.spotify.com/v1/browse/categories/{default_category_id}/playlists?country=DE&offset=1&limit=1",
                "items": [tests.data.playlists.dummy_playlist2],
                "limit": 1,
                "next": None,
                "offset": 0,
                "previous": None,
                "total": 2,
            }
        },
    )

    # detail page for playlist on second page
    mocked_responses.get(
        f"{base_url}playlists/PLAYLIST_ID2",
        json=tests.data.playlists.create_playlist(
            num=2,
            owner=tests.data.users.spotify,
            tracks=data.create_items_no_pagination(
                items=[
                    data.dummy_track_3,
                ],
                href="https://api.spotify.com/v1/playlists/PLAYLIST_ID2/tracks?offset=0&limit=100",
            ),
        ),
    )
    run_main(tmp_path)
    table_names = {
        "artists_records": [
            "id,name",
            "ARTISTID1,Artist 1",
            "ARTISTID2,Artist 2",
            "ARTISTID3,Artist 3",
            "ARTISTID4,Artist 4",
        ],
        "category_playlists_records": [
            "description,name,id,tracks_url,total_tracks,snapshot_id",
            "Description for Playlist 1,Playlist "
            "1,PLAYLIST_ID1,spotify:playlist:PLAYLIST_ID1/tracks,2,PLAYLIST_SNAPSHOT_ID1",
            "Description for Playlist 2,Playlist "
            "2,PLAYLIST_ID2,spotify:playlist:PLAYLIST_ID2/tracks,1,PLAYLIST_SNAPSHOT_ID2",
        ],
        "playlist_records": ["id,followers", "PLAYLIST_ID1,123", "PLAYLIST_ID2,123"],
        "playlist_track_id_records": [
            "playlist_id,playlist_added_at,track_id",
            "PLAYLIST_ID1,2023-07-07T04:00:00+00:00,TRACKID1",
            "PLAYLIST_ID1,2023-07-07T04:00:00+00:00,TRACKID2",
            "PLAYLIST_ID2,2023-07-07T04:00:00+00:00,TRACKID3",
        ],
        "track_artist_id_records": [
            "track_id,artist_id",
            "TRACKID1,ARTISTID1",
            "TRACKID1,ARTISTID2",
            "TRACKID2,ARTISTID3",
            "TRACKID3,ARTISTID4",
        ],
        "tracks_records": [
            "album_type,id,name,popularity,uri",
            "album,TRACKID1,Track 1,89,spotify:track:TRACKID1",
            "album,TRACKID2,Track 2,55,spotify:track:TRACKID2",
            "album,TRACKID3,Track 3,78,spotify:track:TRACKID3",
        ],
    }
    assert read_tables(tmp_path) == table_names


def run_main(tmp_path: Path):
    main(["-o", str(tmp_path)])


def test_track_pagination(mocked_responses: responses.RequestsMock, tmp_path: Path):
    mocked_responses.get(
        f"{base_url}browse/categories/{default_category}/playlists",
        json={
            "playlists": data.create_items_no_pagination(
                items=[tests.data.playlists.dummy_playlist1],
                href=f"https://api.spotify.com/v1/browse/categories/{default_category_id}/playlists?country=DE&offset=0&limit=1",
            )
        },
    )
    # details page for the first playlist
    mocked_responses.get(
        f"{base_url}playlists/{default_playlist_id}",
        json=data.create_default_playlist(
            tracks={
                "href": f"https://api.spotify.com/v1/playlists/{default_playlist_id}/tracks?offset=0&limit=1",
                "items": [tests.data.tracks.dummy_track_1],
                "limit": 1,
                "next": f"https://api.spotify.com/v1/playlists/{default_playlist_id}/tracks?offset=1&limit=1",
                "offset": 0,
                "previous": None,
                "total": 2,
            },
        ),
    )
    # second tracks page for the first playlist
    mocked_responses.get(
        f"{base_url}playlists/{default_playlist_id}/tracks",
        json={
            "href": f"https://api.spotify.com/v1/playlists/{default_playlist_id}/tracks?offset=1&limit=1",
            "items": [tests.data.tracks.dummy_track_2],
            "limit": 1,
            "next": None,
            "offset": 1,
            "previous": None,
            "total": 2,
        },
    )
    run_main(tmp_path)
    expected_tables = {
        "artists_records": [
            "id,name",
            "ARTISTID1,Artist 1",
            "ARTISTID2,Artist 2",
            "ARTISTID3,Artist 3",
        ],
        "category_playlists_records": [
            "description,name,id,tracks_url,total_tracks,snapshot_id",
            "Description for Playlist 1,Playlist "
            "1,PLAYLIST_ID1,spotify:playlist:PLAYLIST_ID1/tracks,2,PLAYLIST_SNAPSHOT_ID1",
        ],
        "playlist_records": ["id,followers", "PLAYLIST_ID1,123"],
        "playlist_track_id_records": [
            "playlist_id,playlist_added_at,track_id",
            "PLAYLIST_ID1,2023-07-07T04:00:00+00:00,TRACKID1",
            "PLAYLIST_ID1,2023-07-07T04:00:00+00:00,TRACKID2",
        ],
        "track_artist_id_records": [
            "track_id,artist_id",
            "TRACKID1,ARTISTID1",
            "TRACKID1,ARTISTID2",
            "TRACKID2,ARTISTID3",
        ],
        "tracks_records": [
            "album_type,id,name,popularity,uri",
            "album,TRACKID1,Track 1,89,spotify:track:TRACKID1",
            "album,TRACKID2,Track 2,55,spotify:track:TRACKID2",
        ],
    }
    assert read_tables(tmp_path) == expected_tables


def test_rate_limit(mocked_responses: responses.RequestsMock, tmp_path: Path):
    mocked_responses.get(
        f"{base_url}browse/categories/{default_category}/playlists",
        status=429,
        headers={"Retry-After": "42"},
    )
    mocked_responses.get(
        f"{base_url}browse/categories/{default_category}/playlists",
        json={
            "playlists": data.create_items_no_pagination(
                items=[tests.data.playlists.dummy_playlist1],
                href=f"https://api.spotify.com/v1/browse/categories/{default_category_id}/playlists?country=DE&offset=0&limit=1",
            )
        },
    )
    mocked_responses.get(
        f"{base_url}playlists/{default_playlist_id}",
        json=data.create_default_playlist(
            tracks=data.create_items_no_pagination(
                items=[tests.data.tracks.dummy_track_1],
                href=f"https://api.spotify.com/v1/playlists/{default_playlist_id}/tracks?offset=0&limit=1",
            ),
        ),
    )
    # This is not ideal as the rate limiter fills up the bucket, and thus we wait an actual second
    spotify_config = SpotifyConfig(
        client_id="X",
        client_secret="X",
        rate_limit_requests_per_bucket=20,
        rate_limit_bucket_size_seconds=1,
    )
    config = Config(spotify=spotify_config, output_dir=tmp_path)
    with patch("time.sleep", return_value=None) as patched_time_sleep:
        run(config)
        patched_time_sleep.assert_called_with(42)
        assert patched_time_sleep.call_count == 1

    expected_tables = {
        "artists_records": ["id,name", "ARTISTID1,Artist 1", "ARTISTID2,Artist 2"],
        "category_playlists_records": [
            "description,name,id,tracks_url,total_tracks,snapshot_id",
            "Description for Playlist 1,Playlist "
            "1,PLAYLIST_ID1,spotify:playlist:PLAYLIST_ID1/tracks,1,PLAYLIST_SNAPSHOT_ID1",
        ],
        "playlist_records": ["id,followers", "PLAYLIST_ID1,123"],
        "playlist_track_id_records": [
            "playlist_id,playlist_added_at,track_id",
            "PLAYLIST_ID1,2023-07-07T04:00:00+00:00,TRACKID1",
        ],
        "track_artist_id_records": [
            "track_id,artist_id",
            "TRACKID1,ARTISTID1",
            "TRACKID1,ARTISTID2",
        ],
        "tracks_records": [
            "album_type,id,name,popularity,uri",
            "album,TRACKID1,Track 1,89,spotify:track:TRACKID1",
        ],
    }
    assert read_tables(tmp_path) == expected_tables


def test_duplicates(mocked_responses: responses.RequestsMock, tmp_path: Path):
    """
    Have a duplicated playlist, track and artist.
    """
    mocked_responses.get(
        f"{base_url}browse/categories/{default_category}/playlists",
        json={
            "playlists": data.create_items_no_pagination(
                items=[
                    tests.data.playlists.dummy_playlist1,
                    tests.data.playlists.dummy_playlist1,
                ],
                href=f"https://api.spotify.com/v1/browse/categories/{default_category_id}/playlists?country=DE&offset=0&limit=1",
            )
        },
    )
    mocked_responses.get(
        f"{base_url}playlists/{default_playlist_id}",
        json=data.create_default_playlist(
            tracks=data.create_items_no_pagination(
                items=[
                    {
                        **tests.data.tracks.dummy_track_1,
                        "artists": [
                            tests.data.artists.artist_1,
                            tests.data.artists.artist_1,
                        ],
                    },
                    tests.data.tracks.dummy_track_1,
                ],
                href="https://api.spotify.com/v1/playlists/{default_playlist_id}/tracks?offset=0&limit=1",
            ),
        ),
    )
    run_main(tmp_path)
    expected_tables = {
        "artists_records": ["id,name", "ARTISTID1,Artist 1", "ARTISTID2,Artist 2"],
        "category_playlists_records": [
            "description,name,id,tracks_url,total_tracks,snapshot_id",
            "Description for Playlist 1,Playlist "
            "1,PLAYLIST_ID1,spotify:playlist:PLAYLIST_ID1/tracks,2,PLAYLIST_SNAPSHOT_ID1",
        ],
        "playlist_records": ["id,followers", "PLAYLIST_ID1,123"],
        "playlist_track_id_records": [
            "playlist_id,playlist_added_at,track_id",
            "PLAYLIST_ID1,2023-07-07T04:00:00+00:00,TRACKID1",
        ],
        "track_artist_id_records": [
            "track_id,artist_id",
            "TRACKID1,ARTISTID1",
            "TRACKID1,ARTISTID2",
        ],
        "tracks_records": [
            "album_type,id,name,popularity,uri",
            "album,TRACKID1,Track 1,89,spotify:track:TRACKID1",
        ],
    }
    assert read_tables(tmp_path) == expected_tables
