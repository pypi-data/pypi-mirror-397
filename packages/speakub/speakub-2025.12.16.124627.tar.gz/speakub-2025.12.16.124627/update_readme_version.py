#!/usr/bin/env python3
"""
Script to update README.md with the current dynamic version.
"""

import re
from datetime import datetime
from speakub._version import get_version


def update_readme_version():
    """Update the version in README.md with current dynamic version."""

    # Get current version
    current_version = get_version()
    current_date = datetime.now().strftime("%Y-%m-%d")

    # Read README.md
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    # Pattern to match version line in history
    version_pattern = r"### Version [\d\.]+\s*\([^)]*\)"

    # Replace with new version
    new_version_line = f"### Version {current_version} (Latest - {current_date})"

    updated_content = re.sub(version_pattern, new_version_line,
                             content, count=1)

    # Write back
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(updated_content)

    print(f"Updated README.md version to {current_version}")


if __name__ == "__main__":
    update_readme_version()
