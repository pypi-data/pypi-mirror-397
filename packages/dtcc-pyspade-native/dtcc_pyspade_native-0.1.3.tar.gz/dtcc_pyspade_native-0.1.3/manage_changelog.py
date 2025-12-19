#!/usr/bin/env python3
"""
Changelog Management Script for dtcc-pyspade-native

This script helps manage the CHANGELOG.md file following the Keep a Changelog format.
It can add entries, prepare releases, and integrate with git history.
"""

import re
import sys
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Optional, Dict
from colorama import init, Fore, Style
import toml

# Initialize colorama for colored output
init(autoreset=True)

class ChangelogManager:
    """Manages CHANGELOG.md operations"""

    # Categories as defined by Keep a Changelog
    CATEGORIES = ["Added", "Changed", "Deprecated", "Removed", "Fixed", "Security"]

    # Mapping of conventional commit types to changelog categories
    COMMIT_TYPE_MAPPING = {
        'feat': 'Added',
        'feature': 'Added',
        'add': 'Added',
        'fix': 'Fixed',
        'bugfix': 'Fixed',
        'bug': 'Fixed',
        'change': 'Changed',
        'update': 'Changed',
        'refactor': 'Changed',
        'deprecate': 'Deprecated',
        'remove': 'Removed',
        'delete': 'Removed',
        'security': 'Security',
        'sec': 'Security'
    }

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.changelog_path = self.project_root / "CHANGELOG.md"
        self.pyproject_path = self.project_root / "pyproject.toml"

        if not self.changelog_path.exists():
            raise FileNotFoundError(f"CHANGELOG.md not found at {self.changelog_path}")

    def read_changelog(self) -> str:
        """Read the current changelog content"""
        with open(self.changelog_path, 'r') as f:
            return f.read()

    def write_changelog(self, content: str, dry_run: bool = False) -> None:
        """Write content to changelog"""
        if dry_run:
            print(f"{Fore.YELLOW}DRY RUN - Would write to CHANGELOG.md{Style.RESET_ALL}")
        else:
            with open(self.changelog_path, 'w') as f:
                f.write(content)
            print(f"{Fore.GREEN}✓ Updated CHANGELOG.md{Style.RESET_ALL}")

    def add_entry(self, category: str, entry: str, dry_run: bool = False) -> None:
        """Add a new entry to the Unreleased section"""
        if category not in self.CATEGORIES:
            raise ValueError(f"Invalid category. Must be one of: {', '.join(self.CATEGORIES)}")

        content = self.read_changelog()

        # Find the Unreleased section
        unreleased_pattern = r'## \[Unreleased\]\n'
        unreleased_match = re.search(unreleased_pattern, content)

        if not unreleased_match:
            raise ValueError("Could not find [Unreleased] section in CHANGELOG.md")

        # Check if category already exists in Unreleased
        category_pattern = rf'## \[Unreleased\].*?\n### {category}\n'
        category_match = re.search(category_pattern, content, re.DOTALL)

        if category_match:
            # Add to existing category
            # Find the position after the category heading
            insert_pos = category_match.end()
            # Add the entry with proper formatting
            new_content = content[:insert_pos] + f"- {entry}\n" + content[insert_pos:]
        else:
            # Create new category in Unreleased section
            # Find position to insert (after ## [Unreleased] and any existing content)
            # Look for the next ## section or the link section at the bottom
            next_section_pattern = r'## \[[0-9]+\.[0-9]+\.[0-9]+\]|\[Unreleased\]:'
            next_section_match = re.search(next_section_pattern, content[unreleased_match.end():])

            if next_section_match:
                insert_pos = unreleased_match.end() + next_section_match.start()
            else:
                insert_pos = len(content)

            # Add category and entry
            new_section = f"\n### {category}\n- {entry}\n"
            new_content = content[:insert_pos] + new_section + content[insert_pos:]

        self.write_changelog(new_content, dry_run)
        print(f"{Fore.GREEN}✓ Added entry to [{category}]: {entry}{Style.RESET_ALL}")

    def release_version(self, version: str, date: str = None, dry_run: bool = False) -> None:
        """
        Prepare a release by moving Unreleased entries to a new version section
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        content = self.read_changelog()

        # Find Unreleased section content
        unreleased_pattern = r'## \[Unreleased\](.*?)(?=## \[|$|\[Unreleased\]:)'
        unreleased_match = re.search(unreleased_pattern, content, re.DOTALL)

        if not unreleased_match:
            raise ValueError("Could not find [Unreleased] section")

        unreleased_content = unreleased_match.group(1).strip()

        if not unreleased_content:
            print(f"{Fore.YELLOW}⚠ No entries in [Unreleased] section{Style.RESET_ALL}")
            return

        # Create new version section
        new_version_section = f"## [{version}] - {date}\n{unreleased_content}\n"

        # Replace Unreleased content with empty section and add new version
        new_content = re.sub(
            r'(## \[Unreleased\]).*?(## \[)',
            rf'\1\n\n{new_version_section}\n\2',
            content,
            count=1,
            flags=re.DOTALL
        )

        # Update links at the bottom
        # Find existing version links
        links_pattern = r'(\[Unreleased\]: .*?\.\.\.HEAD)(.*?)$'
        links_match = re.search(links_pattern, new_content, re.DOTALL)

        if links_match:
            # Update Unreleased link
            repo_url = re.search(r'https://github\.com/[^/]+/[^/]+', links_match.group(1))
            if repo_url:
                repo = repo_url.group(0)
                new_unreleased_link = f"[Unreleased]: {repo}/compare/v{version}...HEAD"
                new_version_link = f"[{version}]: {repo}/releases/tag/v{version}"

                # Check if there's a previous version
                prev_version_pattern = r'\[([0-9]+\.[0-9]+\.[0-9]+)\]:'
                prev_versions = re.findall(prev_version_pattern, links_match.group(2))

                if prev_versions:
                    # Update version link to compare with previous
                    prev_version = prev_versions[0]
                    new_version_link = f"[{version}]: {repo}/compare/v{prev_version}...v{version}"

                # Update links section
                new_links = f"{new_unreleased_link}\n{new_version_link}{links_match.group(2)}"
                new_content = new_content[:links_match.start()] + new_links

        self.write_changelog(new_content, dry_run)
        print(f"{Fore.GREEN}✓ Released version {version}{Style.RESET_ALL}")

    def suggest_from_commits(self, since_tag: str = None, max_commits: int = 50) -> List[Tuple[str, str]]:
        """
        Suggest changelog entries from git commits
        Returns list of (category, entry) tuples
        """
        try:
            # Get commit messages
            cmd = ["git", "log", "--oneline", f"-{max_commits}"]
            if since_tag:
                # Get commits since a specific tag
                cmd = ["git", "log", "--oneline", f"{since_tag}..HEAD"]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            commits = result.stdout.strip().split('\n')

            suggestions = []

            for commit in commits:
                if not commit:
                    continue

                # Parse commit message
                parts = commit.split(' ', 1)
                if len(parts) < 2:
                    continue

                commit_hash, message = parts

                # Skip merge commits
                if message.startswith('Merge'):
                    continue

                # Try to determine category from commit message
                category = self._categorize_commit(message)
                if category:
                    # Clean up the message
                    clean_message = self._clean_commit_message(message)
                    suggestions.append((category, clean_message))

            return suggestions

        except subprocess.CalledProcessError as e:
            print(f"{Fore.RED}Error running git: {e}{Style.RESET_ALL}")
            return []

    def _categorize_commit(self, message: str) -> Optional[str]:
        """Categorize a commit message based on conventional commit format or keywords"""
        message_lower = message.lower()

        # Check for conventional commit format (type: description)
        match = re.match(r'^(\w+):\s*(.+)', message)
        if match:
            commit_type = match.group(1).lower()
            if commit_type in self.COMMIT_TYPE_MAPPING:
                return self.COMMIT_TYPE_MAPPING[commit_type]

        # Check for keywords in message
        for keyword, category in self.COMMIT_TYPE_MAPPING.items():
            if keyword in message_lower:
                return category

        # Default categorization based on common patterns
        if 'fix' in message_lower or 'bug' in message_lower:
            return 'Fixed'
        elif 'add' in message_lower or 'new' in message_lower:
            return 'Added'
        elif 'remove' in message_lower or 'delete' in message_lower:
            return 'Removed'
        elif 'deprecat' in message_lower:
            return 'Deprecated'
        elif 'secur' in message_lower:
            return 'Security'
        elif 'chang' in message_lower or 'updat' in message_lower:
            return 'Changed'

        return None

    def _clean_commit_message(self, message: str) -> str:
        """Clean up commit message for changelog entry"""
        # Remove conventional commit prefix if present
        message = re.sub(r'^\w+:\s*', '', message)

        # Capitalize first letter
        if message and message[0].islower():
            message = message[0].upper() + message[1:]

        # Ensure it doesn't end with a period (changelog convention)
        message = message.rstrip('.')

        return message

    def validate(self) -> bool:
        """Validate the changelog format"""
        content = self.read_changelog()
        issues = []

        # Check for required sections
        if '## [Unreleased]' not in content:
            issues.append("Missing [Unreleased] section")

        # Check for version format
        version_pattern = r'## \[[0-9]+\.[0-9]+\.[0-9]+\] - [0-9]{4}-[0-9]{2}-[0-9]{2}'
        if not re.search(version_pattern, content):
            issues.append("No properly formatted version sections found")

        # Check for link definitions
        if '[Unreleased]:' not in content:
            issues.append("Missing [Unreleased] link definition")

        # Check categories are valid
        category_pattern = r'### (\w+)'
        categories = re.findall(category_pattern, content)
        for cat in categories:
            if cat not in self.CATEGORIES:
                issues.append(f"Invalid category: {cat}")

        if issues:
            print(f"{Fore.RED}Validation failed:{Style.RESET_ALL}")
            for issue in issues:
                print(f"  • {issue}")
            return False
        else:
            print(f"{Fore.GREEN}✓ Changelog format is valid{Style.RESET_ALL}")
            return True

    def interactive_add(self) -> None:
        """Interactive mode for adding changelog entries"""
        print(f"\n{Fore.BLUE}Add Changelog Entry{Style.RESET_ALL}")
        print("=" * 40)

        # Select category
        print("\nSelect category:")
        for i, cat in enumerate(self.CATEGORIES, 1):
            print(f"  {i}. {cat}")

        while True:
            try:
                choice = input(f"\n{Fore.CYAN}Category (1-{len(self.CATEGORIES)}): {Style.RESET_ALL}")
                cat_index = int(choice) - 1
                if 0 <= cat_index < len(self.CATEGORIES):
                    category = self.CATEGORIES[cat_index]
                    break
                else:
                    print(f"{Fore.RED}Invalid choice{Style.RESET_ALL}")
            except (ValueError, KeyboardInterrupt):
                print("\nCancelled")
                return

        # Get entry text
        entry = input(f"{Fore.CYAN}Entry text: {Style.RESET_ALL}").strip()
        if not entry:
            print("Cancelled")
            return

        # Confirm
        print(f"\n{Fore.YELLOW}Will add to [{category}]:{Style.RESET_ALL}")
        print(f"  - {entry}")
        confirm = input(f"\n{Fore.CYAN}Confirm? (y/n): {Style.RESET_ALL}").lower()

        if confirm == 'y':
            self.add_entry(category, entry)
        else:
            print("Cancelled")


def main():
    parser = argparse.ArgumentParser(
        description='Manage CHANGELOG.md for dtcc-pyspade-native',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  add       Add a new entry to [Unreleased] section
  release   Prepare a release (move Unreleased to version)
  suggest   Suggest entries from git commits
  validate  Validate changelog format

Examples:
  %(prog)s add --category Added --message "New triangulation feature"
  %(prog)s add -i                    # Interactive mode
  %(prog)s release --version 0.2.0
  %(prog)s suggest --since v0.1.0    # Suggest from commits
  %(prog)s validate
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Add command
    add_parser = subparsers.add_parser('add', help='Add entry to changelog')
    add_parser.add_argument('-c', '--category',
                          choices=ChangelogManager.CATEGORIES,
                          help='Entry category')
    add_parser.add_argument('-m', '--message',
                          help='Entry message')
    add_parser.add_argument('-i', '--interactive',
                          action='store_true',
                          help='Interactive mode')
    add_parser.add_argument('--dry-run',
                          action='store_true',
                          help='Show what would be done')

    # Release command
    release_parser = subparsers.add_parser('release',
                                          help='Prepare a release')
    release_parser.add_argument('-v', '--version',
                               required=True,
                               help='Version to release')
    release_parser.add_argument('-d', '--date',
                               help='Release date (YYYY-MM-DD)')
    release_parser.add_argument('--dry-run',
                               action='store_true',
                               help='Show what would be done')

    # Suggest command
    suggest_parser = subparsers.add_parser('suggest',
                                          help='Suggest from git commits')
    suggest_parser.add_argument('--since',
                               help='Since tag/commit')
    suggest_parser.add_argument('--max-commits',
                               type=int,
                               default=50,
                               help='Max commits to analyze')
    suggest_parser.add_argument('--add',
                               action='store_true',
                               help='Add suggestions to changelog')

    # Validate command
    subparsers.add_parser('validate', help='Validate changelog format')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        manager = ChangelogManager()

        if args.command == 'add':
            if args.interactive or (not args.category and not args.message):
                manager.interactive_add()
            elif args.category and args.message:
                manager.add_entry(args.category, args.message, args.dry_run)
            else:
                add_parser.print_help()

        elif args.command == 'release':
            manager.release_version(args.version, args.date, args.dry_run)

        elif args.command == 'suggest':
            suggestions = manager.suggest_from_commits(args.since, args.max_commits)
            if suggestions:
                print(f"\n{Fore.BLUE}Suggested entries:{Style.RESET_ALL}")
                for category, entry in suggestions:
                    print(f"  [{category}] {entry}")

                if args.add:
                    confirm = input(f"\n{Fore.CYAN}Add all suggestions? (y/n): {Style.RESET_ALL}")
                    if confirm.lower() == 'y':
                        for category, entry in suggestions:
                            manager.add_entry(category, entry)
            else:
                print(f"{Fore.YELLOW}No suggestions found{Style.RESET_ALL}")

        elif args.command == 'validate':
            manager.validate()

    except Exception as e:
        print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()