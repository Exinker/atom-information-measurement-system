import functools
import logging
from collections import defaultdict

from aims.core.types import XMLPath


LOGGER = logging.getLogger('app')


class CacheManager:
    storeges = defaultdict(dict)

    def __init__(self, field: str) -> None:
        self.storage = self.storeges[field]

    @classmethod
    def remove(cls, filepath: str | None = None) -> None:
        key = filepath

        for field in cls.storeges.keys():
            if key in cls.storeges[field]:
                LOGGER.info('Remove from %s cache %s.', field, filepath)
                del cls.storeges[field][key]

    @classmethod
    def clear(cls) -> None:

        for field in cls.storeges.keys():
            LOGGER.info('Clear %s cache.', field)
            cls.storeges[field].clear()


def cache(cache: CacheManager):

    def inner(func):

        @functools.wraps(func)
        def wrapped(__filepath: XMLPath, *args, **kwargs):
            key = __filepath

            if key not in cache.storage:
                cache.storage[key] = func(__filepath, *args, **kwargs)

            return cache.storage[key]

        return wrapped
    return inner
