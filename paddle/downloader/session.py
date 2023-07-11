import logging
import time
from dataclasses import dataclass
from typing import Dict
from urllib.parse import urlparse

import requests
from pyrate_limiter import RequestRate, Limiter
from requests import Session
from requests_ratelimiter import LimiterAdapter
from urllib3 import Retry

from paddle.downloader.config import SpotifyConfig

logger = logging.getLogger(__name__)


@dataclass
class SpotifySessionCreator:
    """
    Creates a Session object with rate-limiting and retries and the spotify base URL.
    """

    config: SpotifyConfig

    def create_session(self) -> Session:
        session = SessionWithBase(config=self.config)
        session.headers.update(self.__get_bearer_token_headers())
        thirty_seconds_rate = RequestRate(
            limit=self.config.rate_limit_requests_per_bucket,
            interval=self.config.rate_limit_bucket_size_seconds,
        )
        limiter = Limiter(thirty_seconds_rate)
        retries = Retry(
            total=self.config.retry_max_retries,
            backoff_factor=self.config.retry_backoff,
            status_forcelist=[500, 502, 503, 504],
        )
        adapter = LimiterAdapter(limiter=limiter, max_retries=retries)
        session.mount("https://", adapter)
        return session

    def __get_app_access_token(self) -> str:
        """
        Returns: an access token to be used in downstream API calls as Authorization headers
        """
        response = requests.post(
            url=self.config.auth_url,
            data={
                "grant_type": "client_credentials",
                "client_id": self.config.client_id,
                "client_secret": self.config.client_secret,
            },
        )
        response.raise_for_status()
        return response.json()["access_token"]

    def __get_bearer_token_headers(self) -> Dict[str, str]:
        access_token = self.__get_app_access_token()
        return {"Authorization": f"Bearer {access_token}"}


class SessionWithBase(Session):
    """
    Extension of the requests Session with support for a base URL.
    Additionally, it handles rate-limit errors softly by sleeping for Retry-After seconds.
    """

    config: SpotifyConfig

    def __init__(self, config: SpotifyConfig, *args, **kwargs):
        super(SessionWithBase, self).__init__(*args, **kwargs)
        self.config = config

    def request(self, method: str, url: str, **kwargs) -> requests.Response:
        max_retries = self.config.rate_limit_max_retries
        for retry in range(max_retries):
            url = url if urlparse(url).scheme else self.config.base_url + url
            response = super(SessionWithBase, self).request(method, url, **kwargs)
            if response.status_code != 429:
                return response
            retry_after = int(
                response.headers.get(
                    "Retry-After", self.config.rate_limit_bucket_size_seconds
                )
            )
            logger.warning(f"Rate-limit encountered with Retry-After: {retry_after}")
            time.sleep(retry_after)
        raise AssertionError(f"Still received rate-limit after {max_retries}")


def get_response_dict(response: requests.Response) -> dict[any]:
    response.raise_for_status()
    data = response.json()
    assert isinstance(data, dict)
    return data
