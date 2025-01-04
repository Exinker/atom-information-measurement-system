from typing import Any, Mapping


class FakeSettings:

    def __init__(self, data: Mapping[str, Any]) -> None:
        self.data = data

    def get_settings(self, key: str) -> Any:
        return self.data[key]

    def set_settings(self, key: str, value: Any) -> None:
        self.data[key] = value
