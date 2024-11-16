from dataclasses import dataclass

from aims.core.types import AnalysisName, XML


@dataclass
class AtomMeta:
    organization_name: str
    device_name: str
    user_name: str
    analysis_name: AnalysisName

    @classmethod
    def parse_xml(cls, xml: XML) -> 'AtomMeta':  # TODO: add MetaParser
        """Get recorded meta from Atom's .xml file."""

        # parse
        organization_name = xml.find('titul').find('organization').text
        device_name = xml.find('titul').find('device').text
        user_name = xml.find('titul').find('user').text
        analysis_name = xml.find('titul').find('aname').text

        return cls(
            organization_name=organization_name,
            device_name=device_name,
            user_name=user_name,
            analysis_name=analysis_name,
        )
