from typing import Any, Callable, Mapping

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from aims.configs import DEFAULT_SEP
from aims.managers.data_manager.scrapers.utils.scrapers import (
    DEFAULT_PROBES,
    scrape_probes,
)
from aims.managers.data_manager.types import XML


@pytest.fixture
def sep() -> str:
    return DEFAULT_SEP


@pytest.mark.xfail()
def test_scrape_probes(
    sep: str,
    fake_xml_factory: Callable[[Mapping[str, Mapping[str, Any]] | None], XML],
):
    xml = fake_xml_factory()

    results = scrape_probes(xml, sep=sep)

    assert results == ''


def test_scrape_probes_empty(
    sep: str,
    fake_xml_factory: Callable[[Mapping[str, Mapping[str, Any]] | None], XML],
):
    xml = fake_xml_factory()

    results = scrape_probes(xml, sep=sep)

    assert isinstance(results, pd.DataFrame)
    assert_frame_equal(results, DEFAULT_PROBES)


@pytest.mark.xfail()
def test_scrape_probes_with_attribure_error(
    sep: str,
    fake_xml_factory: Callable[[Mapping[str, Mapping[str, Any]] | None], XML],
):
    xml = fake_xml_factory()
    parent = xml.find('.//aname/..')
    parent.remove(parent.find('aname'))

    results = scrape_probes(xml, sep=sep)

    assert isinstance(results, pd.DataFrame)
    assert_frame_equal(results, DEFAULT_PROBES)
