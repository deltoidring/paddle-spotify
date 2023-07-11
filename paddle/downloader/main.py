import argparse
import logging
import os
from pathlib import Path
from typing import Sequence

from paddle.downloader.client import SpotifyClient
from paddle.downloader.config import Config, SpotifyConfig, FileType
from paddle.downloader.records import (
    RecordBuilder,
    CategoryPlaylistRecords,
    PlaylistRecords,
    TracksRecords,
    PlaylistTrackIdRecords,
    TrackArtistIdRecords,
    ArtistsRecords,
)
from paddle.downloader.session import SpotifySessionCreator

logger = logging.getLogger(__name__)


def main(args: Sequence[str] | None = None):
    parser = argparse.ArgumentParser(
        prog="spotify_downloader",
        description="Downloads playlists of a given category from Spotify",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-o", "--output", help="Output directory", default=Config.output_dir, type=Path
    )
    parser.add_argument(
        "-f",
        "--file-type",
        help="Output filetype",
        default=FileType.csvgz,
        type=FileType.parse,
        choices=list(FileType),
    )
    parser.add_argument(
        "-c", "--category", nargs="+", help="Categories to download", default=["latin"]
    )
    parser.add_argument(
        "--rate-limit",
        help=f"Maximum allowed requests / {SpotifyConfig.rate_limit_requests_per_bucket} seconds bucket",
        default=SpotifyConfig.rate_limit_requests_per_bucket,
        type=int,
    )
    result_args = parser.parse_args(args)

    client_id = os.environ["SPOTIFY_CLIENT_ID"]
    client_secret = os.environ["SPOTIFY_CLIENT_SECRET"]
    spotify_config = SpotifyConfig(
        client_id=client_id,
        client_secret=client_secret,
        rate_limit_requests_per_bucket=result_args.rate_limit,
    )
    config = Config(
        spotify=spotify_config,
        output_dir=result_args.output,
        file_type=result_args.file_type,
    )
    run(config)


def run(config: Config):
    logging.basicConfig(level=logging.DEBUG)
    assert (
        config.output_dir.exists()
    ), f"Output directory {config.output_dir} must exist"
    session_creator = SpotifySessionCreator(config=config.spotify)
    session = session_creator.create_session()
    client = SpotifyClient(session=session)
    builder = RecordBuilder(
        builders=[
            CategoryPlaylistRecords(config=config),
            PlaylistRecords(config=config),
            TracksRecords(config=config),
            PlaylistTrackIdRecords(config=config),
            TrackArtistIdRecords(config=config),
            ArtistsRecords(config=config),
        ]
    )
    for category_id in config.category_ids:
        logger.info(f"Starting to process category: '{category_id}'")
        fetch_playlists(client, builder, category_id)
    builder.close()
    logger.info("Finished processing")


def fetch_playlists(client: SpotifyClient, builder: RecordBuilder, category_id: str):
    playlist_ids = set()
    playlists = client.get_playlists(category_id)
    for item in playlists:
        if item.id in playlist_ids:
            logger.info(f"Ignoring duplicate playlist ID: {item.id}")
            continue
        playlist_ids.add(item.id)
        logger.info(f"Fetched playlist ID: {item.id}")
        playlist_client = client.get_playlist(item.id)
        playlist = playlist_client.playlist
        tracks = []
        for track in playlist_client.get_tracks():
            builder.add_track(playlist, track)
            tracks.append(track)
        builder.add_playlist(playlist, tracks)
        logger.info(
            f"Finished processing of playlist ID: {item.id} with {len(tracks)} tracks"
        )
    logger.info(f"Downloaded {len(playlist_ids)} playlists")
