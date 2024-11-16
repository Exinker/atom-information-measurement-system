import functools
import os

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

    def __call__(self, __filepath: XMLPath, *args, **kwargs):
        key = hash(__filepath)

        if key not in self.cache:
            self.cache[key] = self.func(self, __filepath, *args, **kwargs)

            if bool(os.environ['DEBUG']):
                print(f'parsed: {__filepath}')

        return self.cache[key]


def cache(func):
    cache = ParserCache()

    @functools.wraps(func)
    def wrapped(__filepath: XMLPath, *args, **kwargs):
        key = hash(__filepath)

        if key not in cache.storage:
            cache.storage[key] = func(__filepath, *args, **kwargs)

            if bool(os.environ['DEBUG']):
                print(f'parsed: {__filepath}')

        return cache.storage[key]

    return wrapped
