
import logging
import os
from logging import Logger
from typing import Callable, Literal

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent


from PySide6 import QtCore, QtGui, QtWidgets


class Bridge(QtCore.QObject):
    updated = QtCore.Signal(FileSystemEvent)


class ObserverEventHandler(FileSystemEventHandler):

    def __init__(self, callback: Callable, logger: Logger = None):
        self.bridge = Bridge()
        self.bridge.updated.connect(callback)

        self.logger = logger or logging.root

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
                self.logger.info('observer: %s file: %s', kind, event.src_path)

                self.bridge.updated.emit(event)

                # filepath = os.path.join('.', 'tmp.txt')
                # with open(filepath, 'w', encoding='utf-8') as file:
                #     file.write(event.src_path)
