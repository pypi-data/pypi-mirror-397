#!/usr/bin/env python3
"""Complete the release by committing, tagging, and pushing.

Usage:
    python scripts/release.py           # Interactive mode
    python scripts/release.py --commit  # Non-interactive mode
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


def get_current_version() -> str:
    """Get current version from src/adr/__init__.py."""
    init_file = Path("src/adr/__init__.py")
    content = init_file.read_text()
    match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
    if not match:
        print("Error: Could not find __version__ in src/adr/__init__.py")
        sys.exit(1)
    return match.group(1)


def check_working_directory() -> bool:
    """Check if working directory has expected changes."""
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
        check=True,
    )

    changed_files = result.stdout.strip().split("\n")
    expected_files = {"src/adr/__init__.py", "CHANGELOG.md"}

    actual_files = set()
    for line in changed_files:
        if line.strip():
            # Extract filename from status line (e.g., " M filename" or "?? filename")
            parts = line.split()
            if len(parts) >= 2:
                actual_files.add(parts[-1])

    if not actual_files:
        print("Error: No changes detected. Run prepare-release first.")
        return False

    missing = expected_files - actual_files
    extra = actual_files - expected_files

    if missing:
        print(f"Warning: Expected files not modified: {missing}")
    if extra:
        print(f"Note: Additional files modified: {extra}")

    return True


def run_tests() -> bool:
    """Run tests to verify the release."""
    print("Running tests...")
    result = subprocess.run(
        ["python", "-m", "pytest", "tests/", "-v", "--tb=short"],
        capture_output=False,
        check=False,
    )
    return result.returncode == 0


def create_commit(version: str) -> None:
    """Create release commit."""
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(
        ["git", "commit", "-m", f"chore(release): prepare for {version}"],
        check=True,
    )
    print(f"Created commit for version {version}")


def create_tag(version: str) -> None:
    """Create git tag."""
    tag = f"v{version}"
    subprocess.run(
        ["git", "tag", "-a", tag, "-m", f"Release {version}"],
        check=True,
    )
    print(f"Created tag {tag}")


def push_changes() -> None:
    """Push commits and tags to remote."""
    subprocess.run(["git", "push"], check=True)
    subprocess.run(["git", "push", "--tags"], check=True)
    print("Pushed changes and tags to remote")


def main() -> None:
    """Main entry point."""
    version = get_current_version()
    print(f"Preparing to release version {version}")

    # Check working directory
    if not check_working_directory():
        sys.exit(1)

    # Check for --commit flag
    auto_commit = "--commit" in sys.argv

    if not auto_commit:
        print("\nThe following actions will be performed:")
        print(f"  1. Create commit: 'chore(release): prepare for {version}'")
        print(f"  2. Create tag: v{version}")
        print("  3. Push to remote")
        print()
        response = input("Proceed? [y/N] ")
        if response.lower() != "y":
            print("Aborted.")
            sys.exit(0)

    # Run tests
    if not run_tests():
        print("Tests failed. Aborting release.")
        sys.exit(1)

    # Create commit and tag
    create_commit(version)
    create_tag(version)

    if not auto_commit:
        response = input("\nPush to remote? [y/N] ")
        if response.lower() != "y":
            print("Changes committed locally. Push manually when ready.")
            sys.exit(0)

    # Push
    push_changes()

    print(f"\nRelease {version} complete!")
    print(f"View at: https://github.com/m1yag1/adr/releases/tag/v{version}")


if __name__ == "__main__":
    main()
