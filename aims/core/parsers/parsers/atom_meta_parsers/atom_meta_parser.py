from aims.core.atom_data import AtomMeta
from aims.core.types import XML


class MetaParser:

    def parse(self, xml: XML) -> AtomMeta:
        """Get recorded meta data from Atom's .xml file."""

        organization_name = xml.find('titul').find('organization').text
        device_name = xml.find('titul').find('device').text
        user_name = xml.find('titul').find('user').text
        analysis_name = xml.find('titul').find('aname').text

        return AtomMeta(
            organization_name=organization_name,
            device_name=device_name,
            user_name=user_name,
            analysis_name=analysis_name,
        )
