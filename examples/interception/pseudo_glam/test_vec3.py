#!/usr/bin/env python3
"""
Test script for the Vec3 implementation.
Demonstrates various features and verifies functionality.
"""

import numpy as np
import math
from vec3 import Vec3, vec3, vec3_from_numpy, vec3_to_numpy


def test_basic_operations():
    """Test basic vector operations."""
    print("=== Basic Operations ===")

    # Create vectors
    v1 = Vec3(1.0, 2.0, 3.0)
    v2 = vec3(4.0, 5.0, 6.0)

    print(f"v1 = {v1}")
    print(f"v2 = {v2}")

    # Arithmetic
    print(f"v1 + v2 = {v1 + v2}")
    print(f"v1 - v2 = {v1 - v2}")
    print(f"v1 * v2 = {v1 * v2}")
    print(f"v1 / v2 = {v1 / v2}")
    print(f"v1 * 2.0 = {v1 * 2.0}")
    print(f"-v1 = {-v1}")
    print()


def test_vector_math():
    """Test vector mathematical operations."""
    print("=== Vector Math ===")

    v1 = Vec3(1.0, 0.0, 0.0)
    v2 = Vec3(0.0, 1.0, 0.0)
    v3 = Vec3(3.0, 4.0, 0.0)

    print(f"v1 = {v1}")
    print(f"v2 = {v2}")
    print(f"v3 = {v3}")

    # Dot product
    print(f"v1.dot(v2) = {v1.dot(v2)}")
    print(f"v1.dot(v1) = {v1.dot(v1)}")

    # Cross product
    cross = v1.cross(v2)
    print(f"v1.cross(v2) = {cross}")

    # Length operations
    print(f"v3.length() = {v3.length()}")
    print(f"v3.length_squared() = {v3.length_squared()}")

    # Normalization
    v3_norm = v3.normalize()
    print(f"v3.normalize() = {v3_norm}")
    print(f"v3_norm.length() = {v3_norm.length()}")
    print(f"v3_norm.is_normalized() = {v3_norm.is_normalized()}")
    print()


def test_constants():
    """Test predefined constants."""
    print("=== Constants ===")

    print(f"Vec3.ZERO = {Vec3.ZERO}")
    print(f"Vec3.ONE = {Vec3.ONE}")
    print(f"Vec3.X = {Vec3.X}")
    print(f"Vec3.Y = {Vec3.Y}")
    print(f"Vec3.Z = {Vec3.Z}")
    print(f"Vec3.AXES = {Vec3.AXES}")
    print()


def test_utility_methods():
    """Test utility methods."""
    print("=== Utility Methods ===")

    v1 = Vec3(1.5, -2.3, 3.7)
    v2 = Vec3(0.5, 4.2, -1.1)

    print(f"v1 = {v1}")
    print(f"v2 = {v2}")

    # Min/Max operations
    print(f"v1.min(v2) = {v1.min(v2)}")
    print(f"v1.max(v2) = {v1.max(v2)}")
    print(f"v1.min_element() = {v1.min_element()}")
    print(f"v1.max_element() = {v1.max_element()}")

    # Floor/Ceil operations
    print(f"v1.floor() = {v1.floor()}")
    print(f"v1.ceil() = {v1.ceil()}")
    print(f"v1.round() = {v1.round()}")
    print(f"v1.abs() = {v1.abs()}")

    # Linear interpolation
    lerp_result = v1.lerp(v2, 0.5)
    print(f"v1.lerp(v2, 0.5) = {lerp_result}")

    # Midpoint
    print(f"v1.midpoint(v2) = {v1.midpoint(v2)}")
    print()


def test_numpy_interop():
    """Test numpy interoperability."""
    print("=== Numpy Interoperability ===")

    # Create Vec3 from numpy array
    np_array = np.array([1.0, 2.0, 3.0])
    v1 = vec3_from_numpy(np_array)
    print(f"From numpy array {np_array}: {v1}")

    # Convert Vec3 to numpy array
    v2 = Vec3(4.0, 5.0, 6.0)
    np_result = vec3_to_numpy(v2)
    print(f"Vec3 {v2} to numpy: {np_result}")

    # Direct conversion methods
    print(f"v2.to_array() = {v2.to_array()}")
    print(f"Vec3.from_array([7, 8, 9]) = {Vec3.from_array([7, 8, 9])}")
    print()


def test_geometric_operations():
    """Test geometric operations."""
    print("=== Geometric Operations ===")

    # Test reflection
    incident = Vec3(1.0, -1.0, 0.0).normalize()
    normal = Vec3(0.0, 1.0, 0.0)
    reflected = incident.reflect(normal)
    print(f"Incident: {incident}")
    print(f"Normal: {normal}")
    print(f"Reflected: {reflected}")

    # Test projection
    v1 = Vec3(3.0, 4.0, 0.0)
    v2 = Vec3(1.0, 0.0, 0.0)
    projection = v1.project_onto(v2)
    rejection = v1.reject_from(v2)
    print(f"v1 = {v1}")
    print(f"v2 = {v2}")
    print(f"v1.project_onto(v2) = {projection}")
    print(f"v1.reject_from(v2) = {rejection}")

    # Test angle between vectors
    angle = v1.angle_between(v2)
    print(f"Angle between v1 and v2: {angle} radians = {math.degrees(angle)} degrees")

    # Test distance
    v3 = Vec3(0.0, 0.0, 0.0)
    v4 = Vec3(3.0, 4.0, 0.0)
    distance = v3.distance(v4)
    print(f"Distance from {v3} to {v4}: {distance}")
    print()


def test_comparison_operations():
    """Test comparison operations."""
    print("=== Comparison Operations ===")

    v1 = Vec3(1.0, 2.0, 3.0)
    v2 = Vec3(2.0, 1.0, 4.0)

    print(f"v1 = {v1}")
    print(f"v2 = {v2}")
    print(f"v1 == v2: {v1 == v2}")
    print(f"v1 != v2: {v1 != v2}")
    print(f"v1.cmpeq(v2): {v1.cmpeq(v2)}")
    print(f"v1.cmplt(v2): {v1.cmplt(v2)}")
    print(f"v1.cmpgt(v2): {v1.cmpgt(v2)}")

    # Test approximate equality
    v3 = Vec3(1.0001, 2.0001, 3.0001)
    print(f"v3 = {v3}")
    print(f"v1.abs_diff_eq(v3, 0.001): {v1.abs_diff_eq(v3, 0.001)}")
    print(f"v1.abs_diff_eq(v3, 0.0001): {v1.abs_diff_eq(v3, 0.0001)}")
    print()


def test_indexing():
    """Test indexing and iteration."""
    print("=== Indexing and Iteration ===")

    v = Vec3(10.0, 20.0, 30.0)
    print(f"v = {v}")
    print(f"v[0] = {v[0]}")
    print(f"v[1] = {v[1]}")
    print(f"v[2] = {v[2]}")

    # Modify through indexing
    v[1] = 25.0
    print(f"After v[1] = 25.0: {v}")

    # Iteration
    print("Iterating through vector:")
    for i, component in enumerate(v):
        print(f"  {i}: {component}")

    # Convert to other types
    print(f"v.to_tuple() = {v.to_tuple()}")
    print(f"v.to_list() = {v.to_list()}")
    print()


if __name__ == "__main__":
    print("Vec3 Python Implementation Test")
    print("=" * 40)
    print()

    test_basic_operations()
    test_vector_math()
    test_constants()
    test_utility_methods()
    test_numpy_interop()
    test_geometric_operations()
    test_comparison_operations()
    test_indexing()

    print("All tests completed successfully!")
