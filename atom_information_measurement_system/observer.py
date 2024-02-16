
import logging
import os
import time
import queue
from logging import Logger
from multiprocessing import Process, Queue
from typing import Callable

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent, LoggingEventHandler

from core.config import Config


class XMLEventHandler(FileSystemEventHandler):

    def __init__(self, q: Queue, logger: Logger = None):
        self.logger = logger or logging.root
        self.q = q

    def on_modified(self, event: FileSystemEvent):
        # FIXME: check double event???

        if not event.is_directory:
            filedir, filename = os.path.split(event.src_path)
            if filename.endswith('.xml'):
                print(event)

                self.logger.info("observer: modified file: %s", event.src_path)
                self.q.put(event.src_path)


def work(func: Callable, q: Queue):

    while True:
        try:
            path = q.get(timeout=0)

            func(path)

        except queue.Empty:
            time.sleep(1)


def fprint(path):
    print(f'print from worker: {path}')


if __name__ == '__main__':
    config = Config.from_json()
    q = Queue()

    # observer
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    observer = Observer()
    observer.schedule(XMLEventHandler(q), path=config.tracked_path, recursive=True)
    observer.start()

    # worker
    worker = Process(targets=work, kwargs={'func': fprint, 'q': q}, daemon=True)
    worker.start()

    # event loop
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        observer.join()

        worker.join()
