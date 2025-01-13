from collections.abc import Mapping
from typing import Callable

from aims.settings import DEFAULT_SETTING


class FakeSettings:

    def __init__(self, fields: Mapping[str, str]) -> None:

        data = DEFAULT_SETTING
        data.update(**fields)
        self.data = data

    def value(self, key: str) -> str:

        return self.data[key]


def fake_settings_factory(
    fields: Mapping[str, str],
) -> Callable[..., FakeSettings]:

    def factory() -> FakeSettings:
        return FakeSettings(fields=fields)

    return factory
