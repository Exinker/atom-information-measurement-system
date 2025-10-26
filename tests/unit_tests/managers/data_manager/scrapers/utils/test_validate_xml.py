from typing import Any, Callable, Mapping

import pytest

from aims.managers.data_manager.scrapers.utils.validators import validate_xml
from aims.managers.data_manager.types import XML


def test_validate_xml(
    fake_xml_factory: Callable[[Mapping[str, Mapping[str, Any]] | None], XML],
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
        'probes',
        'columns',
    ],
)
def test_validate_xml_invalid(
    exclude: str,
    fake_xml_factory: Callable[[Mapping[str, Mapping[str, Any]] | None], XML],
):
    xml = fake_xml_factory(exclude=exclude)

    status = validate_xml(xml)

    assert status is False
