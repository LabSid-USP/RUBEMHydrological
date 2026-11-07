"""Validate metadata.txt against plugins.qgis.org required fields."""

from __future__ import annotations

import configparser
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration

ROOT = Path(__file__).resolve().parents[2]
REQUIRED_METADATA = (
    "name",
    "description",
    "version",
    "qgisMinimumVersion",
    "email",
    "author",
)


def test_metadata_has_plugins_qgis_org_required_fields() -> None:
    """plugins.qgis.org rejects uploads missing these general keys."""
    path = ROOT / "metadata.txt"
    parser = configparser.ConfigParser()
    parser.optionxform = str
    parser.read(path)
    assert parser.has_section("general"), f"no [general] in {path}"
    metadata = dict(parser.items("general"))
    for key in REQUIRED_METADATA:
        assert key in metadata, f'missing metadata "{key}" in {path}'
