#!/bin/bash
# Build dtcc-pyspade-native

set -e

echo "=== Building dtcc-pyspade-native ==="

# Clean previous builds
rm -rf build dist *.egg-info _skbuild

# Install build dependencies
pip install build wheel

# Build the package
echo "Building package..."
python -m build

echo ""
echo "=== Build complete ===="
echo ""
ls -lh dist/
echo ""
echo "To install locally:"
echo "  pip install dist/pyspade_native-*.whl"
echo ""
echo "To publish to Test PyPI:"
echo "  pip install twine"
echo "  twine upload --repository testpypi dist/*"
echo ""
echo "To publish to PyPI:"
echo "  twine upload dist/*"