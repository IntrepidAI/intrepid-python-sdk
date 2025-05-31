import numpy as np
import math
from typing import Union, Tuple, Optional, Iterator


def vec3(x: float, y: float, z: float) -> 'Vec3':
    """Creates a 3-dimensional vector."""
    return Vec3(x, y, z)


class Vec3:
    """A 3-dimensional vector."""

    # Constants
    ZERO = None  # Will be set after class definition
    ONE = None
    NEG_ONE = None
    X = None
    Y = None
    Z = None
    NEG_X = None
    NEG_Y = None
    NEG_Z = None
    AXES = None

    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        """Creates a new vector."""
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    @classmethod
    def splat(cls, v: float) -> 'Vec3':
        """Creates a vector with all elements set to v."""
        return cls(v, v, v)

    def copy(self) -> 'Vec3':
        """Returns a copy of self."""
        return Vec3(self.x, self.y, self.z)

    def map(self, f) -> 'Vec3':
        """Returns a vector containing each element of self modified by a mapping function f."""
        return Vec3(f(self.x), f(self.y), f(self.z))

    @classmethod
    def select(cls, mask: Tuple[bool, bool, bool], if_true: 'Vec3', if_false: 'Vec3') -> 'Vec3':
        """Creates a vector from the elements in if_true and if_false, selecting which to use for each element."""
        return cls(
            if_true.x if mask[0] else if_false.x,
            if_true.y if mask[1] else if_false.y,
            if_true.z if mask[2] else if_false.z
        )

    @classmethod
    def from_array(cls, a: Union[list, np.ndarray]) -> 'Vec3':
        """Creates a new vector from an array."""
        return cls(a[0], a[1], a[2])

    def to_array(self) -> np.ndarray:
        """Returns [x, y, z] as numpy array."""
        return np.array([self.x, self.y, self.z])

    @classmethod
    def from_slice(cls, slice_data: Union[list, np.ndarray]) -> 'Vec3':
        """Creates a vector from the first 3 values in slice."""
        if len(slice_data) < 3:
            raise ValueError("slice must have at least 3 elements")
        return cls(slice_data[0], slice_data[1], slice_data[2])

    def write_to_slice(self, slice_data: Union[list, np.ndarray]) -> None:
        """Writes the elements of self to the first 3 elements in slice."""
        if len(slice_data) < 3:
            raise ValueError("slice must have at least 3 elements")
        slice_data[0] = self.x
        slice_data[1] = self.y
        slice_data[2] = self.z

    def extend(self, w: float) -> Tuple[float, float, float, float]:
        """Creates a 4D vector from self and the given w value."""
        return (self.x, self.y, self.z, w)

    def truncate(self) -> Tuple[float, float]:
        """Creates a 2D vector from the x and y elements of self, discarding z."""
        return (self.x, self.y)

    def with_x(self, x: float) -> 'Vec3':
        """Creates a 3D vector from self with the given value of x."""
        return Vec3(x, self.y, self.z)

    def with_y(self, y: float) -> 'Vec3':
        """Creates a 3D vector from self with the given value of y."""
        return Vec3(self.x, y, self.z)

    def with_z(self, z: float) -> 'Vec3':
        """Creates a 3D vector from self with the given value of z."""
        return Vec3(self.x, self.y, z)

    def dot(self, rhs: 'Vec3') -> float:
        """Computes the dot product of self and rhs."""
        return self.x * rhs.x + self.y * rhs.y + self.z * rhs.z

    def dot_into_vec(self, rhs: 'Vec3') -> 'Vec3':
        """Returns a vector where every component is the dot product of self and rhs."""
        dot_product = self.dot(rhs)
        return Vec3.splat(dot_product)

    def cross(self, rhs: 'Vec3') -> 'Vec3':
        """Computes the cross product of self and rhs."""
        return Vec3(
            self.y * rhs.z - rhs.y * self.z,
            self.z * rhs.x - rhs.z * self.x,
            self.x * rhs.y - rhs.x * self.y
        )

    def min(self, rhs: 'Vec3') -> 'Vec3':
        """Returns a vector containing the minimum values for each element of self and rhs."""
        return Vec3(
            min(self.x, rhs.x),
            min(self.y, rhs.y),
            min(self.z, rhs.z)
        )

    def max(self, rhs: 'Vec3') -> 'Vec3':
        """Returns a vector containing the maximum values for each element of self and rhs."""
        return Vec3(
            max(self.x, rhs.x),
            max(self.y, rhs.y),
            max(self.z, rhs.z)
        )

    def clamp(self, min_vec: 'Vec3', max_vec: 'Vec3') -> 'Vec3':
        """Component-wise clamping of values."""
        return self.max(min_vec).min(max_vec)

    def min_element(self) -> float:
        """Returns the horizontal minimum of self."""
        return min(self.x, self.y, self.z)

    def max_element(self) -> float:
        """Returns the horizontal maximum of self."""
        return max(self.x, self.y, self.z)

    def min_position(self) -> int:
        """Returns the index of the first minimum element of self."""
        min_val = self.x
        index = 0
        if self.y < min_val:
            min_val = self.y
            index = 1
        if self.z < min_val:
            index = 2
        return index

    def max_position(self) -> int:
        """Returns the index of the first maximum element of self."""
        max_val = self.x
        index = 0
        if self.y > max_val:
            max_val = self.y
            index = 1
        if self.z > max_val:
            index = 2
        return index

    def element_sum(self) -> float:
        """Returns the sum of all elements of self."""
        return self.x + self.y + self.z

    def element_product(self) -> float:
        """Returns the product of all elements of self."""
        return self.x * self.y * self.z

    def cmpeq(self, rhs: 'Vec3') -> Tuple[bool, bool, bool]:
        """Returns a mask containing the result of a == comparison for each element."""
        return (self.x == rhs.x, self.y == rhs.y, self.z == rhs.z)

    def cmpne(self, rhs: 'Vec3') -> Tuple[bool, bool, bool]:
        """Returns a mask containing the result of a != comparison for each element."""
        return (self.x != rhs.x, self.y != rhs.y, self.z != rhs.z)

    def cmpge(self, rhs: 'Vec3') -> Tuple[bool, bool, bool]:
        """Returns a mask containing the result of a >= comparison for each element."""
        return (self.x >= rhs.x, self.y >= rhs.y, self.z >= rhs.z)

    def cmpgt(self, rhs: 'Vec3') -> Tuple[bool, bool, bool]:
        """Returns a mask containing the result of a > comparison for each element."""
        return (self.x > rhs.x, self.y > rhs.y, self.z > rhs.z)

    def cmple(self, rhs: 'Vec3') -> Tuple[bool, bool, bool]:
        """Returns a mask containing the result of a <= comparison for each element."""
        return (self.x <= rhs.x, self.y <= rhs.y, self.z <= rhs.z)

    def cmplt(self, rhs: 'Vec3') -> Tuple[bool, bool, bool]:
        """Returns a mask containing the result of a < comparison for each element."""
        return (self.x < rhs.x, self.y < rhs.y, self.z < rhs.z)

    def abs(self) -> 'Vec3':
        """Returns a vector containing the absolute value of each element of self."""
        return Vec3(abs(self.x), abs(self.y), abs(self.z))

    def signum(self) -> 'Vec3':
        """Returns a vector with elements representing the sign of self."""
        return Vec3(
            math.copysign(1.0, self.x),
            math.copysign(1.0, self.y),
            math.copysign(1.0, self.z)
        )

    def copysign(self, rhs: 'Vec3') -> 'Vec3':
        """Returns a vector with signs of rhs and the magnitudes of self."""
        return Vec3(
            math.copysign(self.x, rhs.x),
            math.copysign(self.y, rhs.y),
            math.copysign(self.z, rhs.z)
        )

    def is_negative_bitmask(self) -> int:
        """Returns a bitmask with the lowest 3 bits set to the sign bits from the elements."""
        return (int(self.x < 0) |
                (int(self.y < 0) << 1) |
                (int(self.z < 0) << 2))

    def is_finite(self) -> bool:
        """Returns True if all elements are finite."""
        return math.isfinite(self.x) and math.isfinite(self.y) and math.isfinite(self.z)

    def is_finite_mask(self) -> Tuple[bool, bool, bool]:
        """Performs is_finite on each element, returning a mask of the results."""
        return (math.isfinite(self.x), math.isfinite(self.y), math.isfinite(self.z))

    def is_nan(self) -> bool:
        """Returns True if any elements are NaN."""
        return math.isnan(self.x) or math.isnan(self.y) or math.isnan(self.z)

    def is_nan_mask(self) -> Tuple[bool, bool, bool]:
        """Performs is_nan on each element, returning a mask of the results."""
        return (math.isnan(self.x), math.isnan(self.y), math.isnan(self.z))

    def length(self) -> float:
        """Computes the length of self."""
        return math.sqrt(self.dot(self))

    def length_squared(self) -> float:
        """Computes the squared length of self."""
        return self.dot(self)

    def length_recip(self) -> float:
        """Computes 1.0 / length()."""
        return 1.0 / self.length()

    def distance(self, rhs: 'Vec3') -> float:
        """Computes the Euclidean distance between two points in space."""
        return (self - rhs).length()

    def distance_squared(self, rhs: 'Vec3') -> float:
        """Compute the squared euclidean distance between two points in space."""
        return (self - rhs).length_squared()

    def normalize(self) -> 'Vec3':
        """Returns self normalized to length 1.0."""
        length = self.length()
        if length == 0.0:
            raise ValueError("Cannot normalize zero vector")
        return self * (1.0 / length)

    def try_normalize(self) -> Optional['Vec3']:
        """Returns self normalized to length 1.0 if possible, else returns None."""
        length = self.length()
        if length == 0.0 or not math.isfinite(length):
            return None
        return self * (1.0 / length)

    def normalize_or(self, fallback: 'Vec3') -> 'Vec3':
        """Returns self normalized to length 1.0 if possible, else returns a fallback value."""
        normalized = self.try_normalize()
        return normalized if normalized is not None else fallback

    def normalize_or_zero(self) -> 'Vec3':
        """Returns self normalized to length 1.0 if possible, else returns zero."""
        return self.normalize_or(Vec3.ZERO)

    def normalize_and_length(self) -> Tuple['Vec3', float]:
        """Returns self normalized to length 1.0 and the length of self."""
        length = self.length()
        if length == 0.0:
            return (Vec3.X, 0.0)
        return (self * (1.0 / length), length)

    def is_normalized(self) -> bool:
        """Returns whether self is length 1.0 or not."""
        return abs(self.length_squared() - 1.0) <= 2e-4

    def project_onto(self, rhs: 'Vec3') -> 'Vec3':
        """Returns the vector projection of self onto rhs."""
        rhs_length_sq = rhs.dot(rhs)
        if rhs_length_sq == 0.0:
            raise ValueError("Cannot project onto zero vector")
        return rhs * (self.dot(rhs) / rhs_length_sq)

    def reject_from(self, rhs: 'Vec3') -> 'Vec3':
        """Returns the vector rejection of self from rhs."""
        return self - self.project_onto(rhs)

    def project_onto_normalized(self, rhs: 'Vec3') -> 'Vec3':
        """Returns the vector projection of self onto rhs. rhs must be normalized."""
        if not rhs.is_normalized():
            raise ValueError("rhs must be normalized")
        return rhs * self.dot(rhs)

    def reject_from_normalized(self, rhs: 'Vec3') -> 'Vec3':
        """Returns the vector rejection of self from rhs. rhs must be normalized."""
        return self - self.project_onto_normalized(rhs)

    def round(self) -> 'Vec3':
        """Returns a vector containing the nearest integer to a number for each element."""
        return Vec3(round(self.x), round(self.y), round(self.z))

    def floor(self) -> 'Vec3':
        """Returns a vector containing the largest integer less than or equal to a number."""
        return Vec3(math.floor(self.x), math.floor(self.y), math.floor(self.z))

    def ceil(self) -> 'Vec3':
        """Returns a vector containing the smallest integer greater than or equal to a number."""
        return Vec3(math.ceil(self.x), math.ceil(self.y), math.ceil(self.z))

    def trunc(self) -> 'Vec3':
        """Returns a vector containing the integer part each element."""
        return Vec3(math.trunc(self.x), math.trunc(self.y), math.trunc(self.z))

    def fract(self) -> 'Vec3':
        """Returns a vector containing the fractional part as self - self.trunc()."""
        return self - self.trunc()

    def fract_gl(self) -> 'Vec3':
        """Returns a vector containing the fractional part as self - self.floor()."""
        return self - self.floor()

    def exp(self) -> 'Vec3':
        """Returns a vector containing e^self for each element."""
        return Vec3(math.exp(self.x), math.exp(self.y), math.exp(self.z))

    def powf(self, n: float) -> 'Vec3':
        """Returns a vector containing each element raised to the power of n."""
        return Vec3(pow(self.x, n), pow(self.y, n), pow(self.z, n))

    def recip(self) -> 'Vec3':
        """Returns a vector containing the reciprocal 1.0/n of each element."""
        return Vec3(1.0 / self.x, 1.0 / self.y, 1.0 / self.z)

    def lerp(self, rhs: 'Vec3', s: float) -> 'Vec3':
        """Performs a linear interpolation between self and rhs based on the value s."""
        return self * (1.0 - s) + rhs * s

    def move_towards(self, rhs: 'Vec3', d: float) -> 'Vec3':
        """Moves towards rhs based on the value d."""
        a = rhs - self
        length = a.length()
        if length <= d or length <= 1e-4:
            return rhs
        return self + a * (d / length)

    def midpoint(self, rhs: 'Vec3') -> 'Vec3':
        """Calculates the midpoint between self and rhs."""
        return (self + rhs) * 0.5

    def abs_diff_eq(self, rhs: 'Vec3', max_abs_diff: float) -> bool:
        """Returns true if the absolute difference of all elements is <= max_abs_diff."""
        diff = (self - rhs).abs()
        return (diff.x <= max_abs_diff and
                diff.y <= max_abs_diff and
                diff.z <= max_abs_diff)

    def clamp_length(self, min_length: float, max_length: float) -> 'Vec3':
        """Returns a vector with a length no less than min and no more than max."""
        if min_length < 0 or max_length < 0 or min_length > max_length:
            raise ValueError("Invalid length constraints")

        length_sq = self.length_squared()
        min_sq = min_length * min_length
        max_sq = max_length * max_length

        if length_sq < min_sq:
            return self * (min_length / math.sqrt(length_sq))
        elif length_sq > max_sq:
            return self * (max_length / math.sqrt(length_sq))
        else:
            return self

    def clamp_length_max(self, max_length: float) -> 'Vec3':
        """Returns a vector with a length no more than max."""
        if max_length < 0:
            raise ValueError("max_length must be non-negative")

        length_sq = self.length_squared()
        max_sq = max_length * max_length

        if length_sq > max_sq:
            return self * (max_length / math.sqrt(length_sq))
        else:
            return self

    def clamp_length_min(self, min_length: float) -> 'Vec3':
        """Returns a vector with a length no less than min."""
        if min_length < 0:
            raise ValueError("min_length must be non-negative")

        length_sq = self.length_squared()
        min_sq = min_length * min_length

        if length_sq < min_sq:
            return self * (min_length / math.sqrt(length_sq))
        else:
            return self

    def mul_add(self, a: 'Vec3', b: 'Vec3') -> 'Vec3':
        """Fused multiply-add. Computes (self * a) + b element-wise."""
        return Vec3(
            self.x * a.x + b.x,
            self.y * a.y + b.y,
            self.z * a.z + b.z
        )

    def reflect(self, normal: 'Vec3') -> 'Vec3':
        """Returns the reflection vector for a given incident vector and surface normal."""
        if not normal.is_normalized():
            raise ValueError("normal must be normalized")
        return self - normal * (2.0 * self.dot(normal))

    def refract(self, normal: 'Vec3', eta: float) -> 'Vec3':
        """Returns the refraction direction. Returns zero vector on total internal reflection."""
        if not self.is_normalized() or not normal.is_normalized():
            raise ValueError("self and normal must be normalized")

        n_dot_i = normal.dot(self)
        k = 1.0 - eta * eta * (1.0 - n_dot_i * n_dot_i)

        if k >= 0.0:
            return self * eta - normal * (eta * n_dot_i + math.sqrt(k))
        else:
            return Vec3.ZERO

    def angle_between(self, rhs: 'Vec3') -> float:
        """Returns the angle (in radians) between two vectors in the range [0, +π]."""
        dot_product = self.dot(rhs)
        lengths_product = math.sqrt(self.length_squared() * rhs.length_squared())
        if lengths_product == 0.0:
            return 0.0
        cos_angle = dot_product / lengths_product
        # Clamp to handle floating point errors
        cos_angle = max(-1.0, min(1.0, cos_angle))
        return math.acos(cos_angle)

    def any_orthogonal_vector(self) -> 'Vec3':
        """Returns some vector that is orthogonal to the given one."""
        if abs(self.x) > abs(self.y):
            return Vec3(-self.z, 0.0, self.x)
        else:
            return Vec3(0.0, self.z, -self.y)

    def any_orthonormal_vector(self) -> 'Vec3':
        """Returns any unit vector that is orthogonal to the given one."""
        if not self.is_normalized():
            raise ValueError("self must be normalized")

        sign = math.copysign(1.0, self.z)
        a = -1.0 / (sign + self.z)
        b = self.x * self.y * a
        return Vec3(b, sign + self.y * self.y * a, -self.y)

    def any_orthonormal_pair(self) -> Tuple['Vec3', 'Vec3']:
        """Returns two other vectors that together form an orthonormal basis."""
        if not self.is_normalized():
            raise ValueError("self must be normalized")

        sign = math.copysign(1.0, self.z)
        a = -1.0 / (sign + self.z)
        b = self.x * self.y * a

        vec1 = Vec3(1.0 + sign * self.x * self.x * a, sign * b, -sign * self.x)
        vec2 = Vec3(b, sign + self.y * self.y * a, -self.y)

        return (vec1, vec2)

    # Arithmetic operators
    def __add__(self, other: Union['Vec3', float]) -> 'Vec3':
        if isinstance(other, Vec3):
            return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)
        else:
            return Vec3(self.x + other, self.y + other, self.z + other)

    def __radd__(self, other: Union['Vec3', float]) -> 'Vec3':
        return self.__add__(other)

    def __iadd__(self, other: Union['Vec3', float]) -> 'Vec3':
        if isinstance(other, Vec3):
            self.x += other.x
            self.y += other.y
            self.z += other.z
        else:
            self.x += other
            self.y += other
            self.z += other
        return self

    def __sub__(self, other: Union['Vec3', float]) -> 'Vec3':
        if isinstance(other, Vec3):
            return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)
        else:
            return Vec3(self.x - other, self.y - other, self.z - other)

    def __rsub__(self, other: Union['Vec3', float]) -> 'Vec3':
        if isinstance(other, Vec3):
            return Vec3(other.x - self.x, other.y - self.y, other.z - self.z)
        else:
            return Vec3(other - self.x, other - self.y, other - self.z)

    def __isub__(self, other: Union['Vec3', float]) -> 'Vec3':
        if isinstance(other, Vec3):
            self.x -= other.x
            self.y -= other.y
            self.z -= other.z
        else:
            self.x -= other
            self.y -= other
            self.z -= other
        return self

    def __mul__(self, other: Union['Vec3', float]) -> 'Vec3':
        if isinstance(other, Vec3):
            return Vec3(self.x * other.x, self.y * other.y, self.z * other.z)
        else:
            return Vec3(self.x * other, self.y * other, self.z * other)

    def __rmul__(self, other: Union['Vec3', float]) -> 'Vec3':
        return self.__mul__(other)

    def __imul__(self, other: Union['Vec3', float]) -> 'Vec3':
        if isinstance(other, Vec3):
            self.x *= other.x
            self.y *= other.y
            self.z *= other.z
        else:
            self.x *= other
            self.y *= other
            self.z *= other
        return self

    def __truediv__(self, other: Union['Vec3', float]) -> 'Vec3':
        if isinstance(other, Vec3):
            return Vec3(self.x / other.x, self.y / other.y, self.z / other.z)
        else:
            return Vec3(self.x / other, self.y / other, self.z / other)

    def __rtruediv__(self, other: Union['Vec3', float]) -> 'Vec3':
        if isinstance(other, Vec3):
            return Vec3(other.x / self.x, other.y / self.y, other.z / self.z)
        else:
            return Vec3(other / self.x, other / self.y, other / self.z)

    def __itruediv__(self, other: Union['Vec3', float]) -> 'Vec3':
        if isinstance(other, Vec3):
            self.x /= other.x
            self.y /= other.y
            self.z /= other.z
        else:
            self.x /= other
            self.y /= other
            self.z /= other
        return self

    def __mod__(self, other: Union['Vec3', float]) -> 'Vec3':
        if isinstance(other, Vec3):
            return Vec3(self.x % other.x, self.y % other.y, self.z % other.z)
        else:
            return Vec3(self.x % other, self.y % other, self.z % other)

    def __rmod__(self, other: Union['Vec3', float]) -> 'Vec3':
        if isinstance(other, Vec3):
            return Vec3(other.x % self.x, other.y % self.y, other.z % self.z)
        else:
            return Vec3(other % self.x, other % self.y, other % self.z)

    def __imod__(self, other: Union['Vec3', float]) -> 'Vec3':
        if isinstance(other, Vec3):
            self.x %= other.x
            self.y %= other.y
            self.z %= other.z
        else:
            self.x %= other
            self.y %= other
            self.z %= other
        return self

    def __neg__(self) -> 'Vec3':
        return Vec3(-self.x, -self.y, -self.z)

    def __pos__(self) -> 'Vec3':
        return Vec3(self.x, self.y, self.z)

    # Comparison operators
    def __eq__(self, other: 'Vec3') -> bool:
        if not isinstance(other, Vec3):
            return False
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __ne__(self, other: 'Vec3') -> bool:
        return not self.__eq__(other)

    # Indexing
    def __getitem__(self, index: int) -> float:
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        elif index == 2:
            return self.z
        else:
            raise IndexError("index out of bounds")

    def __setitem__(self, index: int, value: float) -> None:
        if index == 0:
            self.x = value
        elif index == 1:
            self.y = value
        elif index == 2:
            self.z = value
        else:
            raise IndexError("index out of bounds")

    # Iterator support
    def __iter__(self) -> Iterator[float]:
        yield self.x
        yield self.y
        yield self.z

    def __len__(self) -> int:
        return 3

    # String representation
    def __str__(self) -> str:
        return f"[{self.x}, {self.y}, {self.z}]"

    def __repr__(self) -> str:
        return f"Vec3({self.x}, {self.y}, {self.z})"

    # Type conversions
    def to_tuple(self) -> Tuple[float, float, float]:
        """Convert to tuple."""
        return (self.x, self.y, self.z)

    def to_dict(self) -> dict:
        """Convert to dict."""
        return {
            'x': self.x,
            'y': self.y,
            'z': self.z,
        }

    @classmethod
    def from_tuple(cls, t: Tuple[float, float, float]) -> 'Vec3':
        """Create from tuple."""
        return cls(t[0], t[1], t[2])

    @classmethod
    def from_dict(cls, d: dict) -> 'Vec3':
        """Create from dict."""
        return cls(d['x'], d['y'], d['z'])


# Initialize constants after class definition
Vec3.ZERO = Vec3(0.0, 0.0, 0.0)
Vec3.ONE = Vec3(1.0, 1.0, 1.0)
Vec3.NEG_ONE = Vec3(-1.0, -1.0, -1.0)
Vec3.X = Vec3(1.0, 0.0, 0.0)
Vec3.Y = Vec3(0.0, 1.0, 0.0)
Vec3.Z = Vec3(0.0, 0.0, 1.0)
Vec3.NEG_X = Vec3(-1.0, 0.0, 0.0)
Vec3.NEG_Y = Vec3(0.0, -1.0, 0.0)
Vec3.NEG_Z = Vec3(0.0, 0.0, -1.0)
Vec3.AXES = [Vec3.X, Vec3.Y, Vec3.Z]
