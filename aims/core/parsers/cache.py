import functools
import logging
from collections import defaultdict

from aims.core.types import XMLPath


LOGGER = logging.getLogger('app')


class ParserCache:
    storeges = defaultdict(dict)

    def __init__(self, field: str) -> None:
        self.storage = self.storeges[field]

    @classmethod
    def clear(cls, filepath: str | None = None) -> None:
        fields = cls.storeges.keys()

        if filepath is None:
            LOGGER.info('Clear caches.')
            for field in fields:
                cls.storeges[field].clear()

        else:
            LOGGER.info('Clear caches for: %r.', filepath)

            key = hash(filepath)
            for field in fields:
                if key in cls.storeges[field]:
                    del cls.storeges[field][key]


def cache(cache: ParserCache):

    def inner(func):

        @functools.wraps(func)
        def wrapped(__filepath: XMLPath, *args, **kwargs):
            key = hash(__filepath)
            if key not in cache.storage:
                cache.storage[key] = func(__filepath, *args, **kwargs)

            return cache.storage[key]

        return wrapped
    return inner
