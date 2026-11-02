#!/usr/bin/env python3
"""Build a QGIS plugin zip with one archive root.

QGIS loads the plugin from the top-level directory inside the zip. Metadata,
``__init__.py``, the ``plugin`` package, generated resources and the RUBEM
submodule therefore share the root ``rubem_hydrological``.
"""

from __future__ import annotations

import os
import zipfile
from pathlib import Path

ARCHIVE_ROOT = "rubem_hydrological"
INCLUDE_SUFFIXES = {
    ".py",
    ".ui",
    ".qrc",
    ".rcc",
    ".png",
    ".svg",
    ".jpg",
    ".qm",
    ".txt",
    ".md",
}
EXCLUDE_DIRS = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".git",
    "test",
    "tests",
}


def archive_member(root: Path, path: Path) -> str:
    """Return the zip path of ``path`` under the single plugin root."""
    return f"{ARCHIVE_ROOT}/{path.relative_to(root).as_posix()}"


def iter_plugin_files(root: Path):
    """Yield files the installed plugin needs at runtime."""
    plugin_dir = root / "plugin"
    for dirpath, dirnames, filenames in os.walk(plugin_dir):
        dirnames[:] = [name for name in dirnames if name not in EXCLUDE_DIRS]
        for name in filenames:
            path = Path(dirpath) / name
            if path.suffix.lower() in INCLUDE_SUFFIXES:
                yield path
    for name in ("metadata.txt", "__init__.py", "LICENSE.md", "CHANGELOG.md"):
        path = root / name
        if path.is_file():
            yield path
    images = root / "images"
    if images.is_dir():
        for path in images.rglob("*"):
            if path.is_file() and path.suffix.lower() in INCLUDE_SUFFIXES:
                yield path
    model = root / "external" / "rubem-model" / "rubem"
    if model.is_dir():
        for dirpath, dirnames, filenames in os.walk(model):
            dirnames[:] = [name for name in dirnames if name not in EXCLUDE_DIRS]
            for name in filenames:
                path = Path(dirpath) / name
                if path.suffix.lower() == ".py":
                    yield path


def build_plugin() -> None:
    """Write ``dist/rubem_hydrological.zip``."""
    root = Path(__file__).resolve().parent.parent
    dist = root / "dist"
    dist.mkdir(exist_ok=True)
    zip_path = dist / f"{ARCHIVE_ROOT}.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in iter_plugin_files(root):
            archive.write(path, archive_member(root, path))
    print(f"Package created: {zip_path}")


if __name__ == "__main__":
    build_plugin()
