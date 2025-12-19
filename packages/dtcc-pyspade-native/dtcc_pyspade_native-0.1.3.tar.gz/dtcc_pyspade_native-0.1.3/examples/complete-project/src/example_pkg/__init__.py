"""
Example package demonstrating dtcc-pyspade-native usage.

This package uses Spade C++ library for triangulation in its C++ backend.
"""

from ._geometry_core import triangulate

__version__ = "0.1.0"
__all__ = ["triangulate"]