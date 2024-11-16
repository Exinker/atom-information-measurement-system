from abc import ABC, abstractmethod

from aims.config import Config
from aims.core.data import AtomData
from aims.core.types import XMLPath


class DataParserABC(ABC):

    def __init__(self, config: Config):
        self.config = config

    @abstractmethod
    def parse(self, __filepath: XMLPath) -> AtomData:
        """Get recorded data from Atom's .xml file."""

        raise NotImplementedError
