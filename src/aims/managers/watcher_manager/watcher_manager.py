import os
from typing import Callable

from watchdog.events import FileSystemEvent
from watchdog.observers import Observer

from aims.managers.data_manager import DataManager
from aims.managers.data_manager.cache import CacheManager
from aims.managers.watcher_manager.handlers import WatcherEventHandler
from spectrumapp.types import DirPath


class WatcherManager:

    def __init__(
        self,
        data_manager: DataManager,
        callback: Callable,
    ) -> None:

        self.data_manager = data_manager
        self.callback = callback

        self.observer = None

    def setup(self, path: DirPath) -> None:

        if self.observer:
            self.observer.stop()

        self.observer = Observer()
        self.observer.schedule(
            event_handler=WatcherEventHandler(callback=self.middleware),
            path=os.path.abspath(
                path=path,
            ),
            recursive=True,
        )
        self.observer.start()

    def middleware(self, event: FileSystemEvent | None = None) -> None:

        if event.event_type == 'modified':
            CacheManager.remove(
                filepath=event.src_path,
            )

        self.callback()
