#!/usr/bin/env python3
"""
Post-process pdoc3 output to fix naming conflicts.

When a module file has the same name as its parent package (e.g., port/port.py),
pdoc3 generates both port/index.md and port/port.md. This causes Docusaurus
routing conflicts where both files try to claim the same route.

This script renames conflicting module files to avoid the issue:
- port/port.md -> port/port_module.md
- Updates links in index.md to point to the renamed file
"""
import re
from pathlib import Path


def fix_naming_conflicts(docs_root: Path):
    """Find and fix naming conflicts where module name == package name."""
    fixed_count = 0

    for index_file in docs_root.rglob("index.md"):
        package_dir = index_file.parent
        package_name = package_dir.name

        # Check if there's a conflicting module file
        module_file = package_dir / f"{package_name}.md"
        if module_file.exists():
            # Rename to avoid conflict
            new_name = package_dir / f"{package_name}_module.md"
            rel_path = module_file.relative_to(docs_root)
            print(f"Fixing conflict: {rel_path} -> {new_name.name}")

            # Read content
            content = module_file.read_text()

            # Write to new location and remove old file
            new_name.write_text(content)
            module_file.unlink()

            # Update index.md to point to the renamed file
            index_content = index_file.read_text()
            # Update markdown links [text](package_name) -> [text](package_name_module)
            index_content = re.sub(
                rf'\[([^\]]+)\]\({package_name}\)',
                rf'[\1]({package_name}_module)',
                index_content
            )
            # Update href attributes href="package_name" -> href="package_name_module"
            index_content = re.sub(
                rf'href="{package_name}"',
                rf'href="{package_name}_module"',
                index_content
            )
            index_file.write_text(index_content)

            fixed_count += 1

    if fixed_count > 0:
        print(f"\nFixed {fixed_count} naming conflict(s)")
    else:
        print("No naming conflicts found")


if __name__ == "__main__":
    # Navigate from py/h2o-engine-manager/docs/ to docs/docs/py/
    script_dir = Path(__file__).parent
    docs_root = script_dir.parent.parent.parent / "docs" / "docs" / "py"

    if not docs_root.exists():
        print(f"Error: Documentation root not found at {docs_root}")
        exit(1)

    print(f"Scanning for naming conflicts in {docs_root}")
    fix_naming_conflicts(docs_root)
