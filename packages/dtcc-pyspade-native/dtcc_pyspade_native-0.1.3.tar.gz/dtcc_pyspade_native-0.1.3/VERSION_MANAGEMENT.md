# Version Management

This project uses a centralized version management approach where the version is defined in `pyproject.toml` and automatically propagated to all other files.

## Version Update Script

The `update_version.py` script reads the version from `pyproject.toml` and updates it across the entire codebase.

### Files Updated

The script automatically updates version information in:

1. **CMakeLists.txt** - Main project version
2. **cppspade/CMakeLists.txt** - C++ wrapper project version
3. **src/pyspade_native/__init__.py** - Python package `__version__`
4. **tests/test_import.py** - Version assertion in tests
5. **cppspade/Cargo.toml** - Rust crate version
6. **cppspade/cmake/SpadeHelpers.cmake** - Default version for cmake helpers

### Usage

#### Basic Usage (Dry Run)

By default, the script runs in dry-run mode to show what would be changed:

```bash
python3 update_version.py
```

#### Apply Changes

To actually apply the version changes:

```bash
python3 update_version.py --apply
```

#### Show Detailed Diff

To see a detailed diff of all changes:

```bash
python3 update_version.py --diff
```

#### Override Version

To set a specific version (instead of reading from pyproject.toml):

```bash
python3 update_version.py --version 1.2.3 --apply
```

### Command Line Options

- `--apply`, `-a` - Apply changes (default is dry run)
- `--diff`, `-d` - Show detailed diff of changes
- `--version`, `-v` - Override version instead of reading from pyproject.toml
- `--root`, `-r` - Project root directory (default: current directory)

### Examples

```bash
# Check what would be changed (dry run)
python3 update_version.py

# See detailed changes before applying
python3 update_version.py --diff

# Apply the changes
python3 update_version.py --apply

# Set a specific version and apply
python3 update_version.py --version 2.0.0 --apply
```

## Workflow

### Normal Version Update Process

1. Update the version in `pyproject.toml`
2. Run `python3 update_version.py` to preview changes
3. Run `python3 update_version.py --apply` to apply changes
4. Commit all changes together

### Release Process

When preparing a release:

```bash
# 1. Update version in pyproject.toml
# 2. Propagate version to all files
python3 update_version.py --apply

# 3. Run tests to ensure everything works
pytest

# 4. Commit the version changes
git add .
git commit -m "Bump version to X.Y.Z"

# 5. Create a tag
git tag vX.Y.Z

# 6. Push changes and tag
git push origin main --tags
```

## Adding New Files

If you add new files that contain version information, update the `update_version.py` script:

1. Add a new update method for your file type
2. Call it from the `update_all()` method
3. Use appropriate regex patterns to match your version format

## Requirements

The script requires:
- Python 3.8+
- `toml` package: `pip install toml`
- `colorama` package: `pip install colorama`

Install dependencies:
```bash
pip install toml colorama
```