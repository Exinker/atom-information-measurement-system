from dataclasses import dataclass, field

from aims.managers.data_manager.types import AnalysisName, Frame, XML


@dataclass
class AtomMeta:

    organization_name: str
    device_name: str
    user_name: str
    analysis_name: AnalysisName

    @classmethod
    def parse_xml(cls, xml: XML) -> 'AtomMeta':
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


@dataclass
class AtomData:
    meta: Frame
    concentration: Frame
    reference: Frame | None = field(default=None)
    statistics: Frame | None = field(default=None)
