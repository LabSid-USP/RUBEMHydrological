"""Build the published zip and smoke-check the archive root."""

from __future__ import annotations

import py_compile
import zipfile
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

ROOT = Path(__file__).resolve().parents[2]


def test_build_plugin_zip_layout_and_core_compiles(tmp_path: Path) -> None:
    """The zip QGIS installs must contain runtime files and no unwired v2 tree."""
    from scripts.build_plugin import ARCHIVE_ROOT, build_plugin

    build_plugin()
    zip_path = ROOT / "dist" / f"{ARCHIVE_ROOT}.zip"
    assert zip_path.is_file()
    extract = tmp_path / "extract"
    extract.mkdir()
    with zipfile.ZipFile(zip_path) as archive:
        archive.extractall(extract)
    plugin_root = extract / ARCHIVE_ROOT
    assert (plugin_root / "metadata.txt").is_file()
    assert (plugin_root / "LICENSE").is_file()
    assert (plugin_root / "README.md").is_file()
    assert (plugin_root / "plugin" / "core.py").is_file()
    assert (plugin_root / "plugin" / "dialog" / "_chrome.py").is_file()
    assert not (plugin_root / "plugin" / "core_refactored.py").exists()
    assert not (plugin_root / "plugin" / "models").exists()
    py_compile.compile(str(plugin_root / "plugin" / "core.py"), doraise=True)
    py_compile.compile(
        str(plugin_root / "plugin" / "dialog" / "_chrome.py"), doraise=True
    )
