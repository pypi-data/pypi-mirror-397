# Release Process

This document describes the release process for dtcc-pyspade-native, including version management and changelog automation.

## Overview

The project uses an automated release system with three main scripts:
- **`update_version.py`** - Updates version across all project files
- **`manage_changelog.py`** - Manages CHANGELOG.md entries
- **`release.py`** - Orchestrates the complete release process

## Prerequisites

Install required Python packages:
```bash
pip install toml colorama
```

## Quick Release Guide

For a standard release, simply run:

```bash
python3 release.py 0.2.0
```

This will:
1. Update version in `pyproject.toml`
2. Propagate version to all project files
3. Move [Unreleased] changelog entries to the new version
4. Create a git commit and tag
5. Provide instructions for next steps

## Detailed Workflows

### 1. During Development - Adding Changelog Entries

As you make changes during development, add entries to the changelog:

```bash
# Interactive mode
python3 manage_changelog.py add -i

# Command line mode
python3 manage_changelog.py add --category Added --message "New triangulation algorithm"
python3 manage_changelog.py add --category Fixed --message "Memory leak in mesh generation"
```

Categories follow [Keep a Changelog](https://keepachangelog.com/) format:
- **Added** - New features
- **Changed** - Changes to existing functionality
- **Deprecated** - Features that will be removed
- **Removed** - Removed features
- **Fixed** - Bug fixes
- **Security** - Security fixes

### 2. Preparing a Release

#### Option A: Fully Automated (Recommended)

Use the unified release script:

```bash
# Preview the release
python3 release.py 0.2.0 --dry-run

# Perform the release
python3 release.py 0.2.0

# Release with auto-push to remote
python3 release.py 0.2.0 --push
```

#### Option B: Step-by-Step Manual Process

1. **Add remaining changelog entries** from recent commits:
   ```bash
   # Suggest entries from git history
   python3 manage_changelog.py suggest --since v0.1.1

   # Add all suggestions
   python3 manage_changelog.py suggest --since v0.1.1 --add
   ```

2. **Update version in pyproject.toml**:
   ```bash
   # Edit pyproject.toml manually, then:
   ```

3. **Propagate version and update changelog**:
   ```bash
   # Preview changes
   python3 update_version.py --changelog

   # Apply changes
   python3 update_version.py --changelog --apply
   ```

4. **Commit and tag**:
   ```bash
   git add .
   git commit -m "Release version 0.2.0"
   git tag v0.2.0 -m "Version 0.2.0"
   ```

5. **Push to remote**:
   ```bash
   git push origin main
   git push origin v0.2.0
   ```

### 3. Version Bump Types

The release script supports automatic version bumping:

```bash
# Bump patch version (0.1.1 → 0.1.2)
python3 release.py patch

# Bump minor version (0.1.1 → 0.2.0)
python3 release.py minor

# Bump major version (0.1.1 → 1.0.0)
python3 release.py major
```

### 4. Special Scenarios

#### Release without changelog update:
```bash
python3 release.py 0.2.0 --skip-changelog
```

#### Update files without git operations:
```bash
python3 release.py 0.2.0 --skip-git
```

#### Custom release date:
```bash
python3 release.py 0.2.0 --date 2024-10-25
```

#### Custom commit message:
```bash
python3 release.py 0.2.0 --message "Release v0.2.0: Major performance improvements"
```

## Script Reference

### update_version.py

Updates version across all project files:

```bash
# Preview changes
python3 update_version.py

# Apply changes
python3 update_version.py --apply

# Show detailed diff
python3 update_version.py --diff

# Update with changelog
python3 update_version.py --changelog --apply

# Override version
python3 update_version.py --version 1.0.0 --apply
```

Files updated:
- `CMakeLists.txt` - Project version
- `cppspade/CMakeLists.txt` - C++ wrapper version
- `src/pyspade_native/__init__.py` - Python `__version__`
- `tests/test_import.py` - Version assertion
- `cppspade/Cargo.toml` - Rust crate version
- `cppspade/cmake/SpadeHelpers.cmake` - Default cmake version
- `CHANGELOG.md` (optional) - Release changelog

### manage_changelog.py

Manages CHANGELOG.md entries:

```bash
# Add entry interactively
python3 manage_changelog.py add -i

# Add entry directly
python3 manage_changelog.py add --category Fixed --message "Memory leak"

# Prepare release (move Unreleased to version)
python3 manage_changelog.py release --version 0.2.0

# Suggest entries from git
python3 manage_changelog.py suggest --since v0.1.0

# Validate changelog format
python3 manage_changelog.py validate
```

### release.py

Complete release automation:

```bash
# Standard release
python3 release.py 0.2.0

# Dry run
python3 release.py 0.2.0 --dry-run

# Auto-bump version
python3 release.py patch|minor|major

# Skip components
python3 release.py 0.2.0 --skip-changelog --skip-git

# Push to remote
python3 release.py 0.2.0 --push
```

## Post-Release Tasks

After running the release script:

1. **Create GitHub Release**:
   - Go to: https://github.com/dtcc-platform/dtcc-pyspade-native/releases/new
   - Select the new tag
   - Copy changelog entries for release notes
   - Publish release

2. **Publish to PyPI**:
   ```bash
   # Build package
   python3 -m build

   # Upload to Test PyPI first (optional)
   twine upload --repository testpypi dist/*

   # Upload to PyPI
   twine upload dist/*
   ```

3. **Update Documentation**:
   - Update README if needed
   - Update documentation site
   - Announce release if applicable

## Troubleshooting

### "Working directory has uncommitted changes"

Commit or stash your changes before releasing:
```bash
git add .
git commit -m "Your changes"
# or
git stash
```

### "No unreleased entries in CHANGELOG.md"

Add changelog entries before releasing:
```bash
python3 manage_changelog.py add -i
```

Or skip changelog update:
```bash
python3 release.py 0.2.0 --skip-changelog
```

### Version already exists

Check current versions:
```bash
git tag -l
grep version pyproject.toml
```

### Rollback a failed release

If something goes wrong:
```bash
# Reset to previous commit
git reset --hard HEAD~1

# Delete local tag
git tag -d v0.2.0

# Delete remote tag (if pushed)
git push origin :refs/tags/v0.2.0
```

## Best Practices

1. **Always run tests before releasing**:
   ```bash
   pytest tests/
   ```

2. **Use dry-run first**:
   ```bash
   python3 release.py 0.2.0 --dry-run
   ```

3. **Keep changelog updated during development**:
   - Add entries as you make changes
   - Don't wait until release time

4. **Follow semantic versioning**:
   - MAJOR: Breaking changes
   - MINOR: New features (backward compatible)
   - PATCH: Bug fixes (backward compatible)

5. **Write clear changelog entries**:
   - Start with a verb (Added, Fixed, Changed, etc.)
   - Be specific but concise
   - Include issue/PR numbers if applicable

6. **Test the release on Test PyPI first**:
   ```bash
   twine upload --repository testpypi dist/*
   pip install -i https://test.pypi.org/simple/ dtcc-pyspade-native
   ```

## Example Complete Release

Here's a complete example of releasing version 0.2.0:

```bash
# 1. Check git status
git status

# 2. Add final changelog entries
python3 manage_changelog.py suggest --since v0.1.1
python3 manage_changelog.py add -i

# 3. Run tests
pytest tests/ -v

# 4. Preview release
python3 release.py 0.2.0 --dry-run

# 5. Perform release
python3 release.py 0.2.0

# 6. Push to remote
git push origin main
git push origin v0.2.0

# 7. Create GitHub release
# (Visit GitHub releases page)

# 8. Build and publish to PyPI
python3 -m build
twine upload dist/*

# 9. Clean up
rm -rf dist/ build/
```

## Configuration

The scripts use sensible defaults but can be customized:

- **Version source**: `pyproject.toml` → `[project]` → `version`
- **Changelog format**: [Keep a Changelog](https://keepachangelog.com/)
- **Version format**: [Semantic Versioning](https://semver.org/)
- **Git tag format**: `v{version}` (e.g., `v0.2.0`)

## Contributing

When contributing to this project:

1. Add changelog entries for your changes:
   ```bash
   python3 manage_changelog.py add -i
   ```

2. Don't update version numbers in PRs (maintainers will handle releases)

3. Follow the existing commit message patterns for better changelog generation