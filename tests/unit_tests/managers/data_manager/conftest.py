import dataclasses
import uuid
from dataclasses import dataclass, field
from functools import partial
from typing import Any, Callable, Literal, Mapping, NewType
from xml.etree.ElementTree import Element, SubElement

import pytest
from faker import Faker

from aims.managers.data_manager.types import XML


fake = Faker('ru_RU')


@dataclass
class TitulData:
    aname: str = field(default_factory=fake.user_name)
    user: Literal['Лаборант'] = field(default='Лаборант')
    date: str = field(default='')  # FIXME: change to datetime
    organization: Literal['ВМК'] = field(default='ВМК')
    device: Literal['МАЭС'] = field(default='МАЭС')


@dataclass
class AnalysisData:
    guid: uuid.UUID = field(default_factory=uuid.uuid1)
    file: str = field(default_factory=partial(
        fake.file_path,
        depth=5,
        extension='spd',
        absolute=True,
        file_system_rule='windows',
    ))
    titul: TitulData = field(default_factory=TitulData)
    probes: str = field(default='')
    columns: str = field(default='')


@pytest.fixture
def fake_xml_factory() -> Callable[[str], XML]:

    def build(
        __root: XML,
        fields: Mapping[str, Mapping[str, Any]],
    ) -> XML:

        for _tag, _fields in fields.items():

            element = SubElement(__root, _tag)
            if isinstance(_fields, dict):
                element = build(
                    element,
                    fields=_fields,
                )

            elif isinstance(_fields, list):
                pass

            else:
                element.text = str(_fields)

        return __root

    def inner(
        fields: Mapping[str, Mapping[str, Any]] | None = None,
        exclude: Literal['analysis', 'file', 'titul', 'probes', 'columns'] | None = None,
    ) -> XML:
        fields = fields or {}

        if 'analysis' == exclude:
            return Element('')

        analysis_data_fields = dataclasses.asdict(AnalysisData())
        for _tag, _fields in fields.items():
            analysis_data_fields[_tag].update(_fields)

        if exclude in analysis_data_fields:
            del analysis_data_fields[exclude]

        return build(
            Element('analysis'),
            fields=analysis_data_fields,
        )

    return inner
