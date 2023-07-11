import tests.data.users as users
from tests.data.images import dummy_images


def create_playlist(
    num: int,
    tracks: any,
    owner=users.spotify,
):
    sid = f"PLAYLIST_ID{num}"
    return {
        "collaborative": False,
        "description": f"Description for Playlist {num}",
        "external_urls": {"spotify": f"https://open.spotify.com/playlist/{sid}"},
        "followers": {
            "href": None,
            # followers are currently not tracked
            "total": 123,
        },
        "href": f"https://api.spotify.com/v1/playlists/{sid}",
        "id": sid,
        "images": dummy_images,
        "name": f"Playlist {num}",
        "owner": owner,
        "public": False,
        "snapshot_id": f"PLAYLIST_SNAPSHOT_ID{num}",
        "tracks": tracks,
        "type": "playlist",
        "uri": f"spotify:playlist:{sid}",
    }


dummy_playlist1 = create_playlist(
    num=1,
    tracks={
        "href": "https://api.spotify.com/v1/playlists/PLAYLISTID1/tracks",
        "total": 2,
    },
)
dummy_playlist2 = create_playlist(
    num=2,
    tracks={
        "href": "https://api.spotify.com/v1/playlists/PLAYLISTID2/tracks",
        "total": 3,
    },
)
dummy_playlists = [
    dummy_playlist1,
    dummy_playlist2,
]


def create_default_playlist(tracks: dict[any]) -> any:
    return create_playlist(
        num=1,
        owner=users.spotify,
        tracks=tracks,
    )
