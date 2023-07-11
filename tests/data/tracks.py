import tests.data.users as users
from tests.data import artist_1, artist_2, artist_3, artist_4
from tests.data.images import dummy_images
from tests.data.markets import available_markets


def create_track_item(track: dict[any], added_by: dict[any] | None = None) -> dict[any]:
    return {
        "added_at": "2023-07-07T04:00:00Z",
        "added_by": added_by or users.spotify.copy(),
        "is_local": False,
        "track": track,
    }


def create_album(num: int, artists: list[any]):
    sid = f"ALBUMID{num}"
    return {
        "name": f"Album {num}",
        "album_type": "single",
        "artists": artists,
        "available_markets": available_markets,
        "external_urls": {"spotify": f"https://open.spotify.com/album/{sid}"},
        "href": f"https://api.spotify.com/v1/albums/{sid}",
        "id": sid,
        "images": dummy_images,
        "release_date": "2023-06-23",
        "release_date_precision": "day",
        "total_tracks": 1,
        "type": "album",
        "uri": f"spotify:album:{sid}",
    }


def create_track(num: int, album: dict[any], popularity: int, artists: list[any]):
    sid = f"TRACKID{num}"
    return {
        "album": album,
        "artists": artists,
        "available_markets": available_markets,
        "disc_number": 1,
        "duration_ms": 222461,
        "episode": False,
        "explicit": True,
        "external_ids": {"isrc": "USSD12300274"},
        "external_urls": {"spotify": f"https://open.spotify.com/track/{sid}"},
        "href": f"https://api.spotify.com/v1/tracks/{sid}",
        "id": sid,
        "is_local": False,
        "name": f"Track {num}",
        "popularity": popularity,
        "preview_url": f"https://p.scdn.co/mp3-preview/{sid}",
        "track": True,
        "track_number": 1,
        "type": "track",
        "uri": f"spotify:track:{sid}",
    }


dummy_album_1 = create_album(
    1,
    artists=[
        artist_1,
        artist_2,
    ],
)
dummy_track_1 = create_track_item(
    create_track(
        num=1, popularity=89, album=dummy_album_1, artists=dummy_album_1["artists"]
    )
)
dummy_album_2 = create_album(
    2,
    artists=[
        artist_3,
    ],
)
dummy_track_2 = create_track_item(
    create_track(
        num=2, popularity=55, album=dummy_album_2, artists=dummy_album_2["artists"]
    )
)
dummy_album_3 = create_album(
    3,
    artists=[
        artist_4,
    ],
)
dummy_track_3 = create_track_item(
    create_track(
        num=3, popularity=78, album=dummy_album_3, artists=dummy_album_3["artists"]
    )
)
