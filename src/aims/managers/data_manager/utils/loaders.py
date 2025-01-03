import logging
import xml.etree.ElementTree as ElementTree

from aims.managers.data_manager.types import XML, XMLPath


LOGGER = logging.getLogger('app')


def load_xml(filepath: XMLPath) -> XML | None:
    """Load `xml` element object from file for a given `filepath`."""

    LOGGER.info('Load XML file: %r', filepath)

    try:
        tree = ElementTree.parse(filepath)
        xml = tree.getroot()
    except Exception as error:
        LOGGER.warning('File load failed with %s: %s', type(error).__name__, error)
        return None
    else:
        return xml
