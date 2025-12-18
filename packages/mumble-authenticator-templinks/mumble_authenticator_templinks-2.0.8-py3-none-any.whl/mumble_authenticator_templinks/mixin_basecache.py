import time
from logging import debug, error, warning
from typing import Any

import diskcache


class BaseCacheMixin:
    """
    Base class for caching with diskcache.
    """

    def __init__(
        self, cache_dir: str, cache_ttl: int, cache_max_size: int, cache_max_age: int
    ) -> None:
        self.cache_ttl = cache_ttl
        self.cache_expire = cache_max_age
        try:
            self.cache = diskcache.Cache(directory=cache_dir, size_limit=cache_max_size)
            debug(
                "The cache is initialized with parameters:"
                f" dir={cache_dir}, ttl={cache_ttl}, max_size={cache_max_size}"
            )
        except Exception as e:
            error(f"Failed to initialize diskcache at {cache_dir}: {e}")
            self.cache = None

    def _cache_get(self, key: str) -> Any:
        if self.cache is None:
            return (None, None)
        try:
            return self.cache.get(key, default=(None, None))
        except Exception as e:
            warning(f"Failed to retrieve data from cache: {e}")
            return (None, None)

    def _cache_set(self, key: str, value: Any) -> None:
        if self.cache is None:
            return
        try:
            self.cache.set(key, (value, time.time()), expire=self.cache_expire)
        except Exception as e:
            warning(f"Failed to store data in cache: {e}")

    def _cache_is_fresh(self, cache_time: int = 0) -> bool:
        return time.time() - cache_time < self.cache_ttl
