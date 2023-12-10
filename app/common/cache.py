from typing import Any, Protocol, Type

from common.models import BaseModel
from django.conf import settings
from django.core.cache.backends.redis import DEFAULT_TIMEOUT, RedisCache


class CacheDataLayer(RedisCache):
    def __init__(self, server, params, prefix: str, timeout: int | None = None):
        params.update(
            TIMEOUT=settings.CACHES["default"]["TIMEOUT"] if timeout is None else timeout,
            KEY_PREFIX=params.get("KEY_PREFIX", "") + prefix,
        )
        super().__init__(server, params)

    def get_backend_timeout(self, timeout: int | None = None) -> int | None:
        if timeout == DEFAULT_TIMEOUT:
            timeout = None
        return max(timeout or 0, self.default_timeout)


class DataCacheCollectorProtocol(Protocol):
    pass


# TODO: maybe add singleton
class CoreDataCacheCollector(DataCacheCollectorProtocol):
    PREFIX = ""
    CACHE_DATA_LAYER = CacheDataLayer
    TIMEOUT: int = 0
    ITEM_CLASS = Type[BaseModel]

    def __init__(self) -> None:
        self._cache = self._get_cache()
        if not self.TIMEOUT:
            raise Exception("Timeout must be set")

    def __getattr__(self, name: str) -> Any:
        if name == "get":
            return self.get_data
        if name == "set":
            return self.set_data
        return getattr(self._cache, name)

    def _get_cache(self):
        return self.CACHE_DATA_LAYER(
            settings.CACHES["default"]["LOCATION"], params={}, timeout=self.TIMEOUT, prefix=self.PREFIX
        )

    def _collet_data(self):
        raise NotImplementedError

    def get_key(self):
        raise NotImplementedError

    def get_data(self):
        raise NotImplementedError

    def set_data(self):
        raise NotImplementedError


class BaseDataCacheCollector(CoreDataCacheCollector):
    KEY = ""

    def get_key(self):
        return self.KEY

    def get_data(self):
        if self.has_key(self.get_key()):
            result = self._cache.get(self.get_key())
            if result is not None:
                return result

        self.set_data()
        return self._cache.get(self.get_key())

    def set_data(self):
        data = self._collet_data()
        self._cache.set(self.get_key(), data)


class BaseDataDetailCacheCollector(CoreDataCacheCollector):
    KEY_TEMPLATE = ""

    def _collet_data(self, id):
        raise NotImplementedError

    def get_key(self, id):
        return self.KEY_TEMPLATE.format(id)

    def get_data(self, id):
        if not self.has_key(self.get_key(id)):
            self.set_data(id)

        return self._cache.get(self.get_key(id))

    def set_data(self, id):
        data = self._collet_data(id)
        self._cache.set(self.get_key(id), data)
