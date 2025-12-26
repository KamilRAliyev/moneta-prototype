#!/usr/bin/env python3
"""Fix dateinfer package broken imports.

This script fixes known import issues in dateinfer 0.1.1 package.
The package has incorrect absolute imports that should be relative imports.
"""

import os
import re
import sys
from pathlib import Path


def find_site_packages():
    """Find site-packages directory."""
    for path in sys.path:
        if "site-packages" in path:
            return Path(path)
    return None


def fix_dateinfer():
    """Fix dateinfer package imports."""
    site_packages = find_site_packages()
    if not site_packages:
        print("ERROR: Could not find site-packages directory", file=sys.stderr)
        return False

    dateinfer_dir = site_packages / "dateinfer"
    if not dateinfer_dir.exists():
        print("ERROR: dateinfer package not found", file=sys.stderr)
        return False

    # Fix __init__.py
    init_file = dateinfer_dir / "__init__.py"
    if init_file.exists():
        content = init_file.read_text()
        if "from infer import infer" in content:
            init_file.write_text("from .infer import infer\n")
            print(f"Fixed {init_file}")

    # Fix infer.py
    infer_file = dateinfer_dir / "infer.py"
    if infer_file.exists():
        content = infer_file.read_text()
        original = content
        content = re.sub(
            r"^from date_elements import",
            "from .date_elements import",
            content,
            flags=re.MULTILINE,
        )
        content = re.sub(
            r"^from ruleproc import",
            "from .ruleproc import",
            content,
            flags=re.MULTILINE,
        )
        if content != original:
            infer_file.write_text(content)
            print(f"Fixed {infer_file}")

    # Fix ruleproc.py
    ruleproc_file = dateinfer_dir / "ruleproc.py"
    if ruleproc_file.exists():
        content = ruleproc_file.read_text()
        original = content
        content = re.sub(
            r"^from date_elements import",
            "from .date_elements import",
            content,
            flags=re.MULTILINE,
        )
        if content != original:
            ruleproc_file.write_text(content)
            print(f"Fixed {ruleproc_file}")

    # Verify fix
    try:
        import dateinfer

        result = dateinfer.infer(["2024-01-01", "2024-02-01"])
        print(f"✓ dateinfer is working! Test result: {result}")
        return True
    except Exception as e:
        print(f"ERROR: dateinfer still not working: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    success = fix_dateinfer()
    sys.exit(0 if success else 1)
