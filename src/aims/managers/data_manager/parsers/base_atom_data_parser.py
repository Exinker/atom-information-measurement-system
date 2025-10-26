from abc import ABC, abstractmethod

from aims.configs import Config
from aims.managers.data_manager.atom_data import AtomData
from aims.managers.data_manager.types import XMLPath


class AtomDataParserABC(ABC):

    def __init__(self, config: Config):
        self.config = config

    @abstractmethod
    def parse(self, __filepath: XMLPath) -> AtomData:
        """Get recorded data from Atom's .xml file."""

        raise NotImplementedError
