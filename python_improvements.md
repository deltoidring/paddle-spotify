# Future improvements

### Daily evolution of playlists

- introduce `fetched_at` timestamps for the respective tables
- `category_playlist_records` could have a `category_id` with a new `category_records` table
- upsert into a database (e.g. DuckDB) instead of custom CSV writers
- use conditional requests with an ETag to avoid downloading resources that haven't changed

### Python improvements

- use Parquet instead of compressed gzipped (e.g. with `pyarrow`)
- use a Spotify client library (e.g. Spotipy or Tekore)
- add more relations (users, images, available markets, genres, etc.) or fields (e.g. added_by, release_data, is_playable)
- add more objects (e.g. Shows, Episodes)
- re-use pagination logic
- add maximum limit for playlist to prevent infinite playlists
- save snapshots after every X requests or Y playlists
- allow recovery from a snapshot file
- better mechanism for dealing with API errors (e.g. after max_retries instead of raising an exception, the playlist ID could be added to `dead_playlists`)
- introduce soft error handling instead of hard assertions
- add more complicated test cases (e.g. partially corrupt results)
- add more custom types for e.g. the Spotify ID or URI
- check for the expiration of the access token and request new one before expiration

### General improvements

- setup linting
- setup CI actions (e.g. pytest, pre-commit, pylint, mypy)
- add more documentation (especially for the model fields)
- use async for concurrent execution
- use a thread pool for parallel execution
- use httpx instead of requests and go fully async
- using environment variables for secrets is a security risk and discouraged (using a secrets manager or vault is recommended)

### Advanced improvements

- deploy Docker image for automated daily runs
- use a message queue of playlists to fetch for distributed processing
- use a message queue to stream resulting playlists and aggregate over the stream in chunks
