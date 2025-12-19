#!/usr/bin/env python3
"""
Unified Release Script for dtcc-pyspade-native

This script orchestrates the entire release process, including:
1. Updating version in pyproject.toml
2. Propagating version to all files
3. Updating CHANGELOG.md
4. Creating git commit and tag (optional)
"""

import argparse
import subprocess
import sys
import re
from pathlib import Path
from datetime import datetime
import toml
from colorama import init, Fore, Style
from typing import Optional, List

# Initialize colorama
init(autoreset=True)

class ReleaseManager:
    """Manages the complete release process"""

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.pyproject_path = self.project_root / "pyproject.toml"
        self.changelog_path = self.project_root / "CHANGELOG.md"

        # Validate project structure
        if not self.pyproject_path.exists():
            raise FileNotFoundError(f"pyproject.toml not found at {self.pyproject_path}")

    def get_current_version(self) -> str:
        """Get the current version from pyproject.toml"""
        with open(self.pyproject_path, 'r') as f:
            data = toml.load(f)
        return data.get('project', {}).get('version', '0.0.0')

    def set_version_in_pyproject(self, version: str) -> None:
        """Update version in pyproject.toml"""
        with open(self.pyproject_path, 'r') as f:
            data = toml.load(f)

        data['project']['version'] = version

        with open(self.pyproject_path, 'w') as f:
            toml.dump(data, f)

        print(f"{Fore.GREEN}✓ Updated pyproject.toml to version {version}{Style.RESET_ALL}")

    def validate_version(self, version: str) -> bool:
        """Validate semantic version format"""
        pattern = r'^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9]+)?$'
        if not re.match(pattern, version):
            print(f"{Fore.RED}Invalid version format. Use semantic versioning (e.g., 1.2.3 or 1.2.3-beta1){Style.RESET_ALL}")
            return False
        return True

    def check_git_status(self) -> bool:
        """Check if git working directory is clean"""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                check=True
            )
            if result.stdout.strip():
                print(f"{Fore.YELLOW}⚠ Working directory has uncommitted changes:{Style.RESET_ALL}")
                print(result.stdout)
                return False
            return True
        except subprocess.CalledProcessError:
            print(f"{Fore.RED}Error checking git status{Style.RESET_ALL}")
            return False

    def get_current_branch(self) -> str:
        """Get current git branch"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return "unknown"

    def check_changelog_has_unreleased(self) -> bool:
        """Check if CHANGELOG.md has unreleased entries"""
        if not self.changelog_path.exists():
            return False

        with open(self.changelog_path, 'r') as f:
            content = f.read()

        # Find Unreleased section content
        unreleased_pattern = r'## \[Unreleased\](.*?)(?=## \[|$|\[Unreleased\]:)'
        unreleased_match = re.search(unreleased_pattern, content, re.DOTALL)

        if unreleased_match:
            unreleased_content = unreleased_match.group(1).strip()
            return bool(unreleased_content)
        return False

    def run_command(self, cmd: List[str], description: str, check: bool = True) -> bool:
        """Run a command and report status"""
        try:
            print(f"{Fore.CYAN}→ {description}...{Style.RESET_ALL}")
            result = subprocess.run(cmd, capture_output=True, text=True, check=check)
            if result.stdout:
                print(result.stdout)
            if result.stderr and result.returncode != 0:
                print(f"{Fore.RED}{result.stderr}{Style.RESET_ALL}")
            return result.returncode == 0
        except subprocess.CalledProcessError as e:
            print(f"{Fore.RED}✗ Failed: {e}{Style.RESET_ALL}")
            if e.stdout:
                print(e.stdout)
            if e.stderr:
                print(f"{Fore.RED}{e.stderr}{Style.RESET_ALL}")
            return False

    def suggest_next_version(self, current_version: str, bump_type: str = "patch") -> str:
        """Suggest next version based on bump type"""
        parts = current_version.split('.')
        if len(parts) != 3:
            return current_version

        try:
            major, minor, patch = map(int, parts)

            if bump_type == "major":
                return f"{major + 1}.0.0"
            elif bump_type == "minor":
                return f"{major}.{minor + 1}.0"
            else:  # patch
                return f"{major}.{minor}.{patch + 1}"
        except ValueError:
            return current_version

    def perform_release(
        self,
        version: str,
        dry_run: bool = False,
        skip_git: bool = False,
        skip_changelog: bool = False,
        release_date: str = None,
        commit_message: str = None,
        push: bool = False
    ) -> bool:
        """Perform the complete release process"""

        print(f"\n{Fore.BLUE}{'=' * 60}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{Style.BRIGHT}Release Process{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{'=' * 60}{Style.RESET_ALL}\n")

        # Show current state
        current_version = self.get_current_version()
        current_branch = self.get_current_branch()

        print(f"Current version: {Style.BRIGHT}{current_version}{Style.RESET_ALL}")
        print(f"New version: {Style.BRIGHT}{version}{Style.RESET_ALL}")
        print(f"Branch: {Style.BRIGHT}{current_branch}{Style.RESET_ALL}")
        print(f"Mode: {Style.BRIGHT}{'DRY RUN' if dry_run else 'LIVE'}{Style.RESET_ALL}")

        if not skip_git and current_branch != "main":
            print(f"{Fore.YELLOW}⚠ Warning: Not on main branch{Style.RESET_ALL}")

        print()

        # Validate version
        if not self.validate_version(version):
            return False

        # Check git status (unless skipping git operations)
        if not skip_git and not dry_run:
            if not self.check_git_status():
                response = input(f"{Fore.YELLOW}Continue anyway? (y/N): {Style.RESET_ALL}")
                if response.lower() != 'y':
                    print("Aborted")
                    return False

        # Check changelog has unreleased entries
        if not skip_changelog:
            if not self.check_changelog_has_unreleased():
                print(f"{Fore.YELLOW}⚠ No unreleased entries in CHANGELOG.md{Style.RESET_ALL}")
                if not skip_changelog:
                    response = input(f"{Fore.YELLOW}Continue without changelog update? (y/N): {Style.RESET_ALL}")
                    if response.lower() != 'y':
                        print("Aborted")
                        return False
                    skip_changelog = True

        # Step-by-step release process
        steps = []

        # 1. Update pyproject.toml
        steps.append(("Update pyproject.toml", lambda: (
            self.set_version_in_pyproject(version) if not dry_run else
            print(f"{Fore.CYAN}→ Would update pyproject.toml to {version}{Style.RESET_ALL}")
        )))

        # 2. Run version update script
        update_cmd = ["python3", "update_version.py"]
        if not dry_run:
            update_cmd.append("--apply")
        if not skip_changelog:
            update_cmd.append("--changelog")
            if release_date:
                update_cmd.extend(["--date", release_date])

        steps.append(("Propagate version changes", lambda: self.run_command(
            update_cmd,
            "Updating version in all files"
        )))

        # 3. Run tests (optional but recommended)
        if (self.project_root / "tests").exists():
            steps.append(("Run tests", lambda: self.run_command(
                ["python3", "-m", "pytest", "tests/", "-v"],
                "Running tests",
                check=False  # Don't fail on test errors, just report
            )))

        # 4. Git operations
        if not skip_git and not dry_run:
            # Commit changes
            if commit_message is None:
                commit_message = f"Release version {version}"

            steps.append(("Commit changes", lambda: self.run_command(
                ["git", "add", "."],
                "Staging changes"
            ) and self.run_command(
                ["git", "commit", "-m", commit_message],
                "Creating commit"
            )))

            # Create tag
            steps.append(("Create git tag", lambda: self.run_command(
                ["git", "tag", f"v{version}", "-m", f"Version {version}"],
                f"Creating tag v{version}"
            )))

            # Push to remote (if requested)
            if push:
                steps.append(("Push to remote", lambda: self.run_command(
                    ["git", "push", "origin", current_branch],
                    "Pushing commits"
                ) and self.run_command(
                    ["git", "push", "origin", f"v{version}"],
                    "Pushing tag"
                )))

        # Execute steps
        print(f"\n{Fore.BLUE}Executing release steps:{Style.RESET_ALL}\n")
        for step_name, step_func in steps:
            print(f"{Fore.CYAN}• {step_name}{Style.RESET_ALL}")
            step_func()
            print()

        # Summary
        print(f"{Fore.BLUE}{'=' * 60}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}Release Summary:{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{'=' * 60}{Style.RESET_ALL}\n")

        if dry_run:
            print(f"{Fore.YELLOW}This was a dry run. No actual changes were made.{Style.RESET_ALL}")
            print(f"To perform the actual release, run without --dry-run")
        else:
            print(f"{Fore.GREEN}✓ Successfully released version {version}{Style.RESET_ALL}")

            if not skip_git:
                print(f"\nNext steps:")
                if not push:
                    print(f"  • Push changes: git push origin {current_branch}")
                    print(f"  • Push tag: git push origin v{version}")
                print(f"  • Create GitHub release: https://github.com/dtcc-platform/dtcc-pyspade-native/releases/new")
                print(f"  • Publish to PyPI: python -m build && twine upload dist/*")

        return True


def main():
    parser = argparse.ArgumentParser(
        description='Unified release script for dtcc-pyspade-native',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This script orchestrates the complete release process:
1. Updates version in pyproject.toml
2. Propagates version to all project files
3. Updates CHANGELOG.md (moves Unreleased to version)
4. Creates git commit and tag (optional)
5. Pushes to remote (optional)

Examples:
  %(prog)s 0.2.0                    # Release version 0.2.0
  %(prog)s 0.2.0 --dry-run          # Preview what would happen
  %(prog)s patch                     # Auto-bump patch version
  %(prog)s minor --push             # Bump minor version and push
  %(prog)s 1.0.0 --skip-changelog   # Release without changelog update
  %(prog)s 1.0.0 --skip-git         # Update files without git operations
        """
    )

    parser.add_argument(
        'version',
        help='Version to release (e.g., 0.2.0) or bump type (major/minor/patch)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without applying them'
    )

    parser.add_argument(
        '--skip-git',
        action='store_true',
        help='Skip git operations (commit, tag)'
    )

    parser.add_argument(
        '--skip-changelog',
        action='store_true',
        help='Skip changelog update'
    )

    parser.add_argument(
        '--push',
        action='store_true',
        help='Push commits and tags to remote'
    )

    parser.add_argument(
        '--date',
        help='Release date for changelog (YYYY-MM-DD)'
    )

    parser.add_argument(
        '--message', '-m',
        help='Custom commit message'
    )

    args = parser.parse_args()

    try:
        manager = ReleaseManager()

        # Determine version
        version = args.version
        if version in ['major', 'minor', 'patch']:
            current = manager.get_current_version()
            version = manager.suggest_next_version(current, version)
            print(f"{Fore.CYAN}Auto-bumping {args.version} version: {current} → {version}{Style.RESET_ALL}")

        # Confirm before proceeding (unless dry run)
        if not args.dry_run:
            print(f"\n{Fore.YELLOW}About to release version {version}{Style.RESET_ALL}")
            response = input(f"{Fore.CYAN}Continue? (y/N): {Style.RESET_ALL}")
            if response.lower() != 'y':
                print("Aborted")
                return

        # Perform release
        success = manager.perform_release(
            version=version,
            dry_run=args.dry_run,
            skip_git=args.skip_git,
            skip_changelog=args.skip_changelog,
            release_date=args.date,
            commit_message=args.message,
            push=args.push
        )

        sys.exit(0 if success else 1)

    except Exception as e:
        print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()