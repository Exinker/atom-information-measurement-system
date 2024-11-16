from dataclasses import dataclass

from aims.core.types import Frame

from .meta import AtomMeta


@dataclass
class AtomData:
    meta: AtomMeta
    probes: Frame
    lines: Frame
    prediction: Frame
    reference: Frame
