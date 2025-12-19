#!/bin/bash
# Test dtcc-pyspade-native installation

set -e

echo "=== Testing dtcc-pyspade-native ==="

# Test Python import
echo "Testing Python import..."
python -c "import pyspade_native; print('✓ Import successful')"

# Test Python API
echo "Testing Python API..."
python -c "import pyspade_native; print('Include dir:', pyspade_native.get_include_dir())"
python -c "import pyspade_native; print('Library dir:', pyspade_native.get_library_dir())"
python -c "import pyspade_native; print('CMake dir:', pyspade_native.get_cmake_dir())"
python -c "import pyspade_native; libs = pyspade_native.get_libraries(); print('Libraries:', libs)"

# Print full info
echo ""
echo "Full installation info:"
python -m pyspade_native

# Test example project
echo ""
echo "=== Testing example project ==="
cd examples/complete-project
pip install -e .
python test_example.py
cd ../..

echo ""
echo "=== All tests passed ✓ ==="