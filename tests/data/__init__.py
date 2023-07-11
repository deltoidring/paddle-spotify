import tests.data.users as users
from .artists import create_artist, artist_1, artist_2, artist_3, artist_4
from .images import dummy_images
from .markets import available_markets
from .playlists import (
    create_playlist,
    create_default_playlist,
    dummy_playlist2,
    dummy_playlist1,
    dummy_playlists,
)
from .tracks import (
    create_track,
    create_album,
    dummy_track_1,
    dummy_track_2,
    dummy_track_3,
)


def create_items_no_pagination(items: list[any], href: str) -> dict[any]:
    return {
        "href": href,
        "items": items,
        "limit": len(items),
        "next": None,
        "offset": 0,
        "previous": None,
        "total": len(items),
    }
