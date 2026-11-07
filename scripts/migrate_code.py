#!/usr/bin/env python3
"""Migration helper script for RUBEM Hydrological v2.0.

This script helps with migrating code from v1.x to v2.0 by:
1. Adding type hints to function signatures
2. Converting print statements to logger calls
3. Converting generic exceptions to custom exceptions
4. Updating import statements
5. Formatting code with black

Usage:
    python scripts/migrate_code.py <file_or_directory>
"""

from __future__ import annotations

import argparse
import ast
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


class CodeMigrator:
    """Helper class to migrate code to v2.0 standards."""

    def __init__(self, path: Path, dry_run: bool = False) -> None:
        """Initialize the migrator.

        Args:
            path: Path to file or directory to migrate.
            dry_run: If True, only show what would be changed.
        """
        self.path = path
        self.dry_run = dry_run
        self.changes: list[str] = []

    def migrate(self) -> None:
        """Run all migration steps."""
        if self.path.is_file():
            self._migrate_file(self.path)
        elif self.path.is_dir():
            for py_file in self.path.rglob("*.py"):
                # Skip generated files
                if "generated" in str(py_file):
                    continue
                self._migrate_file(py_file)
        else:
            print(f"Error: {self.path} is not a file or directory")
            sys.exit(1)

        self._print_summary()

    def _migrate_file(self, file_path: Path) -> None:
        """Migrate a single Python file.

        Args:
            file_path: Path to the Python file.
        """
        print(f"\nProcessing: {file_path}")

        content = file_path.read_text(encoding="utf-8")
        original_content = content

        # Apply transformations
        content = self._add_future_annotations(content)
        content = self._update_imports(content)
        content = self._replace_print_with_logger(content)
        content = self._update_exceptions(content)
        content = self._add_type_hints_comments(content)

        if content != original_content:
            if not self.dry_run:
                file_path.write_text(content, encoding="utf-8")
                self._format_with_black(file_path)
                print(f"  ✓ Updated {file_path}")
            else:
                print(f"  ⚠ Would update {file_path}")

            self.changes.append(str(file_path))

    def _add_future_annotations(self, content: str) -> str:
        """Add 'from __future__ import annotations' if not present.

        Args:
            content: File content.

        Returns:
            Updated content.
        """
        if "from __future__ import annotations" in content:
            return content

        # Find position after docstring
        lines = content.split("\n")
        insert_pos = 0

        # Skip encoding declaration
        if lines and lines[0].startswith("#"):
            insert_pos = 1

        # Skip module docstring
        if insert_pos < len(lines) and ('"""' in lines[insert_pos] or "'''" in lines[insert_pos]):
            in_docstring = True
            quote = '"""' if '"""' in lines[insert_pos] else "'''"
            insert_pos += 1
            while insert_pos < len(lines) and in_docstring:
                if quote in lines[insert_pos]:
                    in_docstring = False
                insert_pos += 1

        # Insert import
        lines.insert(insert_pos, "\nfrom __future__ import annotations\n")
        return "\n".join(lines)

    def _update_imports(self, content: str) -> str:
        """Update import statements to use new modules.

        Args:
            content: File content.

        Returns:
            Updated content.
        """
        replacements = [
            # Use new exception classes
            (
                r"^from plugin\.core import",
                "from plugin.core_refactored import",
            ),
            # Add logger import if print is used
        ]

        for pattern, replacement in replacements:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

        return content

    def _replace_print_with_logger(self, content: str) -> str:
        """Replace print statements with logger calls.

        Args:
            content: File content.

        Returns:
            Updated content.
        """
        # Check if content has print statements
        if "print(" not in content:
            return content

        # Add logger import if not present
        if "from plugin.logging import get_logger" not in content:
            # Find where to insert import
            import_section_end = 0
            lines = content.split("\n")

            for i, line in enumerate(lines):
                if line.startswith("import ") or line.startswith("from "):
                    import_section_end = i + 1

            if import_section_end > 0:
                lines.insert(
                    import_section_end,
                    "\nfrom plugin.logging import get_logger\n\nlogger = get_logger(__name__)\n",
                )
                content = "\n".join(lines)

        # Replace print statements
        # This is a simple replacement - manual review recommended
        content = re.sub(
            r'print\((.*?)\)',
            r'logger.info(\1)  # TODO: Review log level',
            content,
        )

        return content

    def _update_exceptions(self, content: str) -> str:
        """Update exception usage to custom exceptions.

        Args:
            content: File content.

        Returns:
            Updated content.
        """
        # Add exceptions import if exceptions are raised
        if "raise ValueError" in content or "raise Exception" in content:
            if "from plugin.exceptions import" not in content:
                import_section_end = 0
                lines = content.split("\n")

                for i, line in enumerate(lines):
                    if line.startswith("import ") or line.startswith("from "):
                        import_section_end = i + 1

                if import_section_end > 0:
                    lines.insert(
                        import_section_end,
                        "\nfrom plugin.exceptions import ValidationError, ConfigurationError, RUBEMException\n",
                    )
                    content = "\n".join(lines)

        # Suggest replacements (commented)
        replacements = [
            (r"raise ValueError\((.*?)\)", r"raise ValidationError(\1)  # TODO: Review exception type"),
            (r"raise Exception\((.*?)\)", r"raise RUBEMException(\1)  # TODO: Review exception type"),
        ]

        for pattern, replacement in replacements:
            content = re.sub(pattern, replacement, content)

        return content

    def _add_type_hints_comments(self, content: str) -> str:
        """Add comments suggesting where to add type hints.

        Args:
            content: File content.

        Returns:
            Updated content.
        """
        # Parse AST to find functions without type hints
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return content

        lines = content.split("\n")

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check if function has return annotation
                if node.returns is None and not node.name.startswith("_"):
                    # Add comment above function
                    line_num = node.lineno - 1
                    if line_num >= 0 and "TODO: Add type hints" not in lines[line_num]:
                        lines[line_num] = (
                            f"    # TODO: Add type hints and return type\n{lines[line_num]}"
                        )

        return "\n".join(lines)

    def _format_with_black(self, file_path: Path) -> None:
        """Format file with black.

        Args:
            file_path: Path to file to format.
        """
        try:
            subprocess.run(
                ["black", str(file_path)],
                check=True,
                capture_output=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"  ⚠ Could not format with black: {file_path}")

    def _print_summary(self) -> None:
        """Print migration summary."""
        print("\n" + "=" * 60)
        print("Migration Summary")
        print("=" * 60)

        if self.changes:
            print(f"\n{'Would update' if self.dry_run else 'Updated'} {len(self.changes)} file(s):")
            for change in self.changes:
                print(f"  - {change}")
        else:
            print("\nNo changes needed!")

        print("\n⚠ Important: Review all TODO comments in migrated files!")
        print("⚠ Especially check:")
        print("  - Log levels (info, debug, warning, error)")
        print("  - Exception types")
        print("  - Type hints accuracy")
        print("\nNext steps:")
        print("  1. Run: ruff check --fix .")
        print("  2. Run: mypy plugin/")
        print("  3. Run: pytest test/")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Migrate RUBEM Hydrological code to v2.0"
    )
    parser.add_argument(
        "path",
        type=Path,
        help="Path to Python file or directory to migrate",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without modifying files",
    )

    args = parser.parse_args()

    if not args.path.exists():
        print(f"Error: {args.path} does not exist")
        sys.exit(1)

    migrator = CodeMigrator(args.path, args.dry_run)
    migrator.migrate()


if __name__ == "__main__":
    main()
