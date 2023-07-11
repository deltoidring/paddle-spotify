# Paddle Spotify Downloader

## Setup

1) [Install Poetry through the official installer](https://python-poetry.org/docs/)

2) Set up a new virtualenv with Poetry:

```sh
poetry install
```

For convenience a `requirements.txt` has been exported from poetry. In a non-poetry environment, the dependencies can be installed with:

```sh
pip install -r requirements.txt
```

## Downloader

By default, the downloader will download all playlists of the [category `latin`][category-latin] into the `output` directory and create these tables as `.csv.gz` files:
- `artists_records.csv.gz`
- `category_playlists_records.csv.gz`
- `playlist_records.csv.gz`
- `playlist_track_id_records.csv.gz`
- `track_artist_id_records.csv.gz`
- `tracks_records.csv.gz`

### Run local

The downloader can be run locally with e.g. Poetry:

```sh
poetry run downloader
```

Or directly as Python module:

```sh
python -m paddle.downloader
```

With different arguments:

```sh
poetry run downloader -o my_output -f csv
```

### Run via Docker

```sh
./run.sh
```

The same arguments can be passed as well:

```sh
./run.sh -o my_output -f csv
```

### Options

```sh
usage: spotify_downloader [-h] [-o OUTPUT] [-f {csv,csvgz}] [-c CATEGORY [CATEGORY ...]]
                          [--rate-limit RATE_LIMIT]

Downloads playlists of a given category from Spotify

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output directory (default: output)
  -f {csv,csvgz}, --file-type {csv,csvgz}
                        Output filetype (default: csvgz)
  -c CATEGORY [CATEGORY ...], --category CATEGORY [CATEGORY ...]
                        Categories to download (default: ['latin'])
  --rate-limit RATE_LIMIT
                        Maximum allowed requests / 50 seconds bucket (default: 50)
```

## Tests

Tests can be run with:

```sh
poetry run pytest
```

## Install pre-commit hook

The pre-commit hooks can be installed with:

```sh
pre-commit install
```

[category-latin]: https://open.spotify.com/genre/latin
