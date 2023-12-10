import logging
from typing import Any, TypeVar

from common.cache import BaseDataCacheCollector
from damri.services.base import BaseService

CacheCollector = TypeVar("CacheCollector", bound=BaseDataCacheCollector)

logger = logging.getLogger(__name__)


class BaseCacheTaskService(BaseService):
    """
    Collect(periodically) and store data by key for specific time in cache.
    """

    CACHE_SERVICE = CacheCollector

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        self.collect()

    def collect(self):
        logger.info(f"Collecting data {self.__class__.__name__}")
        self._collect()
        logger.info(f"Collected data {self.__class__.__name__}")

    def _collect(self):
        self.CACHE_SERVICE.set_data()
