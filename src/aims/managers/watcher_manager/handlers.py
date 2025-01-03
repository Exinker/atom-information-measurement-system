import logging
import os
from typing import Callable, Literal

from PySide6 import QtCore
from watchdog.events import FileSystemEvent, FileSystemEventHandler


LOGGER = logging.getLogger('app')


class Bridge(QtCore.QObject):
    updated = QtCore.Signal(FileSystemEvent)


class WatcherEventHandler(FileSystemEventHandler):

    def __init__(self, callback: Callable):
        self.bridge = Bridge()
        self.bridge.updated.connect(callback)

    def on_created(self, event: FileSystemEvent):
        self._on_emitted(event, kind='created')

    def on_deleted(self, event: FileSystemEvent):
        self._on_emitted(event, kind='deleted')

    def on_modified(self, event: FileSystemEvent):
        self._on_emitted(event, kind='modified')

    def on_moved(self, event: FileSystemEvent):
        self._on_emitted(event, kind='moved')

    def _on_emitted(
        self,
        event: FileSystemEvent,
        kind: Literal['created', 'deleted', 'modified', 'moved'],
    ):
        if event.is_directory:
            return None

        _, filename = os.path.split(event.src_path)
        if filename.endswith('.xml'):
            match kind:
                case 'created' | 'modified':
                    LOGGER.info('Observer: %s file %s', kind, event.src_path)
                    self.bridge.updated.emit(event)
                case _:
                    LOGGER.debug('Observer: %s file %s', kind, event.src_path)
