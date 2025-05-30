import numpy as np
import math
from typing import Union, Tuple, Iterator
from pseudo_glam.vec3 import Vec3


class EulerRot:
    """Euler rotation order enumeration."""
    XYZ = "XYZ"
    XZY = "XZY"
    YXZ = "YXZ"
    YZX = "YZX"
    ZXY = "ZXY"
    ZYX = "ZYX"


class Quat:
    """A quaternion representing an orientation.

    This quaternion is intended to be of unit length but may denormalize due to
    floating point "error creep" which can occur when successive quaternion
    operations are applied.
    """

    # Constants
    ZERO = None      # Will be set after class definition
    IDENTITY = None
    NAN = None

    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0, w: float = 1.0):
        """Creates a new quaternion.

        This should generally not be called manually unless you know what you are doing.
        Use one of the other constructors instead such as identity or from_axis_angle.
        """
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.w = float(w)

    @classmethod
    def from_xyzw(cls, x: float, y: float, z: float, w: float) -> 'Quat':
        """Creates a new rotation quaternion.

        This function does not check if the input is normalized, it is up to the user to
        provide normalized input or to normalize the resulting quaternion.
        """
        return cls(x, y, z, w)

    @classmethod
    def from_array(cls, a: Union[list, np.ndarray]) -> 'Quat':
        """Creates a rotation quaternion from an array.

        This function does not check if the input is normalized.
        """
        return cls(a[0], a[1], a[2], a[3])

    @classmethod
    def from_vec4(cls, v: Tuple[float, float, float, float]) -> 'Quat':
        """Creates a new rotation quaternion from a 4D vector.

        This function does not check if the input is normalized.
        """
        return cls(v[0], v[1], v[2], v[3])

    @classmethod
    def from_slice(cls, slice_data: Union[list, np.ndarray]) -> 'Quat':
        """Creates a rotation quaternion from a slice.

        This function does not check if the input is normalized.
        """
        if len(slice_data) < 4:
            raise ValueError("slice must have at least 4 elements")
        return cls(slice_data[0], slice_data[1], slice_data[2], slice_data[3])

    def copy(self) -> 'Quat':
        """Returns a copy of self."""
        return Quat(self.x, self.y, self.z, self.w)

    def write_to_slice(self, slice_data: Union[list, np.ndarray]) -> None:
        """Writes the quaternion to an unaligned slice."""
        if len(slice_data) < 4:
            raise ValueError("slice must have at least 4 elements")
        slice_data[0] = self.x
        slice_data[1] = self.y
        slice_data[2] = self.z
        slice_data[3] = self.w

    @classmethod
    def from_axis_angle(cls, axis: Vec3, angle: float) -> 'Quat':
        """Create a quaternion for a normalized rotation axis and angle (in radians).

        The axis must be a unit vector.
        """
        if not axis.is_normalized():
            raise ValueError("axis must be normalized")

        half_angle = angle * 0.5
        s = math.sin(half_angle)
        c = math.cos(half_angle)
        v = axis * s
        return cls(v.x, v.y, v.z, c)

    @classmethod
    def from_scaled_axis(cls, v: Vec3) -> 'Quat':
        """Create a quaternion that rotates v.length() radians around v.normalize().

        from_scaled_axis(Vec3.ZERO) results in the identity quaternion.
        """
        length = v.length()
        if length == 0.0:
            return cls.IDENTITY
        else:
            return cls.from_axis_angle(v / length, length)

    @classmethod
    def from_rotation_x(cls, angle: float) -> 'Quat':
        """Creates a quaternion from the angle (in radians) around the x axis."""
        half_angle = angle * 0.5
        s = math.sin(half_angle)
        c = math.cos(half_angle)
        return cls(s, 0.0, 0.0, c)

    @classmethod
    def from_rotation_y(cls, angle: float) -> 'Quat':
        """Creates a quaternion from the angle (in radians) around the y axis."""
        half_angle = angle * 0.5
        s = math.sin(half_angle)
        c = math.cos(half_angle)
        return cls(0.0, s, 0.0, c)

    @classmethod
    def from_rotation_z(cls, angle: float) -> 'Quat':
        """Creates a quaternion from the angle (in radians) around the z axis."""
        half_angle = angle * 0.5
        s = math.sin(half_angle)
        c = math.cos(half_angle)
        return cls(0.0, 0.0, s, c)

    @classmethod
    def from_euler(cls, euler: str, a: float, b: float, c: float) -> 'Quat':
        """Creates a quaternion from the given Euler rotation sequence and the angles (in radians)."""
        return cls._from_euler_angles(euler, a, b, c)

    @classmethod
    def _from_euler_angles(cls, order: str, a: float, b: float, c: float) -> 'Quat':
        """Internal method to create quaternion from Euler angles."""
        # Convert to half angles
        a *= 0.5
        b *= 0.5
        c *= 0.5

        ca = math.cos(a)
        sa = math.sin(a)
        cb = math.cos(b)
        sb = math.sin(b)
        cc = math.cos(c)
        sc = math.sin(c)

        if order == EulerRot.XYZ:
            x = sa * cb * cc - ca * sb * sc
            y = ca * sb * cc + sa * cb * sc
            z = ca * cb * sc - sa * sb * cc
            w = ca * cb * cc + sa * sb * sc
        elif order == EulerRot.XZY:
            x = sa * cb * cc + ca * sb * sc
            y = ca * sb * cc - sa * cb * sc
            z = ca * cb * sc + sa * sb * cc
            w = ca * cb * cc - sa * sb * sc
        elif order == EulerRot.YXZ:
            x = sa * cb * cc + ca * sb * sc
            y = ca * sb * cc - sa * cb * sc
            z = ca * cb * sc - sa * sb * cc
            w = ca * cb * cc + sa * sb * sc
        elif order == EulerRot.YZX:
            x = sa * cb * cc - ca * sb * sc
            y = ca * sb * cc + sa * cb * sc
            z = ca * cb * sc + sa * sb * cc
            w = ca * cb * cc - sa * sb * sc
        elif order == EulerRot.ZXY:
            x = sa * cb * cc - ca * sb * sc
            y = ca * sb * cc + sa * cb * sc
            z = ca * cb * sc + sa * sb * cc
            w = ca * cb * cc - sa * sb * sc
        elif order == EulerRot.ZYX:
            x = sa * cb * cc + ca * sb * sc
            y = ca * sb * cc - sa * cb * sc
            z = ca * cb * sc + sa * sb * cc
            w = ca * cb * cc - sa * sb * sc
        else:
            raise ValueError(f"Unknown euler rotation order: {order}")

        return cls(x, y, z, w)

    @classmethod
    def from_rotation_arc(cls, from_vec: Vec3, to_vec: Vec3) -> 'Quat':
        """Gets the minimal rotation for transforming from to to.

        The rotation is in the plane spanned by the two vectors. Will rotate at most 180 degrees.
        The inputs must be unit vectors.
        """
        if not from_vec.is_normalized() or not to_vec.is_normalized():
            raise ValueError("from_vec and to_vec must be normalized")

        ONE_MINUS_EPS = 1.0 - 2.0 * 2.2204460492503131e-16  # f32::EPSILON equivalent
        dot = from_vec.dot(to_vec)

        if dot > ONE_MINUS_EPS:
            # 0° singularity: from ≈ to
            return cls.IDENTITY
        elif dot < -ONE_MINUS_EPS:
            # 180° singularity: from ≈ -to
            PI = math.pi
            return cls.from_axis_angle(from_vec.any_orthonormal_vector(), PI)
        else:
            c = from_vec.cross(to_vec)
            return cls(c.x, c.y, c.z, 1.0 + dot).normalize()

    @classmethod
    def from_rotation_arc_colinear(cls, from_vec: Vec3, to_vec: Vec3) -> 'Quat':
        """Gets the minimal rotation for transforming from to either to or -to.

        This means that the resulting quaternion will rotate from so that it is colinear with to.
        """
        if from_vec.dot(to_vec) < 0.0:
            return cls.from_rotation_arc(from_vec, -to_vec)
        else:
            return cls.from_rotation_arc(from_vec, to_vec)

    @classmethod
    def from_rotation_arc_2d(cls, from_vec: Tuple[float, float], to_vec: Tuple[float, float]) -> 'Quat':
        """Gets the minimal rotation for transforming from to to in 2D.

        The resulting rotation is around the z axis. Will rotate at most 180 degrees.
        """
        # Convert to Vec2-like behavior
        from_len = math.sqrt(from_vec[0]**2 + from_vec[1]**2)
        to_len = math.sqrt(to_vec[0]**2 + to_vec[1]**2)

        if abs(from_len - 1.0) > 1e-6 or abs(to_len - 1.0) > 1e-6:
            raise ValueError("from_vec and to_vec must be normalized")

        ONE_MINUS_EPSILON = 1.0 - 2.0 * 2.2204460492503131e-16
        dot = from_vec[0] * to_vec[0] + from_vec[1] * to_vec[1]

        if dot > ONE_MINUS_EPSILON:
            # 0° singularity: from ≈ to
            return cls.IDENTITY
        elif dot < -ONE_MINUS_EPSILON:
            # 180° singularity: from ≈ -to
            return cls(0.0, 0.0, 1.0, 0.0)  # 180° rotation around z
        else:
            # vector3 cross where z=0
            z = from_vec[0] * to_vec[1] - to_vec[0] * from_vec[1]
            w = 1.0 + dot
            # calculate length with x=0 and y=0 to normalize
            len_rcp = 1.0 / math.sqrt(z * z + w * w)
            return cls(0.0, 0.0, z * len_rcp, w * len_rcp)

    @classmethod
    def look_to_lh(cls, dir_vec: Vec3, up: Vec3) -> 'Quat':
        """Creates a quaternion rotation from a facing direction and an up direction.

        For a left-handed view coordinate system with +X=right, +Y=up and +Z=forward.
        """
        return cls.look_to_rh(-dir_vec, up)

    @classmethod
    def look_to_rh(cls, dir_vec: Vec3, up: Vec3) -> 'Quat':
        """Creates a quaternion rotation from facing direction and an up direction.

        For a right-handed view coordinate system with +X=right, +Y=up and +Z=back.
        """
        if not dir_vec.is_normalized() or not up.is_normalized():
            raise ValueError("dir_vec and up must be normalized")

        f = dir_vec
        s = f.cross(up).normalize()
        u = s.cross(f)

        return cls._from_rotation_axes(
            Vec3(s.x, u.x, -f.x),
            Vec3(s.y, u.y, -f.y),
            Vec3(s.z, u.z, -f.z)
        )

    @classmethod
    def look_at_lh(cls, eye: Vec3, center: Vec3, up: Vec3) -> 'Quat':
        """Creates a left-handed view matrix using a camera position, a focal point, and an up direction."""
        return cls.look_to_lh((center - eye).normalize(), up)

    @classmethod
    def look_at_rh(cls, eye: Vec3, center: Vec3, up: Vec3) -> 'Quat':
        """Creates a right-handed view matrix using a camera position, an up direction, and a focal point."""
        return cls.look_to_rh((center - eye).normalize(), up)

    @classmethod
    def _from_rotation_axes(cls, x_axis: Vec3, y_axis: Vec3, z_axis: Vec3) -> 'Quat':
        """From the columns of a 3x3 rotation matrix."""
        if not (x_axis.is_normalized() and y_axis.is_normalized() and z_axis.is_normalized()):
            raise ValueError("All axes must be normalized")

        # Based on https://github.com/microsoft/DirectXMath XMQuaternionRotationMatrix
        m00, m01, m02 = x_axis.x, x_axis.y, x_axis.z
        m10, m11, m12 = y_axis.x, y_axis.y, y_axis.z
        m20, m21, m22 = z_axis.x, z_axis.y, z_axis.z

        if m22 <= 0.0:
            # x^2 + y^2 >= z^2 + w^2
            dif10 = m11 - m00
            omm22 = 1.0 - m22
            if dif10 <= 0.0:
                # x^2 >= y^2
                four_xsq = omm22 - dif10
                inv4x = 0.5 / math.sqrt(four_xsq)
                return cls(
                    four_xsq * inv4x,
                    (m01 + m10) * inv4x,
                    (m02 + m20) * inv4x,
                    (m12 - m21) * inv4x,
                )
            else:
                # y^2 >= x^2
                four_ysq = omm22 + dif10
                inv4y = 0.5 / math.sqrt(four_ysq)
                return cls(
                    (m01 + m10) * inv4y,
                    four_ysq * inv4y,
                    (m12 + m21) * inv4y,
                    (m20 - m02) * inv4y,
                )
        else:
            # z^2 + w^2 >= x^2 + y^2
            sum10 = m11 + m00
            opm22 = 1.0 + m22
            if sum10 <= 0.0:
                # z^2 >= w^2
                four_zsq = opm22 - sum10
                inv4z = 0.5 / math.sqrt(four_zsq)
                return cls(
                    (m02 + m20) * inv4z,
                    (m12 + m21) * inv4z,
                    four_zsq * inv4z,
                    (m01 - m10) * inv4z,
                )
            else:
                # w^2 >= z^2
                four_wsq = opm22 + sum10
                inv4w = 0.5 / math.sqrt(four_wsq)
                return cls(
                    (m12 - m21) * inv4w,
                    (m20 - m02) * inv4w,
                    (m01 - m10) * inv4w,
                    four_wsq * inv4w,
                )

    def to_axis_angle(self) -> Tuple[Vec3, float]:
        """Returns the rotation axis (normalized) and angle (in radians) of self."""
        EPSILON = 1.0e-8
        v = Vec3(self.x, self.y, self.z)
        length = v.length()
        if length >= EPSILON:
            angle = 2.0 * math.atan2(length, self.w)
            axis = v / length
            return (axis, angle)
        else:
            return (Vec3.X, 0.0)

    def to_scaled_axis(self) -> Vec3:
        """Returns the rotation axis scaled by the rotation in radians."""
        axis, angle = self.to_axis_angle()
        return axis * angle

    def to_euler(self, order: str) -> Tuple[float, float, float]:
        """Returns the rotation angles for the given euler rotation sequence."""
        return self._to_euler_angles(order)

    def _to_euler_angles(self, order: str) -> Tuple[float, float, float]:
        """Internal method to convert quaternion to Euler angles."""
        # Convert quaternion to rotation matrix elements we need
        xx = self.x * self.x
        yy = self.y * self.y
        zz = self.z * self.z
        ww = self.w * self.w
        xy = self.x * self.y
        xz = self.x * self.z
        yz = self.y * self.z
        wx = self.w * self.x
        wy = self.w * self.y
        wz = self.w * self.z

        if order == EulerRot.XYZ:
            # Extract XYZ Euler angles
            m12 = 2.0 * (yz + wx)
            m12 = max(-1.0, min(1.0, m12))  # Clamp to handle numerical errors

            if abs(m12) >= 1.0:
                # Gimbal lock case
                x = math.asin(m12)
                y = math.atan2(-2.0 * (xz - wy), ww - xx + yy - zz)
                z = 0.0
            else:
                x = math.asin(m12)
                y = math.atan2(-2.0 * (xz - wy), ww - xx - yy + zz)
                z = math.atan2(-2.0 * (xy - wz), ww - xx + yy - zz)

            return (x, y, z)

        elif order == EulerRot.ZYX:
            # Extract ZYX Euler angles (yaw, pitch, roll)
            m21 = 2.0 * (xy + wz)
            m21 = max(-1.0, min(1.0, m21))  # Clamp to handle numerical errors

            if abs(m21) >= 1.0:
                # Gimbal lock case
                z = 0.0
                y = math.asin(-m21)
                x = math.atan2(2.0 * (yz - wx), ww + xx - yy - zz)
            else:
                z = math.atan2(2.0 * (xy + wz), ww + xx - yy - zz)
                y = math.asin(-m21)
                x = math.atan2(2.0 * (yz + wx), ww - xx + yy - zz)

            return (x, y, z)

        # For other orders, implement similar logic
        # This is a simplified implementation - full implementation would handle all 6 orders
        else:
            raise NotImplementedError(f"Euler order {order} not yet implemented")

    def to_array(self) -> np.ndarray:
        """Returns [x, y, z, w] as numpy array."""
        return np.array([self.x, self.y, self.z, self.w])

    def xyz(self) -> Vec3:
        """Returns the vector part of the quaternion."""
        return Vec3(self.x, self.y, self.z)

    def conjugate(self) -> 'Quat':
        """Returns the quaternion conjugate of self.

        For a unit quaternion the conjugate is also the inverse.
        """
        return Quat(-self.x, -self.y, -self.z, self.w)

    def inverse(self) -> 'Quat':
        """Returns the inverse of a normalized quaternion.

        Typically quaternion inverse returns the conjugate of a normalized quaternion.
        Because self is assumed to already be unit length this method does not normalize
        before returning the conjugate.
        """
        if not self.is_normalized():
            raise ValueError("quaternion must be normalized")
        return self.conjugate()

    def dot(self, rhs: 'Quat') -> float:
        """Computes the dot product of self and rhs.

        The dot product is equal to the cosine of the angle between two quaternion rotations.
        """
        return self.x * rhs.x + self.y * rhs.y + self.z * rhs.z + self.w * rhs.w

    def length(self) -> float:
        """Computes the length of self."""
        return math.sqrt(self.dot(self))

    def length_squared(self) -> float:
        """Computes the squared length of self.

        This is generally faster than length() as it avoids a square root operation.
        """
        return self.dot(self)

    def length_recip(self) -> float:
        """Computes 1.0 / length().

        For valid results, self must not be of length zero.
        """
        return 1.0 / self.length()

    def normalize(self) -> 'Quat':
        """Returns self normalized to length 1.0.

        For valid results, self must not be of length zero.
        """
        length = self.length()
        if length == 0.0:
            raise ValueError("Cannot normalize zero quaternion")
        inv_length = 1.0 / length
        return Quat(self.x * inv_length, self.y * inv_length, self.z * inv_length, self.w * inv_length)

    def is_finite(self) -> bool:
        """Returns True if, and only if, all elements are finite.

        If any element is either NaN, positive or negative infinity, this will return False.
        """
        return (math.isfinite(self.x) and math.isfinite(self.y) and
                math.isfinite(self.z) and math.isfinite(self.w))

    def is_nan(self) -> bool:
        """Returns True if any elements are NaN."""
        return (math.isnan(self.x) or math.isnan(self.y) or
                math.isnan(self.z) or math.isnan(self.w))

    def is_normalized(self) -> bool:
        """Returns whether self is of length 1.0 or not.

        Uses a precision threshold of 1e-6.
        """
        return abs(self.length_squared() - 1.0) <= 1e-6

    def is_near_identity(self) -> bool:
        """Returns whether self is near the identity quaternion."""
        threshold_angle = 0.002847144460678101  # ~0.00284714461 rad
        positive_w_angle = math.acos(abs(self.w)) * 2.0
        return positive_w_angle < threshold_angle

    def angle_between(self, rhs: 'Quat') -> float:
        """Returns the angle (in radians) for the minimal rotation for transforming this quaternion into another.

        Both quaternions must be normalized.
        """
        if not (self.is_normalized() and rhs.is_normalized()):
            raise ValueError("Both quaternions must be normalized")
        return math.acos(abs(self.dot(rhs))) * 2.0

    def rotate_towards(self, rhs: 'Quat', max_angle: float) -> 'Quat':
        """Rotates towards rhs up to max_angle (in radians).

        When max_angle is 0.0, the result will be equal to self. When max_angle is equal to
        self.angle_between(rhs), the result will be equal to rhs.
        """
        if not (self.is_normalized() and rhs.is_normalized()):
            raise ValueError("Both quaternions must be normalized")

        angle = self.angle_between(rhs)
        if angle <= 1e-4:
            return rhs

        s = max(-1.0, min(1.0, max_angle / angle))
        return self.slerp(rhs, s)

    def abs_diff_eq(self, rhs: 'Quat', max_abs_diff: float) -> bool:
        """Returns true if the absolute difference of all elements between self and rhs
        is less than or equal to max_abs_diff.
        """
        return (abs(self.x - rhs.x) <= max_abs_diff and
                abs(self.y - rhs.y) <= max_abs_diff and
                abs(self.z - rhs.z) <= max_abs_diff and
                abs(self.w - rhs.w) <= max_abs_diff)

    def _lerp_impl(self, end: 'Quat', s: float) -> 'Quat':
        """Internal linear interpolation implementation."""
        return (self * (1.0 - s) + end * s).normalize()

    def lerp(self, end: 'Quat', s: float) -> 'Quat':
        """Performs a linear interpolation between self and rhs based on the value s.

        When s is 0.0, the result will be equal to self. When s is 1.0, the result will be equal to end.
        """
        if not (self.is_normalized() and end.is_normalized()):
            raise ValueError("Both quaternions must be normalized")

        # Calculate the bias, if the dot product is positive or zero, there is no bias
        # but if it is negative, we want to flip the 'end' rotation components
        dot = self.dot(end)
        if dot < 0.0:
            end = -end

        return self._lerp_impl(end, s)

    def slerp(self, end: 'Quat', s: float) -> 'Quat':
        """Performs a spherical linear interpolation between self and end based on the value s.

        When s is 0.0, the result will be equal to self. When s is 1.0, the result will be equal to end.
        """
        if not (self.is_normalized() and end.is_normalized()):
            raise ValueError("Both quaternions must be normalized")

        # Note that a rotation can be represented by two quaternions: q and -q.
        # The slerp path between q and end will be different from the path between -q and end.
        # One path will take the long way around and one will take the short way.
        # In order to correct for this, the dot product between self and end should be positive.
        # If the dot product is negative, slerp between self and -end.
        dot = self.dot(end)
        if dot < 0.0:
            end = -end
            dot = -dot

        DOT_THRESHOLD = 1.0 - 2.2204460492503131e-16  # 1.0 - f32::EPSILON
        if dot > DOT_THRESHOLD:
            # If above threshold perform linear interpolation to avoid divide by zero
            return self._lerp_impl(end, s)
        else:
            theta = math.acos(dot)

            scale1 = math.sin(theta * (1.0 - s))
            scale2 = math.sin(theta * s)
            theta_sin = math.sin(theta)

            return ((self * scale1) + (end * scale2)) * (1.0 / theta_sin)

    def mul_vec3(self, rhs: Vec3) -> Vec3:
        """Multiplies a quaternion and a 3D vector, returning the rotated vector."""
        if not self.is_normalized():
            raise ValueError("quaternion must be normalized")

        # Quaternion-vector multiplication using the formula:
        # v' = v + 2.0 * cross(q.xyz, cross(q.xyz, v) + q.w * v)
        qvec = Vec3(self.x, self.y, self.z)
        uv = qvec.cross(rhs)
        uuv = qvec.cross(uv)
        return rhs + (uv * self.w + uuv) * 2.0

    def mul_quat(self, rhs: 'Quat') -> 'Quat':
        """Multiplies two quaternions.

        If they each represent a rotation, the result will represent the combined rotation.
        Note that due to floating point rounding the result may not be perfectly normalized.
        """
        # Quaternion multiplication formula:
        # (q1 * q2).w = q1.w * q2.w - q1.x * q2.x - q1.y * q2.y - q1.z * q2.z
        # (q1 * q2).x = q1.w * q2.x + q1.x * q2.w + q1.y * q2.z - q1.z * q2.y
        # (q1 * q2).y = q1.w * q2.y - q1.x * q2.z + q1.y * q2.w + q1.z * q2.x
        # (q1 * q2).z = q1.w * q2.z + q1.x * q2.y - q1.y * q2.x + q1.z * q2.w

        w = self.w * rhs.w - self.x * rhs.x - self.y * rhs.y - self.z * rhs.z
        x = self.w * rhs.x + self.x * rhs.w + self.y * rhs.z - self.z * rhs.y
        y = self.w * rhs.y - self.x * rhs.z + self.y * rhs.w + self.z * rhs.x
        z = self.w * rhs.z + self.x * rhs.y - self.y * rhs.x + self.z * rhs.w

        return Quat(x, y, z, w)

    # Arithmetic operators
    def __add__(self, other: 'Quat') -> 'Quat':
        """Adds two quaternions.

        The sum is not guaranteed to be normalized.
        Note that addition is not the same as combining the rotations represented by the
        two quaternions! That corresponds to multiplication.
        """
        return Quat(self.x + other.x, self.y + other.y, self.z + other.z, self.w + other.w)

    def __sub__(self, other: 'Quat') -> 'Quat':
        """Subtracts the rhs quaternion from self.

        The difference is not guaranteed to be normalized.
        """
        return Quat(self.x - other.x, self.y - other.y, self.z - other.z, self.w - other.w)

    def __mul__(self, other: Union['Quat', Vec3, float]) -> Union['Quat', Vec3]:
        """Multiplies with another quaternion, vector, or scalar."""
        if isinstance(other, Quat):
            return self.mul_quat(other)
        elif isinstance(other, Vec3):
            return self.mul_vec3(other)
        elif isinstance(other, (int, float)):
            return Quat(self.x * other, self.y * other, self.z * other, self.w * other)
        else:
            return NotImplemented

    def __rmul__(self, other: Union[float, int]) -> 'Quat':
        """Right multiplication by scalar."""
        if isinstance(other, (int, float)):
            return Quat(self.x * other, self.y * other, self.z * other, self.w * other)
        else:
            return NotImplemented

    def __imul__(self, other: 'Quat') -> 'Quat':
        """In-place quaternion multiplication."""
        if isinstance(other, Quat):
            result = self.mul_quat(other)
            self.x, self.y, self.z, self.w = result.x, result.y, result.z, result.w
            return self
        else:
            return NotImplemented

    def __truediv__(self, other: float) -> 'Quat':
        """Divides a quaternion by a scalar value.

        The quotient is not guaranteed to be normalized.
        """
        if isinstance(other, (int, float)):
            return Quat(self.x / other, self.y / other, self.z / other, self.w / other)
        else:
            return NotImplemented

    def __neg__(self) -> 'Quat':
        """Negates the quaternion."""
        return Quat(-self.x, -self.y, -self.z, -self.w)

    def __pos__(self) -> 'Quat':
        """Returns a copy of the quaternion."""
        return Quat(self.x, self.y, self.z, self.w)

    # Comparison operators
    def __eq__(self, other: 'Quat') -> bool:
        """Returns True if all components are equal."""
        if not isinstance(other, Quat):
            return False
        return (self.x == other.x and self.y == other.y and
                self.z == other.z and self.w == other.w)

    def __ne__(self, other: 'Quat') -> bool:
        """Returns True if any components are not equal."""
        return not self.__eq__(other)

    # Indexing (though less common for quaternions)
    def __getitem__(self, index: int) -> float:
        """Get component by index: 0=x, 1=y, 2=z, 3=w."""
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        elif index == 2:
            return self.z
        elif index == 3:
            return self.w
        else:
            raise IndexError("index out of bounds")

    def __setitem__(self, index: int, value: float) -> None:
        """Set component by index: 0=x, 1=y, 2=z, 3=w."""
        if index == 0:
            self.x = value
        elif index == 1:
            self.y = value
        elif index == 2:
            self.z = value
        elif index == 3:
            self.w = value
        else:
            raise IndexError("index out of bounds")

    # Iterator support
    def __iter__(self) -> Iterator[float]:
        """Iterate over quaternion components."""
        yield self.x
        yield self.y
        yield self.z
        yield self.w

    def __len__(self) -> int:
        """Returns 4 (number of components)."""
        return 4

    # String representation
    def __str__(self) -> str:
        """String representation."""
        return f"[{self.x}, {self.y}, {self.z}, {self.w}]"

    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"Quat({self.x}, {self.y}, {self.z}, {self.w})"

    # Type conversions
    def to_tuple(self) -> Tuple[float, float, float, float]:
        """Convert to tuple (x, y, z, w)."""
        return (self.x, self.y, self.z, self.w)

    @classmethod
    def from_tuple(cls, t: Tuple[float, float, float, float]) -> 'Quat':
        """Create from tuple (x, y, z, w)."""
        return cls(t[0], t[1], t[2], t[3])


# Initialize constants after class definition
Quat.ZERO = Quat(0.0, 0.0, 0.0, 0.0)
Quat.IDENTITY = Quat(0.0, 0.0, 0.0, 1.0)
Quat.NAN = Quat(float('nan'), float('nan'), float('nan'), float('nan'))
