from logging import debug, error, warning
from typing import Optional
from urllib.parse import urlparse
from urllib.request import urlopen

from prometheus_client import Counter, Summary

from .mixin_basecache import BaseCacheMixin

AVATAR_CACHE_MISS = Counter("avatar_cache_miss", "Number of cache misses for avatar")
AVATAR_CACHE_HIT = Counter("avatar_cache_hit", "Number of cache hits for avatar")
AVATAR_CACHE_STALE = Counter(
    "avatar_cache_stale", "Number of times stale cache was used for avatar"
)
AVATAR_DOWNLOAD_TIME = Summary("avatar_download_time", "Time spent downloading avatar")


class AvatarCacheMixin(BaseCacheMixin):
    """
    Mixin for handling avatar caching and downloading with diskcache.
    """

    def __init__(
        self,
        url_template: str,
        cache_dir: str = "avatar",
        cache_ttl: int = 2592000,
        cache_max_size: int = 10737418240,
        cache_max_age: int = 7776000,
    ):
        super().__init__(cache_dir, cache_ttl, cache_max_size, cache_max_age)
        self.url_template = url_template

    def _avatar_get(self, character_id: int) -> bytes:
        """
        Retrieves avatar from cache if valid, otherwise downloads and caches it.

        Args:
            character_id (int): Unique character identifier.

        Returns:
            bytes: Avatar image data.
        """
        avatar_data: Optional[bytes] = None
        avatar_url = self.url_template.format(character_id=character_id)
        avatar_data, cache_time = self._cache_get(avatar_url)
        if avatar_data is not None and self._cache_is_fresh(cache_time):
            debug(f"Cache hit for avatar with key '{avatar_url}'")
            AVATAR_CACHE_HIT.inc()
            return avatar_data
        try:
            debug(f"Downloading avatar from URL {avatar_url}")
            avatar_data = self._avatar_download(avatar_url)
            self._cache_set(avatar_url, avatar_data)
            AVATAR_CACHE_MISS.inc()
            return avatar_data
        except Exception as e:
            if avatar_data is None:
                error(f"Failed to download avatar from URL {avatar_url}: {e}")
                return b""
            else:
                warning(f"Returning expired cached avatar for key '{avatar_url}'")
                AVATAR_CACHE_STALE.inc()
                return avatar_data

    @AVATAR_DOWNLOAD_TIME.time()
    def _avatar_download(self, avatar_url: str) -> bytes:
        """
        Downloads the avatar from the specified URL.

        Args:
            avatar_url (str): URL to download the avatar from.

        Returns:
            bytes: Downloaded avatar data.
        """
        parsed_url = urlparse(avatar_url)
        if parsed_url.scheme not in ["http", "https"]:
            raise ValueError(f"Invalid avatar URL scheme: {avatar_url}")
        with urlopen(avatar_url) as response:
            content_type = response.headers.get("Content-Type")
            if not content_type or not content_type.startswith("image/"):
                raise ValueError(f"Invalid content type for avatar: {content_type}")
            avatar_data: bytes = response.read()
            return avatar_data
