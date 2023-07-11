from datetime import datetime
from enum import Enum
from typing import Literal, List, Annotated, Any

from pydantic import BaseModel, Field, PositiveInt


class ExternalUrls(BaseModel):
    spotify: str


class Image(BaseModel):
    url: str
    height: int | None = None
    width: int | None = None


class Followers(BaseModel):
    href: str | None = None
    total: int


class PublicUser(BaseModel):
    external_urls: ExternalUrls
    followers: Followers | None = None
    href: str
    id: str
    type: Literal["user"]
    uri: str
    display_name: str | None = None


class PlaylistTracksReference(BaseModel):
    href: str
    total: int


class SimplifiedPlaylist(BaseModel):
    collaborative: bool
    description: str | None = None
    external_urls: ExternalUrls
    href: str
    id: str
    images: List[Image]
    name: str
    owner: PublicUser
    public: bool | None = None
    snapshot_id: str
    tracks: PlaylistTracksReference | None = None
    type: Literal["playlist"]
    uri: str


Popularity = Annotated[int, Field(ge=0, le=100)]


class Restrictions(BaseModel):
    reason: str


class ExternalIds(BaseModel):
    isrc: str
    ean: str
    upc: str


class AlbumGroup(str, Enum):
    single = "single"
    album = "album"
    compilation = "compilation"


class ReleaseDatePrecision(str, Enum):
    year = "year"
    month = "month"
    day = "day"


class SimplifiedArtist(BaseModel):
    type: Literal["artist"]
    external_urls: ExternalUrls
    href: str
    id: str
    name: str
    uri: str


class Artist(SimplifiedArtist):
    followers: Followers
    genres: List[str]
    images: List[Image]
    popularity: Popularity


class Album(BaseModel):
    type: Literal["album"]
    album_type: AlbumGroup
    total_tracks: int
    available_markets: List[str]
    external_urls: ExternalUrls
    href: str
    id: str
    images: List[Image]
    name: str
    release_date: str
    release_date_precision: ReleaseDatePrecision
    restrictions: Restrictions | None = None
    uri: str
    copyrights: Any | None = None
    external_ids: ExternalIds | None = None
    label: str | None = None
    genres: List[str] | None = None
    popularity: Popularity | None = None
    album_group: str | None = None
    artists: List[SimplifiedArtist]


class LinkedTrack(BaseModel):
    external_urls: ExternalUrls
    href: str
    id: str
    type: Literal["track"]
    uri: str


class SimplifiedTrack(BaseModel):
    type: Literal["track"]
    album: Album
    artists: List[SimplifiedArtist]
    available_markets: List[str]
    disc_number: PositiveInt
    duration_ms: int
    explicit: bool
    external_urls: ExternalUrls
    href: str
    id: str
    is_playable: bool | None = None
    linked_from: LinkedTrack | None = None
    name: str
    popularity: Popularity
    preview_url: str | None = None
    track_number: PositiveInt
    uri: str
    is_local: bool


class Episode(BaseModel):
    type: Literal["episode"]
    audio_preview_url: str | None = None
    description: str
    html_description: str
    duration_ms: int
    explicit: bool
    external_urls: ExternalUrls
    href: str
    id: str
    images: List[Image]
    is_externally_hosted: bool
    is_playable: bool
    languages: List[str]
    name: str
    release_date: str
    release_date_precision: str
    uri: str
    restrictions: Restrictions
    # Ignored attributes for now (episodes are not considered)
    resume_point: Any
    show: Any


class PlaylistTrack(BaseModel):
    added_at: datetime | None = None
    added_by: PublicUser | None = None
    is_local: bool
    track: SimplifiedTrack | Episode = Field(discriminator="type")


class Playlist(SimplifiedPlaylist):
    followers: Followers
    # Tracks are parsed separately
    # tracks: List[PlaylistTrack]
