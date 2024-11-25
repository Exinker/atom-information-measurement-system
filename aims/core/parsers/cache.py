import functools
import logging
from collections import defaultdict

from aims.core.types import XMLPath


LOGGER = logging.getLogger('app')


class ParserCache:
    storages = defaultdict(dict)

    def __init__(self, method: str) -> None:
        self.storage = self.storages[method]

    @classmethod
    def clear(cls) -> None:
        methods = cls.storages.keys()

        LOGGER.info('Clear cache storages: %r.', methods)
        for method in methods:
            cls.storages[method].clear()


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
