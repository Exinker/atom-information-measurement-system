from typing import Any, Callable, Mapping
from xml.etree import ElementTree

import pytest

from aims.managers.data_manager.scrapers.utils.scrapers import scrape_analysis_name
from aims.managers.data_manager.types import XML


@pytest.fixture
def aname(
    faker,
) -> str:
    return faker.name()


def test_scrape_analysis_name(
    aname: str,
    fake_xml_factory: Callable[[Mapping[str, Mapping[str, Any]] | None], XML],
):
    xml = fake_xml_factory({
        'titul': {
            'aname': aname,
        },
    })

    results = scrape_analysis_name(xml)

    assert results == aname


def test_scrape_analysis_name_empty(
    fake_xml_factory: Callable[[Mapping[str, Mapping[str, Any]] | None], XML],
):
    xml = fake_xml_factory({
        'titul': {
            'aname': '',
        },
    })

    results = scrape_analysis_name(xml)

    assert results == ''


def test_scrape_analysis_name_with_attribure_error(
    fake_xml_factory: Callable[[Mapping[str, Mapping[str, Any]] | None], XML],
):
    xml = fake_xml_factory()
    parent = xml.find('.//aname/..')
    parent.remove(parent.find('aname'))

    results = scrape_analysis_name(xml)

    assert results == ''
