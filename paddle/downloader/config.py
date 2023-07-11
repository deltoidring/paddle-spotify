from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


@dataclass
class SpotifyConfig:
    client_id: str
    client_secret: str
    base_url = "https://api.spotify.com/v1/"
    auth_url = "https://accounts.spotify.com/api/token"
    retry_max_retries = 5
    retry_backoff = 0.1
    rate_limit_bucket_size_seconds: int = 30
    # https://developer.spotify.com/documentation/web-api/concepts/rate-limits doesn't specify
    # a rate limit, but we try to be nice API citizens
    rate_limit_requests_per_bucket: int = 100
    rate_limit_max_retries = 3


class FileType(Enum):
    csv = "csv"
    csvgz = "csv.gz"

    def __str__(self):
        return self.name.lower()

    @staticmethod
    def parse(s: str):
        return FileType[s]


@dataclass
class Config:
    spotify: SpotifyConfig
    output_dir: Path = Path("output")
    category_ids: list[str] = field(default_factory=lambda: ["latin"])
    file_type: FileType = FileType.csvgz
