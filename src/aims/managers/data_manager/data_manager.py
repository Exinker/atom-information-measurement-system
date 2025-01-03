from datetime import datetime

from aims.config import Config
from aims.managers.data_manager.cache import CacheManager
from aims.managers.data_manager.data import (
    DataABC,
    data_factory,
)
from aims.managers.data_manager.data.datum import DatumABC


class DataManager:

    def __init__(self) -> None:
        self._milestone = None
        self._data = None

    @property
    def milestone(self) -> datetime:
        return self._milestone

    @property
    def data(self) -> DataABC:
        return self._data

    @property
    def last_datum(self) -> DatumABC | None:

        if self.data:
            return self.data[-1]

        return None

    def update(self) -> None:

        self._milestone = datetime.now()
        self._data = data_factory(
            milestone=self.milestone,
            config=Config.load(),
        )

    def clear(self) -> None:

        CacheManager.clear()  # to data maanger
