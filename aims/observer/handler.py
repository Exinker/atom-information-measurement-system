import logging
import os
from logging import Logger
from typing import Callable, Literal

from PySide6 import QtCore
from watchdog.events import FileSystemEvent, FileSystemEventHandler


LOGGER = logging.getLogger('app')


class Bridge(QtCore.QObject):
    updated = QtCore.Signal(FileSystemEvent)


class ObserverEventHandler(FileSystemEventHandler):

    def __init__(self, callback: Callable):
        self.bridge = Bridge()
        self.bridge.updated.connect(callback)

    def on_created(self, event):
        self._on_emitted(event, kind='created')

    def on_modified(self, event: FileSystemEvent):
        self._on_emitted(event, kind='modified')

    def _on_emitted(self, event: FileSystemEvent, kind: Literal['created', 'modified']):

        if event.is_directory:
            pass  # TODO: может ли добавляться папка?

        else:
            filedir, filename = os.path.split(event.src_path)

            if filename.endswith('.xml'):
                LOGGER.info('Observer: %s file %s', kind, event.src_path)

                self.bridge.updated.emit(event)
