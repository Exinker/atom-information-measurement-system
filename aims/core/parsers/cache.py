import functools

from aims.core.types import XMLPath


class ParserCache:
    instance = None
    storage = {}

    def __new__(cls) -> 'ParserCache':
        if cls.instance is None:
            cls.instance = super().__new__(cls)

        return cls.instance

    @classmethod
    def clear(cls) -> None:
        cls.storage = {}


def cache(func):
    cache = ParserCache()

    @functools.wraps(func)
    def wrapped(__filepath: XMLPath, *args, **kwargs):
        key = hash(__filepath)

        if key not in cache.storage:
            cache.storage[key] = func(__filepath, *args, **kwargs)

        return cache.storage[key]

    return wrapped
