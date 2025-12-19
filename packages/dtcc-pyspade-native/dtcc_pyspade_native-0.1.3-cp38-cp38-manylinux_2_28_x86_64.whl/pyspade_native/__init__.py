"""
dtcc-pyspade-native: Spade C++ library packaged for Python projects.

This package provides the Spade C++ Delaunay triangulation library
for use in Python projects that have C++ components.

No Python bindings are provided - this is purely for shipping the
C++ library via pip.

PyPI package name: dtcc-pyspade-native
GitHub repository: dtcc-pyspade-native
"""

import os
from pathlib import Path

__version__ = "0.1.1"

# Get the package installation directory
_PACKAGE_DIR = Path(__file__).parent.absolute()


def get_include_dir() -> str:
    """
    Get the directory containing Spade C++ header files.

    Returns:
        Absolute path to the include directory.

    Example:
        In setup.py:
        >>> import pyspade_native
        >>> include_dirs = [pyspade_native.get_include_dir()]
    """
    include_dir = _PACKAGE_DIR / "include"
    if not include_dir.exists():
        raise RuntimeError(
            f"Spade include directory not found at {include_dir}. "
            "The package may not have been installed correctly."
        )
    return str(include_dir)


def get_library_dir() -> str:
    """
    Get the directory containing Spade C++ libraries.

    Returns:
        Absolute path to the library directory.

    Example:
        In setup.py:
        >>> import pyspade_native
        >>> library_dirs = [pyspade_native.get_library_dir()]
    """
    lib_dir = _PACKAGE_DIR / "lib"
    if not lib_dir.exists():
        raise RuntimeError(
            f"Spade library directory not found at {lib_dir}. "
            "The package may not have been installed correctly."
        )
    return str(lib_dir)


def get_cmake_dir() -> str:
    """
    Get the directory containing CMake configuration files.

    Returns:
        Absolute path to the cmake directory.

    Example:
        In CMakeLists.txt:
        ```cmake
        find_package(Python REQUIRED COMPONENTS Interpreter)
        execute_process(
            COMMAND ${Python_EXECUTABLE} -c "import pyspade_native; print(pyspade_native.get_cmake_dir())"
            OUTPUT_VARIABLE PYSPADE_CMAKE_DIR
            OUTPUT_STRIP_TRAILING_WHITESPACE
        )
        find_package(pyspade_native REQUIRED PATHS ${PYSPADE_CMAKE_DIR})
        ```
    """
    cmake_dir = _PACKAGE_DIR / "cmake"
    if not cmake_dir.exists():
        raise RuntimeError(
            f"Spade CMake directory not found at {cmake_dir}. "
            "The package may not have been installed correctly."
        )
    return str(cmake_dir)


def get_libraries() -> dict:
    """
    Get paths to all Spade libraries.

    Returns:
        Dictionary with library names as keys and absolute paths as values.

    Example:
        >>> libs = pyspade_native.get_libraries()
        >>> print(libs['spade_wrapper'])
        >>> print(libs['spade_ffi'])
    """
    lib_dir = Path(get_library_dir())
    libraries = {}

    # Common library patterns
    patterns = {
        'spade_wrapper': ['libspade_wrapper.so', 'libspade_wrapper.dylib',
                         'libspade_wrapper.a', 'spade_wrapper.dll', 'spade_wrapper.lib'],
        'spade_ffi': ['libspade_ffi.so', 'libspade_ffi.dylib',
                     'libspade_ffi.a', 'spade_ffi.dll', 'spade_ffi.lib'],
    }

    for lib_name, file_patterns in patterns.items():
        for pattern in file_patterns:
            lib_path = lib_dir / pattern
            if lib_path.exists():
                libraries[lib_name] = str(lib_path)
                break

    return libraries


def print_info():
    """Print information about the dtcc-pyspade-native installation."""
    print("dtcc-pyspade-native Installation Info")
    print("=" * 60)
    print(f"Version: {__version__}")
    print(f"Package directory: {_PACKAGE_DIR}")
    print(f"Include directory: {get_include_dir()}")
    print(f"Library directory: {get_library_dir()}")
    print(f"CMake directory: {get_cmake_dir()}")
    print("\nAvailable libraries:")
    for name, path in get_libraries().items():
        print(f"  {name}: {path}")
    print("\nHeaders:")
    include_dir = Path(get_include_dir())
    for header in sorted(include_dir.glob("*.h")):
        print(f"  {header.name}")


__all__ = [
    "get_include_dir",
    "get_library_dir",
    "get_cmake_dir",
    "get_libraries",
    "print_info",
    "__version__",
]