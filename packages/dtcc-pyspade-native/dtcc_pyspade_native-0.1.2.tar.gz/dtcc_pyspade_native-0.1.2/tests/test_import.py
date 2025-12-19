"""Test basic pyspade_native functionality."""

import pytest


def test_import():
    """Test that the module can be imported."""
    import pyspade_native
    assert pyspade_native.__version__ == "0.1.1"


def test_get_include_dir():
    """Test getting include directory."""
    import pyspade_native
    include_dir = pyspade_native.get_include_dir()
    assert isinstance(include_dir, str)
    assert len(include_dir) > 0


def test_get_library_dir():
    """Test getting library directory."""
    import pyspade_native
    lib_dir = pyspade_native.get_library_dir()
    assert isinstance(lib_dir, str)
    assert len(lib_dir) > 0


def test_get_cmake_dir():
    """Test getting CMake directory."""
    import pyspade_native
    cmake_dir = pyspade_native.get_cmake_dir()
    assert isinstance(cmake_dir, str)
    assert len(cmake_dir) > 0


def test_get_libraries():
    """Test getting libraries dictionary."""
    import pyspade_native
    libs = pyspade_native.get_libraries()
    assert isinstance(libs, dict)
    # Should have at least spade_wrapper
    assert 'spade_wrapper' in libs or 'spade_ffi' in libs


def test_print_info():
    """Test that print_info runs without error."""
    import pyspade_native
    # Should not raise an exception
    pyspade_native.print_info()