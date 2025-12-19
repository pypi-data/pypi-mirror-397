#!/usr/bin/env python3
"""
Version Update Script for dtcc-pyspade-native

This script reads the version from pyproject.toml and propagates it
to all relevant files in the codebase.
"""

import re
import sys
import toml
from pathlib import Path
from typing import List, Tuple, Optional
import argparse
import difflib
from datetime import datetime
import subprocess
from colorama import init, Fore, Style

# Initialize colorama for colored output
init(autoreset=True)

class VersionUpdater:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.version = self._read_version_from_pyproject()
        self.changes = []

    def _read_version_from_pyproject(self) -> str:
        """Read the version from pyproject.toml"""
        pyproject_path = self.project_root / "pyproject.toml"
        if not pyproject_path.exists():
            raise FileNotFoundError(f"pyproject.toml not found at {pyproject_path}")

        with open(pyproject_path, 'r') as f:
            data = toml.load(f)

        version = data.get('project', {}).get('version')
        if not version:
            raise ValueError("Version not found in pyproject.toml")

        print(f"{Fore.GREEN}✓ Found version in pyproject.toml: {Style.BRIGHT}{version}{Style.RESET_ALL}")
        return version

    def _update_file(self, file_path: Path, pattern: str, replacement: str,
                     description: str, dry_run: bool = True) -> bool:
        """Update a file with a specific pattern replacement"""
        if not file_path.exists():
            print(f"{Fore.YELLOW}⚠ File not found: {file_path}{Style.RESET_ALL}")
            return False

        with open(file_path, 'r') as f:
            content = f.read()

        new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

        if content != new_content:
            self.changes.append((file_path, content, new_content, description))

            if not dry_run:
                with open(file_path, 'w') as f:
                    f.write(new_content)
                print(f"{Fore.GREEN}✓ Updated {file_path.relative_to(self.project_root)}: {description}{Style.RESET_ALL}")
            else:
                print(f"{Fore.CYAN}→ Would update {file_path.relative_to(self.project_root)}: {description}{Style.RESET_ALL}")
            return True
        else:
            print(f"{Style.DIM}○ No changes needed in {file_path.relative_to(self.project_root)}{Style.RESET_ALL}")
            return False

    def update_cmake_files(self, dry_run: bool = True):
        """Update version in CMakeLists.txt files"""
        # Main CMakeLists.txt
        main_cmake = self.project_root / "CMakeLists.txt"
        pattern = r'(project\([^)]+VERSION\s+)[\d.]+(\s+LANGUAGES)'
        replacement = rf'\g<1>{self.version}\g<2>'
        self._update_file(main_cmake, pattern, replacement,
                         "project VERSION", dry_run)

        # cppspade CMakeLists.txt
        cppspade_cmake = self.project_root / "cppspade" / "CMakeLists.txt"
        self._update_file(cppspade_cmake, pattern, replacement,
                         "project VERSION", dry_run)

    def update_python_init(self, dry_run: bool = True):
        """Update version in Python __init__.py files"""
        init_file = self.project_root / "src" / "pyspade_native" / "__init__.py"
        pattern = r'__version__\s*=\s*["\'][\d.]+["\']'
        replacement = f'__version__ = "{self.version}"'
        self._update_file(init_file, pattern, replacement,
                         "__version__", dry_run)

    def update_test_files(self, dry_run: bool = True):
        """Update version assertions in test files"""
        test_file = self.project_root / "tests" / "test_import.py"
        pattern = r'assert\s+pyspade_native\.__version__\s*==\s*["\'][\d.]+["\']'
        replacement = f'assert pyspade_native.__version__ == "{self.version}"'
        self._update_file(test_file, pattern, replacement,
                         "version assertion", dry_run)

    def update_cargo_toml(self, dry_run: bool = True):
        """Update version in Cargo.toml"""
        cargo_file = self.project_root / "cppspade" / "Cargo.toml"
        pattern = r'(^version\s*=\s*["\'])[\d.]+(["\'])'
        replacement = rf'\g<1>{self.version}\g<2>'
        self._update_file(cargo_file, pattern, replacement,
                         "Cargo.toml version", dry_run)

    def update_spade_helpers(self, dry_run: bool = True):
        """Update default version in SpadeHelpers.cmake"""
        helpers_file = self.project_root / "cppspade" / "cmake" / "SpadeHelpers.cmake"
        pattern = r'(set\(ARGS_VERSION\s+")[^"]+("\))'
        replacement = rf'\g<1>{self.version}\g<2>'
        self._update_file(helpers_file, pattern, replacement,
                         "default ARGS_VERSION", dry_run)

    def update_changelog(self, dry_run: bool = True, release_date: str = None) -> bool:
        """Update CHANGELOG.md for the new version"""
        changelog_path = self.project_root / "CHANGELOG.md"
        if not changelog_path.exists():
            print(f"{Fore.YELLOW}⚠ CHANGELOG.md not found, skipping{Style.RESET_ALL}")
            return False

        with open(changelog_path, 'r') as f:
            content = f.read()

        # Check if version already exists
        version_header = f"## [{self.version}]"
        if version_header in content:
            print(f"{Style.DIM}○ Version {self.version} already in CHANGELOG.md{Style.RESET_ALL}")
            return False

        # Find Unreleased section content
        unreleased_pattern = r'## \[Unreleased\](.*?)(?=## \[|$|\[Unreleased\]:)'
        unreleased_match = re.search(unreleased_pattern, content, re.DOTALL)

        if not unreleased_match:
            print(f"{Fore.YELLOW}⚠ Could not find [Unreleased] section in CHANGELOG.md{Style.RESET_ALL}")
            return False

        unreleased_content = unreleased_match.group(1).strip()

        if not unreleased_content:
            print(f"{Fore.YELLOW}⚠ No entries in [Unreleased] section{Style.RESET_ALL}")
            return False

        # Set release date
        if release_date is None:
            release_date = datetime.now().strftime("%Y-%m-%d")

        # Create new version section
        new_version_section = f"## [{self.version}] - {release_date}\n{unreleased_content}\n"

        # Replace Unreleased content with empty section and add new version
        new_content = re.sub(
            r'(## \[Unreleased\]).*?(## \[)',
            rf'\1\n\n{new_version_section}\n\2',
            content,
            count=1,
            flags=re.DOTALL
        )

        # Update links at the bottom
        links_pattern = r'(\[Unreleased\]: .*?\.\.\.HEAD)(.*?)$'
        links_match = re.search(links_pattern, new_content, re.DOTALL)

        if links_match:
            # Update Unreleased link
            repo_url = re.search(r'https://github\.com/[^/]+/[^/]+', links_match.group(1))
            if repo_url:
                repo = repo_url.group(0)
                new_unreleased_link = f"[Unreleased]: {repo}/compare/v{self.version}...HEAD"
                new_version_link = f"[{self.version}]: {repo}/releases/tag/v{self.version}"

                # Check if there's a previous version
                prev_version_pattern = r'\[([0-9]+\.[0-9]+\.[0-9]+)\]:'
                prev_versions = re.findall(prev_version_pattern, links_match.group(2))

                if prev_versions:
                    # Update version link to compare with previous
                    prev_version = prev_versions[0]
                    new_version_link = f"[{self.version}]: {repo}/compare/v{prev_version}...v{self.version}"

                # Update links section
                new_links = f"{new_unreleased_link}\n{new_version_link}{links_match.group(2)}"
                new_content = new_content[:links_match.start()] + new_links

        self.changes.append((changelog_path, content, new_content, "Changelog release"))

        if not dry_run:
            with open(changelog_path, 'w') as f:
                f.write(new_content)
            print(f"{Fore.GREEN}✓ Updated CHANGELOG.md: Released version {self.version}{Style.RESET_ALL}")
        else:
            print(f"{Fore.CYAN}→ Would update CHANGELOG.md: Release version {self.version}{Style.RESET_ALL}")

        return True

    def update_all(self, dry_run: bool = True, show_diff: bool = False,
                   update_changelog: bool = False, release_date: str = None):
        """Update all version references"""
        print(f"\n{Fore.BLUE}{'=' * 60}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{Style.BRIGHT}Version Update Report{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{'=' * 60}{Style.RESET_ALL}\n")

        print(f"Target version: {Style.BRIGHT}{self.version}{Style.RESET_ALL}")
        print(f"Mode: {Style.BRIGHT}{'DRY RUN' if dry_run else 'APPLYING CHANGES'}{Style.RESET_ALL}")
        if update_changelog:
            print(f"Changelog: {Style.BRIGHT}WILL UPDATE{Style.RESET_ALL}")
        print()

        # Clear changes list for fresh run
        self.changes = []

        # Update all files
        print(f"{Fore.YELLOW}Checking files...{Style.RESET_ALL}\n")
        self.update_cmake_files(dry_run)
        self.update_python_init(dry_run)
        self.update_test_files(dry_run)
        self.update_cargo_toml(dry_run)
        self.update_spade_helpers(dry_run)

        # Update changelog if requested
        if update_changelog:
            self.update_changelog(dry_run, release_date)

        # Show summary
        print(f"\n{Fore.BLUE}{'=' * 60}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}Summary:{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{'=' * 60}{Style.RESET_ALL}")

        if self.changes:
            print(f"\n{Fore.GREEN}Files to be updated: {len(self.changes)}{Style.RESET_ALL}")
            for file_path, _, _, description in self.changes:
                rel_path = file_path.relative_to(self.project_root)
                print(f"  • {rel_path}: {description}")

            if show_diff and dry_run:
                print(f"\n{Fore.BLUE}{'=' * 60}{Style.RESET_ALL}")
                print(f"{Fore.BLUE}Detailed Changes:{Style.RESET_ALL}")
                print(f"{Fore.BLUE}{'=' * 60}{Style.RESET_ALL}")
                for file_path, old_content, new_content, _ in self.changes:
                    print(f"\n{Fore.CYAN}File: {file_path.relative_to(self.project_root)}{Style.RESET_ALL}")
                    print("-" * 40)
                    diff = difflib.unified_diff(
                        old_content.splitlines(keepends=True),
                        new_content.splitlines(keepends=True),
                        fromfile=f"{file_path} (old)",
                        tofile=f"{file_path} (new)",
                        n=2
                    )
                    for line in diff:
                        if line.startswith('+') and not line.startswith('+++'):
                            print(f"{Fore.GREEN}{line}{Style.RESET_ALL}", end='')
                        elif line.startswith('-') and not line.startswith('---'):
                            print(f"{Fore.RED}{line}{Style.RESET_ALL}", end='')
                        else:
                            print(line, end='')
        else:
            print(f"\n{Fore.GREEN}✓ All files are already up to date!{Style.RESET_ALL}")

        if dry_run and self.changes:
            print(f"\n{Fore.YELLOW}This was a dry run. Use --apply to make actual changes.{Style.RESET_ALL}")
        elif not dry_run and self.changes:
            print(f"\n{Fore.GREEN}✓ All changes have been applied successfully!{Style.RESET_ALL}")

def main():
    parser = argparse.ArgumentParser(
        description='Update version across all files in dtcc-pyspade-native project',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s              # Dry run - show what would be changed
  %(prog)s --apply      # Actually apply the changes
  %(prog)s --diff       # Show detailed diff of changes
  %(prog)s --version 1.0.0 --apply  # Override version and apply
  %(prog)s --changelog --apply  # Update version and release changelog
  %(prog)s --changelog --date 2024-10-24 --apply  # With custom date
        """
    )

    parser.add_argument(
        '--apply', '-a',
        action='store_true',
        help='Apply changes (default is dry run)'
    )

    parser.add_argument(
        '--diff', '-d',
        action='store_true',
        help='Show detailed diff of changes'
    )

    parser.add_argument(
        '--version', '-v',
        type=str,
        help='Override version instead of reading from pyproject.toml'
    )

    parser.add_argument(
        '--changelog', '-c',
        action='store_true',
        help='Also update CHANGELOG.md (move Unreleased to version)'
    )

    parser.add_argument(
        '--date',
        type=str,
        help='Release date for changelog (YYYY-MM-DD format)'
    )

    parser.add_argument(
        '--root', '-r',
        type=Path,
        default=Path.cwd(),
        help='Project root directory (default: current directory)'
    )

    args = parser.parse_args()

    try:
        updater = VersionUpdater(args.root)

        # Override version if specified
        if args.version:
            print(f"{Fore.YELLOW}Overriding version with: {args.version}{Style.RESET_ALL}")
            updater.version = args.version

        # Run the update
        updater.update_all(
            dry_run=not args.apply,
            show_diff=args.diff,
            update_changelog=args.changelog,
            release_date=args.date
        )

    except Exception as e:
        print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()