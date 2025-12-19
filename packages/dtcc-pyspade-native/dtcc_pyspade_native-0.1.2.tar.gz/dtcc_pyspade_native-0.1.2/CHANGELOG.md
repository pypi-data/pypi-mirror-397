# Changelog

All notable changes to dtcc-pyspade-native will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive release documentation in RELEASING.md
- Version management script to update all version references
- Automated changelog management system with three integrated scripts

## [0.1.0] - 2024-10-22

### Added
- Initial release of dtcc-pyspade-native
- C++ Spade triangulation library packaged for Python
- CMake `find_package()` support
- Pre-built wheels for Linux, macOS (Intel/ARM), Windows
- Python helper API for getting library paths
- Complete example project demonstrating usage
- Comprehensive documentation
- CI/CD with GitHub Actions
- Support for Python 3.8-3.12

### Features
- Constrained Delaunay triangulation (CDT)
- Mesh refinement with quality controls
- Support for polygons with holes
- Interior constraint loops
- Cross-platform support

[Unreleased]: https://github.com/dtcc-platform/dtcc-pyspade-native/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/dtcc-platform/dtcc-pyspade-native/releases/tag/v0.1.0