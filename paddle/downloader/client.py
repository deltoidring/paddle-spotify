from dataclasses import dataclass
from typing import Iterator

from pydantic import ValidationError
from requests import Session

from paddle.downloader.models import Playlist
from paddle.downloader.models import SimplifiedPlaylist
from paddle.downloader.playlist import PlaylistClient
from paddle.downloader.session import get_response_dict


@dataclass
class SpotifyClient:
    """
    A mini Spotify client to fetch playlists.
    """

    session: Session

    def get_playlists(self, category_id: str) -> Iterator[SimplifiedPlaylist]:
        next_url = f"browse/categories/{category_id}/playlists?limit=50"
        while next_url is not None:
            res = self.session.get(next_url)
            data = get_response_dict(res)
            playlists = data.get("playlists")
            assert isinstance(playlists, dict)
            next_url = playlists.get("next")
            items = playlists["items"]
            assert isinstance(items, list)
            for item in items:
                try:
                    yield SimplifiedPlaylist.model_validate(item)
                except ValidationError as e:
                    raise e

    def get_playlist(self, playlist_id: str) -> PlaylistClient:
        res = self.session.get(f"playlists/{playlist_id}")
        data = get_response_dict(res)
        next_url = data["tracks"].get("next")
        tracks = data["tracks"]["items"]
        del data["tracks"]
        playlist = Playlist.model_validate(data)
        return PlaylistClient(
            self.session, playlist=playlist, next_url=next_url, pending_tracks=tracks
        )
