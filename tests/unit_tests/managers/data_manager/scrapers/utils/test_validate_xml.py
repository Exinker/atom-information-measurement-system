import dataclasses
import os
import uuid
from dataclasses import dataclass, field
from functools import partial
from pathlib import Path
from typing import Any, Callable, Literal, Mapping
from xml.etree.ElementTree import Element, SubElement

import pytest
from faker import Faker

from aims.managers.data_manager.scrapers.validators import validate_xml
from aims.managers.data_manager.types import XML
from spectrumapp.types import FilePath


fake = Faker('ru_RU')


@dataclass
class TitulData:
    aname: str = field(default_factory=fake.user_name)
    user: Literal['Лаборант'] = field(default='Лаборант')
    date: str = field(default='')
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
        fields: Mapping[str, Any],
        exclude: str,
    ) -> XML:

        for key, item in fields.items():
            if key != exclude:
                element = SubElement(__root, key)
                if isinstance(item, dict):
                    element = build(
                        element,
                        fields=item,
                        exclude=exclude,
                    )
                else:
                    element.text = str(item)

        return __root

    def wrapper(
        exclude: str = '',
    ) -> XML:

        if 'analysis' == exclude:
            return Element('')

        data = AnalysisData()
        return build(
            Element('analysis'),
            fields=dataclasses.asdict(data),
            exclude=exclude,
        )

    return wrapper


def test_validate_xml(
    fake_xml_factory: Callable[[str], XML],
):
    xml = fake_xml_factory()

    status = validate_xml(xml)

    assert status is True


@pytest.mark.parametrize(
    'exclude', [
        'analysis',
        # 'guid',
        'file',
        'titul',
        'aname',
        'user',
        'date',
        'organization',
        'device',
        'probes',
        'columns',
    ],
)
def test_validate_xml_invalid(
    exclude: str,
    fake_xml_factory: Callable[[str], XML],
):
    xml = fake_xml_factory(exclude=exclude)

    status = validate_xml(xml)

    assert status is False
