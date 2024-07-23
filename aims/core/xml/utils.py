import xml.etree.ElementTree as ElementTree

from aims.core.types import XML, XMLPath


def load_xml(filepath: XMLPath) -> XML | None:
    """Load `xml` element object from file for a given `filepath`."""

    try:
        tree = ElementTree.parse(filepath)
        xml = tree.getroot()

        return xml

    except Exception:
        return None


def validate_xml(xml: XML | None) -> bool:
    """Validate `xml` to simplest cases."""

    if xml is None:
        return False

    # check analysis
    if xml.tag != 'analysis':
        return False

    # check titul
    titul = xml.find('titul')
    if titul is None:
        return False

    if any(titul.find(tag) is None for tag in ('organization', 'device', 'user', 'date', 'aname')):
        return False

    # check probes
    probes = xml.find('probes')
    if probes is None:
        return False

    # check columns
    columns = xml.find('columns')
    if columns is None:
        return False

    #
    return True
