#!/usr/bin/env python3
"""Prepare a release by updating CHANGELOG.md and version.

Usage:
    python scripts/prepare_release.py              # Auto-detect version from commits
    python scripts/prepare_release.py 0.2.0        # Explicit version
    python scripts/prepare_release.py --patch      # Force patch bump
    python scripts/prepare_release.py --minor      # Force minor bump
    python scripts/prepare_release.py --major      # Force major bump
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


def get_latest_tag() -> str | None:
    """Get the latest git tag."""
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None


def get_commits_since_tag(tag: str | None) -> list[str]:
    """Get commit messages since the given tag."""
    if tag:
        cmd = ["git", "log", f"{tag}..HEAD", "--pretty=format:%s"]
    else:
        cmd = ["git", "log", "--pretty=format:%s"]

    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return [line for line in result.stdout.strip().split("\n") if line]


def analyze_commits(commits: list[str]) -> str:
    """Analyze commits to determine version bump type.

    Pre-1.0 semantics:
    - feat or BREAKING CHANGE -> minor
    - fix, refactor, perf -> patch
    """
    has_breaking = any(
        "BREAKING CHANGE" in c or "!" in c.split(":")[0] for c in commits
    )
    has_feat = any(c.startswith("feat") for c in commits)
    has_fix = any(
        c.startswith(("fix", "refactor", "perf", "docs", "style", "test", "chore"))
        for c in commits
    )

    if has_breaking or has_feat:
        return "minor"
    elif has_fix:
        return "patch"
    else:
        return "patch"


def bump_version(current: str, bump_type: str) -> str:
    """Bump version according to semver."""
    parts = current.split(".")
    major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2].split("-")[0])

    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    else:
        return f"{major}.{minor}.{patch + 1}"


def update_version_file(new_version: str) -> None:
    """Update version in src/adr/__init__.py."""
    init_file = Path("src/adr/__init__.py")
    content = init_file.read_text()
    new_content = re.sub(
        r'(__version__\s*=\s*["\'])([^"\']+)(["\'])',
        f"\\g<1>{new_version}\\g<3>",
        content,
    )
    init_file.write_text(new_content)
    print(f"Updated src/adr/__init__.py to version {new_version}")


def generate_changelog(version: str) -> None:
    """Generate changelog using git-cliff."""
    try:
        subprocess.run(
            ["git-cliff", "--tag", f"v{version}", "-o", "CHANGELOG.md"],
            check=True,
        )
        print(f"Generated CHANGELOG.md for version {version}")
    except FileNotFoundError:
        print("Warning: git-cliff not found. Install with: cargo install git-cliff")
        print("Skipping changelog generation.")


def main() -> None:
    """Main entry point."""
    current_version = get_current_version()
    print(f"Current version: {current_version}")

    # Parse arguments
    args = sys.argv[1:]
    new_version = None
    bump_type = None

    if args:
        arg = args[0]
        if arg == "--patch":
            bump_type = "patch"
        elif arg == "--minor":
            bump_type = "minor"
        elif arg == "--major":
            bump_type = "major"
        elif re.match(r"^\d+\.\d+\.\d+", arg):
            new_version = arg
        else:
            print(f"Unknown argument: {arg}")
            print(__doc__)
            sys.exit(1)

    if not new_version:
        # Auto-detect from commits
        latest_tag = get_latest_tag()
        if latest_tag:
            print(f"Latest tag: {latest_tag}")
        else:
            print("No previous tags found")

        commits = get_commits_since_tag(latest_tag)
        if not commits:
            print("No commits since last tag")
            sys.exit(0)

        print(f"Found {len(commits)} commits since last release")

        if not bump_type:
            bump_type = analyze_commits(commits)

        print(f"Detected bump type: {bump_type}")
        new_version = bump_version(current_version, bump_type)

    print(f"New version: {new_version}")

    # Update version file
    update_version_file(new_version)

    # Generate changelog
    generate_changelog(new_version)

    print("\nPrepare release complete!")
    print("Review the changes, then run: tox -e release")


if __name__ == "__main__":
    main()
