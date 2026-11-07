"""Cross-platform path helpers used by series / project resolution."""

from __future__ import annotations

import os

import pytest

from plugin.utils.series import getFirstFileNameMapSeries, splitDirFilePrefix

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    "path,expected_dir",
    [
        ("etp00000.001", "./"),
        ("/etp00000.001", "./"),
        ("//etp00000.001", "./"),
        ("data/etp/etp00000.001", "data/etp/"),
    ],
)
def test_split_dir_file_prefix_never_uses_filesystem_root(
    path: str, expected_dir: str
) -> None:
    """Bare names and root-like splits become ``./``, never ``/`` alone."""
    directory, prefix = splitDirFilePrefix(path)
    assert directory == expected_dir
    assert prefix == "etp"


def test_get_first_map_series_joins_directory_and_respects_prefix(
    tmp_path,
) -> None:
    """Directory + prefix filter must not treat the folder as a file prefix."""
    series_dir = tmp_path / "landuse"
    series_dir.mkdir()
    (series_dir / "luc00000.001").write_text("a", encoding="utf-8")
    (series_dir / "etp00000.001").write_text("b", encoding="utf-8")
    found = getFirstFileNameMapSeries(str(series_dir), prefix="luc")
    assert os.path.basename(found).startswith("luc")
