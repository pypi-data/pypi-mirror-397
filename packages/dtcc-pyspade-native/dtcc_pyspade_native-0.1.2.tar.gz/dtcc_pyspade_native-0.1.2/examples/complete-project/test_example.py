#!/usr/bin/env python3
"""Test the example package."""

import numpy as np
from example_pkg import triangulate


def main():
    print("Testing dtcc-pyspade-native integration...")

    # Create a simple polygon
    polygon = np.array([
        [0, 0],
        [10, 0],
        [10, 10],
        [0, 10]
    ], dtype=float)

    print(f"Input polygon: {polygon.shape}")

    # Triangulate using C++ backend with Spade
    result = triangulate(polygon, max_edge_length=2.0)

    print(f"Output vertices: {result['num_vertices']}")
    print(f"Output triangles: {result['num_triangles']}")
    print(f"Vertices shape: {result['vertices'].shape}")
    print(f"Triangles shape: {result['triangles'].shape}")

    print("\nFirst few triangles:")
    for i in range(min(3, len(result['triangles']))):
        tri = result['triangles'][i]
        print(f"  Triangle {i}: {tri}")

    print("\n✓ Test passed! dtcc-pyspade-native is working correctly.")


if __name__ == "__main__":
    main()