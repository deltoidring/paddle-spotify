import _csv
import csv
import gzip
from abc import ABCMeta, abstractmethod
from typing import List, Iterable, TextIO, Any

from paddle.downloader.config import Config, FileType
from paddle.downloader.models import SimplifiedTrack, Playlist, PlaylistTrack


class RecordWriter:
    w: "_csv._writer"
    f: TextIO

    def __init__(self, config: Config, table_name: str, column_names: Iterable[str]):
        match config.file_type:
            case FileType.csv:
                self.f = open(config.output_dir / f"{table_name}.csv", "wt")
            case FileType.csvgz:
                self.f = gzip.open(config.output_dir / f"{table_name}.csv.gz", "wt")
        self.w = csv.writer(self.f)
        self.w.writerow(column_names)

    def writerow(self, row: Iterable[Any]):
        self.w.writerow(row)

    def close(self):
        self.f.close()


class Builder(metaclass=ABCMeta):
    def add_playlist(self, playlist: Playlist, tracks: List[PlaylistTrack]):
        pass

    def add_track(self, playlist: Playlist, playlist_track: PlaylistTrack):
        pass

    @abstractmethod
    def close(self):
        raise NotImplementedError


class FileBuilder(Builder):
    w: "_csv._writer"

    def close(self):
        self.w.close()


class CategoryPlaylistRecords(FileBuilder):
    ids: set[str]

    def __init__(self, config: Config):
        self.w = RecordWriter(
            config=config,
            table_name="category_playlists_records",
            column_names=(
                "description",
                "name",
                "id",
                "tracks_url",
                "total_tracks",
                "snapshot_id",
            ),
        )
        self.ids = set()

    def add_playlist(self, playlist: Playlist, tracks: List[PlaylistTrack]):
        sid = playlist.id
        if sid in self.ids:
            return
        self.ids.add(sid)
        self.w.writerow(
            (
                playlist.description,
                playlist.name,
                playlist.id,
                f"{playlist.uri}/tracks",
                len(tracks),
                playlist.snapshot_id,
            )
        )


class PlaylistRecords(FileBuilder):
    ids: set[str]

    def __init__(self, config: Config):
        self.w = RecordWriter(
            config=config,
            table_name="playlist_records",
            column_names=("id", "followers"),
        )
        self.ids = set()

    def add_playlist(self, playlist: Playlist, _tracks: List[PlaylistTrack]):
        sid = playlist.id
        if sid in self.ids:
            return
        self.ids.add(sid)
        self.w.writerow((playlist.id, playlist.followers.total))


class TracksRecords(FileBuilder):
    ids: set[str]

    def __init__(self, config: Config):
        self.w = RecordWriter(
            config=config,
            table_name="tracks_records",
            column_names=("album_type", "id", "name", "popularity", "uri"),
        )
        self.ids = set()

    def add_track(self, playlist: Playlist, playlist_track: PlaylistTrack):
        track = playlist_track.track
        if isinstance(track, SimplifiedTrack):
            sid = track.id
            if sid in self.ids:
                return
            self.ids.add(sid)
            self.w.writerow(
                (track.album.type, track.id, track.name, track.popularity, track.uri)
            )


class PlaylistTrackIdRecords(FileBuilder):
    ids: set[(str, str)]

    def __init__(self, config: Config):
        self.w = RecordWriter(
            config=config,
            table_name="playlist_track_id_records",
            column_names=(
                "playlist_id",
                "playlist_added_at",
                "track_id",
            ),
        )
        self.ids = set()

    def add_track(self, playlist: Playlist, playlist_track: PlaylistTrack):
        track = playlist_track.track
        if isinstance(track, SimplifiedTrack):
            sid = (playlist.id, track.id)
            if sid in self.ids:
                return
            self.ids.add(sid)
            self.w.writerow(
                (playlist.id, playlist_track.added_at.isoformat(), track.id)
            )


class TrackArtistIdRecords(FileBuilder):
    ids: set[(str, str)]

    def __init__(self, config: Config):
        self.w = RecordWriter(
            config=config,
            table_name="track_artist_id_records",
            column_names=("track_id", "artist_id"),
        )
        self.ids = set()

    def add_track(self, playlist: Playlist, playlist_track: PlaylistTrack):
        track = playlist_track.track
        if isinstance(track, SimplifiedTrack):
            for artist in track.artists:
                sid = (track.id, artist.id)
                if sid in self.ids:
                    return
                self.ids.add(sid)
                self.w.writerow((track.id, artist.id))


class ArtistsRecords(FileBuilder):
    ids: set[str]

    def __init__(self, config: Config):
        self.w = RecordWriter(
            config=config, table_name="artists_records", column_names=("id", "name")
        )
        self.ids = set()

    def add_track(self, playlist: Playlist, playlist_track: PlaylistTrack):
        track = playlist_track.track
        if isinstance(track, SimplifiedTrack):
            for artist in track.artists:
                sid = artist.id
                if sid in self.ids:
                    return
                self.ids.add(sid)
                self.w.writerow((artist.id, artist.name))


class RecordBuilder(Builder):
    builders: List[Builder]

    def __init__(self, builders: List[Builder]):
        self.builders = builders

    def add_playlist(self, playlist: Playlist, tracks: List[PlaylistTrack]):
        for builder in self.builders:
            builder.add_playlist(playlist, tracks)

    def add_track(self, playlist: Playlist, playlist_track: PlaylistTrack):
        for builder in self.builders:
            builder.add_track(playlist, playlist_track)

    def close(self):
        for builder in self.builders:
            builder.close()
