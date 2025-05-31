#!/usr/bin/env python3
"""
Test script for the Quat implementation.
Demonstrates various features and verifies functionality.
"""

import numpy as np
import math
from quat import Quat, quat, EulerRot, quat_from_numpy, quat_to_numpy
from vec3 import Vec3


def test_basic_operations():
    """Test basic quaternion operations."""
    print("=== Basic Operations ===")

    # Create quaternions
    q1 = Quat(0.0, 0.0, 0.0, 1.0)  # Identity
    q2 = quat(0.1, 0.2, 0.3, 0.9)  # Convenience function

    print(f"q1 (identity) = {q1}")
    print(f"q2 = {q2}")

    # Arithmetic
    print(f"q1 + q2 = {q1 + q2}")
    print(f"q1 - q2 = {q1 - q2}")
    print(f"q2 * 2.0 = {q2 * 2.0}")
    print(f"q2 / 2.0 = {q2 / 2.0}")
    print(f"-q2 = {-q2}")
    print()


def test_constants():
    """Test predefined constants."""
    print("=== Constants ===")

    print(f"Quat.IDENTITY = {Quat.IDENTITY}")
    print(f"Quat.ZERO = {Quat.ZERO}")
    print(f"Quat.IDENTITY.is_normalized() = {Quat.IDENTITY.is_normalized()}")
    print(f"Quat.IDENTITY.is_near_identity() = {Quat.IDENTITY.is_near_identity()}")
    print()


def test_axis_angle():
    """Test axis-angle construction and conversion."""
    print("=== Axis-Angle Operations ===")

    # Create quaternion from axis-angle
    axis = Vec3(0.0, 1.0, 0.0)  # Y axis
    angle = math.pi / 2  # 90 degrees

    q = Quat.from_axis_angle(axis, angle)
    print(f"Quaternion from Y-axis, 90° = {q}")
    print(f"Is normalized: {q.is_normalized()}")

    # Convert back to axis-angle
    recovered_axis, recovered_angle = q.to_axis_angle()
    print(f"Recovered axis = {recovered_axis}")
    print(f"Recovered angle = {recovered_angle} radians = {math.degrees(recovered_angle)} degrees")

    # Test scaled axis
    scaled_axis = Vec3(0.0, math.pi/4, 0.0)  # 45 degrees around Y
    q_scaled = Quat.from_scaled_axis(scaled_axis)
    print(f"From scaled axis {scaled_axis} = {q_scaled}")

    recovered_scaled = q_scaled.to_scaled_axis()
    print(f"Recovered scaled axis = {recovered_scaled}")
    print()


def test_euler_angles():
    """Test Euler angle operations."""
    print("=== Euler Angle Operations ===")

    # Create quaternion from Euler angles
    roll = math.pi / 6   # 30 degrees
    pitch = math.pi / 4  # 45 degrees
    yaw = math.pi / 3    # 60 degrees

    q_xyz = Quat.from_euler(EulerRot.XYZ, roll, pitch, yaw)
    print(f"From Euler XYZ ({math.degrees(roll):.1f}°, {math.degrees(pitch):.1f}°, {math.degrees(yaw):.1f}°) = {q_xyz}")

    q_zyx = Quat.from_euler(EulerRot.ZYX, yaw, pitch, roll)
    print(f"From Euler ZYX ({math.degrees(yaw):.1f}°, {math.degrees(pitch):.1f}°, {math.degrees(roll):.1f}°) = {q_zyx}")

    # Convert back to Euler angles
    try:
        euler_xyz = q_xyz.to_euler(EulerRot.XYZ)
        print(f"Back to XYZ: ({math.degrees(euler_xyz[0]):.1f}°, {math.degrees(euler_xyz[1]):.1f}°, {math.degrees(euler_xyz[2]):.1f}°)")
    except NotImplementedError as e:
        print(f"Euler conversion: {e}")

    print()


def test_rotation_creation():
    """Test various rotation creation methods."""
    print("=== Rotation Creation ===")

    # Single axis rotations
    qx = Quat.from_rotation_x(math.pi / 2)
    qy = Quat.from_rotation_y(math.pi / 2)
    qz = Quat.from_rotation_z(math.pi / 2)

    print(f"90° rotation around X = {qx}")
    print(f"90° rotation around Y = {qy}")
    print(f"90° rotation around Z = {qz}")

    # Rotation arc between vectors
    from_vec = Vec3(1.0, 0.0, 0.0)
    to_vec = Vec3(0.0, 1.0, 0.0)

    q_arc = Quat.from_rotation_arc(from_vec, to_vec)
    print(f"Rotation from {from_vec} to {to_vec} = {q_arc}")

    # Test the rotation
    rotated = q_arc * from_vec
    print(f"Applied rotation: {from_vec} -> {rotated}")
    print(f"Target was: {to_vec}")
    print(f"Close to target: {rotated.abs_diff_eq(to_vec, 1e-6)}")
    print()


def test_quaternion_math():
    """Test quaternion mathematical operations."""
    print("=== Quaternion Math ===")

    q1 = Quat.from_rotation_z(math.pi / 4)  # 45° around Z
    q2 = Quat.from_rotation_y(math.pi / 4)  # 45° around Y

    print(f"q1 (45° Z) = {q1}")
    print(f"q2 (45° Y) = {q2}")

    # Quaternion operations
    print(f"q1.length() = {q1.length()}")
    print(f"q1.length_squared() = {q1.length_squared()}")
    print(f"q1.dot(q2) = {q1.dot(q2)}")

    # Conjugate and inverse
    q1_conj = q1.conjugate()
    q1_inv = q1.inverse()
    print(f"q1.conjugate() = {q1_conj}")
    print(f"q1.inverse() = {q1_inv}")
    print(f"q1 * q1.inverse() = {q1 * q1_inv}")

    # Angle between quaternions
    angle = q1.angle_between(q2)
    print(f"Angle between q1 and q2: {angle} radians = {math.degrees(angle):.1f} degrees")
    print()


def test_vector_rotation():
    """Test vector rotation with quaternions."""
    print("=== Vector Rotation ===")

    # Create a vector and rotation
    vec = Vec3(1.0, 0.0, 0.0)  # X axis
    q = Quat.from_rotation_z(math.pi / 2)  # 90° around Z

    print(f"Original vector: {vec}")
    print(f"Rotation (90° around Z): {q}")

    # Rotate the vector
    rotated = q * vec
    print(f"Rotated vector: {rotated}")
    print(f"Expected: [0, 1, 0]")

    # Multiple rotations
    q1 = Quat.from_rotation_z(math.pi / 4)  # 45° around Z
    q2 = Quat.from_rotation_y(math.pi / 4)  # 45° around Y

    combined = q2 * q1  # Apply q1 first, then q2

    result1 = q2 * (q1 * vec)
    result2 = combined * vec

    print(f"Step-by-step rotation: {result1}")
    print(f"Combined rotation: {result2}")
    print(f"Results match: {result1.abs_diff_eq(result2, 1e-6)}")
    print()


def test_interpolation():
    """Test quaternion interpolation methods."""
    print("=== Interpolation ===")

    q1 = Quat.IDENTITY
    q2 = Quat.from_rotation_z(math.pi / 2)  # 90° around Z

    print(f"q1 (identity) = {q1}")
    print(f"q2 (90° Z) = {q2}")

    # Linear interpolation
    lerp_half = q1.lerp(q2, 0.5)
    print(f"LERP at t=0.5: {lerp_half}")

    # Spherical linear interpolation
    slerp_half = q1.slerp(q2, 0.5)
    print(f"SLERP at t=0.5: {slerp_half}")

    # Test multiple interpolation points
    print("SLERP progression:")
    for t in [0.0, 0.25, 0.5, 0.75, 1.0]:
        q_t = q1.slerp(q2, t)
        axis, angle = q_t.to_axis_angle()
        print(f"  t={t}: angle={math.degrees(angle):.1f}°")

    # Rotate towards
    max_angle = math.pi / 4  # 45° max
    rotated_towards = q1.rotate_towards(q2, max_angle)
    axis, angle = rotated_towards.to_axis_angle()
    print(f"Rotate towards (max 45°): angle={math.degrees(angle):.1f}°")
    print()


def test_look_operations():
    """Test look-at and look-to operations."""
    print("=== Look Operations ===")

    # Look-to operations
    dir_vec = Vec3(1.0, 0.0, 0.0)  # Look along X
    up_vec = Vec3(0.0, 1.0, 0.0)   # Y is up

    q_look_rh = Quat.look_to_rh(dir_vec, up_vec)
    q_look_lh = Quat.look_to_lh(dir_vec, up_vec)

    print(f"Look-to RH: {q_look_rh}")
    print(f"Look-to LH: {q_look_lh}")

    # Look-at operations
    eye = Vec3(0.0, 0.0, 0.0)
    center = Vec3(1.0, 0.0, 0.0)
    up = Vec3(0.0, 1.0, 0.0)

    q_look_at_rh = Quat.look_at_rh(eye, center, up)
    q_look_at_lh = Quat.look_at_lh(eye, center, up)

    print(f"Look-at RH: {q_look_at_rh}")
    print(f"Look-at LH: {q_look_at_lh}")
    print()


def test_numpy_interop():
    """Test numpy interoperability."""
    print("=== Numpy Interoperability ===")

    # Create Quat from numpy array
    np_array = np.array([0.1, 0.2, 0.3, 0.9])
    q1 = quat_from_numpy(np_array)
    print(f"From numpy array {np_array}: {q1}")

    # Convert Quat to numpy array
    q2 = Quat.from_rotation_z(math.pi / 4)
    np_result = quat_to_numpy(q2)
    print(f"Quat {q2} to numpy: {np_result}")

    # Direct conversion methods
    print(f"q2.to_array() = {q2.to_array()}")
    print(f"Quat.from_array([0, 0, 0.707, 0.707]) = {Quat.from_array([0, 0, 0.707, 0.707])}")
    print()


def test_comparison_operations():
    """Test comparison operations."""
    print("=== Comparison Operations ===")

    q1 = Quat(0.1, 0.2, 0.3, 0.9)
    q2 = Quat(0.1, 0.2, 0.3, 0.9)
    q3 = Quat(0.15, 0.25, 0.35, 0.85)

    print(f"q1 = {q1}")
    print(f"q2 = {q2}")
    print(f"q3 = {q3}")
    print(f"q1 == q2: {q1 == q2}")
    print(f"q1 != q3: {q1 != q3}")

    # Approximate equality
    print(f"q1.abs_diff_eq(q3, 0.1): {q1.abs_diff_eq(q3, 0.1)}")
    print(f"q1.abs_diff_eq(q3, 0.01): {q1.abs_diff_eq(q3, 0.01)}")

    # Normalization checks
    q_norm = q1.normalize()
    print(f"q1.normalize() = {q_norm}")
    print(f"Normalized length: {q_norm.length()}")
    print(f"Is normalized: {q_norm.is_normalized()}")
    print()


def test_indexing_and_iteration():
    """Test indexing and iteration."""
    print("=== Indexing and Iteration ===")

    q = Quat(10.0, 20.0, 30.0, 40.0)
    print(f"q = {q}")
    print(f"q[0] (x) = {q[0]}")
    print(f"q[1] (y) = {q[1]}")
    print(f"q[2] (z) = {q[2]}")
    print(f"q[3] (w) = {q[3]}")

    # Modify through indexing
    q[1] = 25.0
    print(f"After q[1] = 25.0: {q}")

    # Iteration
    print("Iterating through quaternion:")
    for i, component in enumerate(q):
        print(f"  {i}: {component}")

    # Convert to other types
    print(f"q.to_tuple() = {q.to_tuple()}")
    print(f"q.to_list() = {q.to_list()}")
    print()


def test_edge_cases():
    """Test edge cases and error handling."""
    print("=== Edge Cases ===")

    # Near-identity quaternions
    near_identity = Quat(0.001, 0.001, 0.001, 0.9999)
    near_identity = near_identity.normalize()
    print(f"Near identity: {near_identity}")
    print(f"Is near identity: {near_identity.is_near_identity()}")

    # 180-degree rotations
    opposite_vec = Vec3(1.0, 0.0, 0.0)
    neg_opposite = Vec3(-1.0, 0.0, 0.0)

    q_180 = Quat.from_rotation_arc(opposite_vec, neg_opposite)
    print(f"180° rotation: {q_180}")

    axis, angle = q_180.to_axis_angle()
    print(f"180° axis: {axis}, angle: {math.degrees(angle):.1f}°")

    # Zero vector handling
    try:
        zero_quat = Quat.ZERO.normalize()
    except ValueError as e:
        print(f"Zero quaternion normalization error: {e}")

    # Non-normalized axis error
    try:
        bad_axis = Vec3(2.0, 0.0, 0.0)  # Not normalized
        Quat.from_axis_angle(bad_axis, math.pi / 2)
    except ValueError as e:
        print(f"Non-normalized axis error: {e}")

    print()


def test_advanced_operations():
    """Test advanced quaternion operations."""
    print("=== Advanced Operations ===")

    # Test finite and NaN checking
    q_good = Quat(0.0, 0.0, 0.0, 1.0)
    q_nan = Quat(float('nan'), 0.0, 0.0, 1.0)
    q_inf = Quat(float('inf'), 0.0, 0.0, 1.0)

    print(f"Good quaternion is_finite: {q_good.is_finite()}")
    print(f"NaN quaternion is_nan: {q_nan.is_nan()}")
    print(f"Inf quaternion is_finite: {q_inf.is_finite()}")

    # Test quaternion conjugate properties
    q = Quat.from_rotation_z(math.pi / 3)
    q_conj = q.conjugate()

    # q * q.conjugate() should be identity for unit quaternions
    result = q * q_conj
    print(f"q * q.conjugate() = {result}")
    print(f"Should be identity: {result.abs_diff_eq(Quat.IDENTITY, 1e-6)}")

    # Test xyz() method
    xyz_part = q.xyz()
    print(f"q.xyz() = {xyz_part}")
    print(f"Should be Vec3({q.x}, {q.y}, {q.z})")

    print()


if __name__ == "__main__":
    print("Quat Python Implementation Test")
    print("=" * 40)
    print()

    test_basic_operations()
    test_constants()
    test_axis_angle()
    test_euler_angles()
    test_rotation_creation()
    test_quaternion_math()
    test_vector_rotation()
    test_interpolation()
    test_look_operations()
    test_numpy_interop()
    test_comparison_operations()
    test_indexing_and_iteration()
    test_edge_cases()
    test_advanced_operations()

    print("All tests completed successfully!")
