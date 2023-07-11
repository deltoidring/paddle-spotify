from dataclasses import dataclass
from typing import Iterator

from requests import Session

from paddle.downloader.models import Playlist, PlaylistTrack
from paddle.downloader.session import get_response_dict


@dataclass
class PlaylistClient:
    """
    Client over a Spotify Playlist.
    Allows to lazily fetch all tracks of a given playlist.
    """

    session: Session
    playlist: Playlist
    next_url: str
    pending_tracks: list[any]

    def get_tracks(self) -> Iterator[PlaylistTrack]:
        for item in self.pending_tracks:
            yield PlaylistTrack.model_validate(item)
        next_url = self.next_url
        while next_url is not None:
            res = self.session.get(next_url)
            data = get_response_dict(res)
            for item in data["items"]:
                yield PlaylistTrack.model_validate(item)
            next_url = data["next"]
