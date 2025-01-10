from collections.abc import Mapping
from typing import Callable


class FakeSettings:

    def __init__(self, data: Mapping[str, str]) -> None:
        self.data = data

    def value(self, key: str) -> str:
        return self.data[key]


def fake_load_settings(
    data: Mapping[str, str],
) -> Callable[..., FakeSettings]:

    def factory() -> FakeSettings:
        return FakeSettings(data=data)

    return factory
