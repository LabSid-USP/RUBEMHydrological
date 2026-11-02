#!/usr/bin/env python3
"""Build script for RUBEM Hydrological plugin package.

This script creates a distributable ZIP file of the plugin.
"""

from __future__ import annotations

import os
import shutil
import zipfile
from pathlib import Path


def build_plugin() -> None:
    """Build the plugin distribution package."""
    print("Building RUBEM Hydrological plugin package...")

    # Define paths
    root_dir = Path(__file__).parent.parent
    plugin_dir = root_dir / "plugin"
    dist_dir = root_dir / "dist"
    build_dir = root_dir / "build"

    # Create dist directory
    dist_dir.mkdir(exist_ok=True)
    build_dir.mkdir(exist_ok=True)

    # Plugin name and output
    plugin_name = "rubem_hydrological"
    zip_path = dist_dir / f"{plugin_name}.zip"

    # Remove old build
    if zip_path.exists():
        zip_path.unlink()
        print(f"Removed old package: {zip_path}")

    # Files to include
    include_patterns = [
        "*.py",
        "*.ui",
        "*.qrc",
        "*.png",
        "*.svg",
        "*.jpg",
        "*.qm",
        "*.txt",
        "*.md",
    ]

    # Directories to exclude
    exclude_dirs = [
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "test",
        "tests",
    ]

    print(f"Creating package: {zip_path}")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        # Add plugin files
        for root, dirs, files in os.walk(plugin_dir):
            # Filter directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            for file in files:
                # Check if file matches include patterns
                if any(file.endswith(pattern[1:]) for pattern in include_patterns):
                    file_path = Path(root) / file
                    arc_path = file_path.relative_to(root_dir.parent)
                    zipf.write(file_path, arc_path)
                    print(f"  Added: {arc_path}")

        # Add metadata and other root files
        root_files = ["metadata.txt", "__init__.py", "LICENSE.md", "CHANGELOG.md"]
        for file in root_files:
            file_path = root_dir / file
            if file_path.exists():
                arc_path = f"rubem_hydrological/{file}"
                zipf.write(file_path, arc_path)
                print(f"  Added: {arc_path}")

        # Add images
        images_dir = root_dir / "images"
        if images_dir.exists():
            for img in images_dir.rglob("*"):
                if img.is_file():
                    arc_path = f"rubem_hydrological/images/{img.relative_to(images_dir)}"
                    zipf.write(img, arc_path)
                    print(f"  Added: {arc_path}")

    print(f"\n✓ Package created successfully: {zip_path}")
    print(f"  Size: {zip_path.stat().st_size / 1024:.2f} KB")


if __name__ == "__main__":
    build_plugin()
