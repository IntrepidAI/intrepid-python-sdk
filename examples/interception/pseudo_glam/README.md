# Python port of glam-rs

AI-generated port of `Vec3` and `Quat` from `glam-rs`.

## Vec3

### Basic Usage

```python
from vec3 import Vec3, vec3

# Create vectors
v1 = Vec3(1.0, 2.0, 3.0)
v2 = vec3(4.0, 5.0, 6.0)

# Basic arithmetic
result = v1 + v2          # [5.0, 7.0, 9.0]
result = v1 - v2          # [-3.0, -3.0, -3.0]
result = v1 * 2.0         # [2.0, 4.0, 6.0]
result = v1 / 2.0         # [0.5, 1.0, 1.5]

# Vector operations
dot_product = v1.dot(v2)          # 32.0
cross_product = v1.cross(v2)     # [-3.0, 6.0, -3.0]
length = v1.length()              # 3.74165...
normalized = v1.normalize()       # Unit vector
```

### Vec3 Constants

```python
from vec3 import Vec3

# Predefined constants
zero = Vec3.ZERO      # [0.0, 0.0, 0.0]
one = Vec3.ONE        # [1.0, 1.0, 1.0]
x_axis = Vec3.X       # [1.0, 0.0, 0.0]
y_axis = Vec3.Y       # [0.0, 1.0, 0.0]
z_axis = Vec3.Z       # [0.0, 0.0, 1.0]
axes = Vec3.AXES      # [X, Y, Z]
```

### Vector Math Operations

```python
# Length operations
length = v1.length()              # Vector magnitude
length_sq = v1.length_squared()   # Magnitude squared (faster)
normalized = v1.normalize()       # Unit vector
is_unit = v1.is_normalized()      # Check if unit vector

# Distance operations
distance = v1.distance(v2)        # Euclidean distance
dist_sq = v1.distance_squared(v2) # Distance squared

# Geometric operations
projected = v1.project_onto(v2)   # Vector projection
rejected = v1.reject_from(v2)     # Vector rejection
reflected = v1.reflect(normal)    # Reflection
angle = v1.angle_between(v2)      # Angle in radians

# Interpolation
lerped = v1.lerp(v2, 0.5)         # Linear interpolation
midpoint = v1.midpoint(v2)        # Halfway point
```

### Utility Operations

```python
# Element-wise operations
minimum = v1.min(v2)              # Component-wise minimum
maximum = v1.max(v2)              # Component-wise maximum
clamped = v1.clamp(min_vec, max_vec)  # Component-wise clamp

# Reduction operations
min_elem = v1.min_element()       # Smallest component
max_elem = v1.max_element()       # Largest component
sum_elem = v1.element_sum()       # Sum of components
product = v1.element_product()    # Product of components

# Math functions
absolute = v1.abs()               # Absolute values
floored = v1.floor()              # Floor each component
ceiled = v1.ceil()                # Ceil each component
rounded = v1.round()              # Round each component
```

## Quat

### Basic Usage

```python
from quat import Quat, quat, EulerRot
from vec3 import Vec3
import math

# Create quaternions
q1 = Quat.IDENTITY                    # Identity quaternion
q2 = quat(0.0, 0.0, 0.707, 0.707)   # Convenience function
q3 = Quat(0.0, 0.0, 0.707, 0.707)   # Direct construction

# Basic arithmetic
result = q1 + q2          # Addition (not common for rotations)
result = q1 * q2          # Quaternion multiplication (rotation composition)
result = q2 * 2.0         # Scalar multiplication
result = q2 / 2.0         # Scalar division
```

### Constants

```python
from quat import Quat

# Predefined constants
identity = Quat.IDENTITY  # [0, 0, 0, 1] - no rotation
zero = Quat.ZERO          # [0, 0, 0, 0] - invalid quaternion
nan_quat = Quat.NAN       # [NaN, NaN, NaN, NaN] - invalid quaternion
```

### Creating Rotations

#### From Axis and Angle

```python
import math
from vec3 import Vec3

# Create rotation around Y-axis by 90 degrees
axis = Vec3(0.0, 1.0, 0.0)  # Y-axis (must be normalized)
angle = math.pi / 2         # 90 degrees in radians
q = Quat.from_axis_angle(axis, angle)

# From scaled axis (length = angle in radians)
scaled_axis = Vec3(0.0, math.pi/2, 0.0)  # 90° around Y
q = Quat.from_scaled_axis(scaled_axis)
```

#### Single Axis Rotations

```python
# Rotations around coordinate axes
qx = Quat.from_rotation_x(math.pi / 2)  # 90° around X
qy = Quat.from_rotation_y(math.pi / 2)  # 90° around Y
qz = Quat.from_rotation_z(math.pi / 2)  # 90° around Z
```

#### From Euler Angles

```python
from quat import EulerRot

# Create from Euler angles (in radians)
roll = math.pi / 6   # 30°
pitch = math.pi / 4  # 45°
yaw = math.pi / 3    # 60°

q_xyz = Quat.from_euler(EulerRot.XYZ, roll, pitch, yaw)
q_zyx = Quat.from_euler(EulerRot.ZYX, yaw, pitch, roll)

# Available rotation orders
# EulerRot.XYZ, EulerRot.XZY, EulerRot.YXZ,
# EulerRot.YZX, EulerRot.ZXY, EulerRot.ZYX
```

#### From Vector to Vector

```python
# Create rotation that transforms one vector to another
from_vec = Vec3(1.0, 0.0, 0.0)  # X-axis
to_vec = Vec3(0.0, 1.0, 0.0)    # Y-axis

q = Quat.from_rotation_arc(from_vec, to_vec)

# Verify the rotation
rotated = q * from_vec  # Should be close to to_vec
```

#### Look-At Rotations

```python
# Camera-style rotations
eye = Vec3(0.0, 0.0, 0.0)       # Camera position
target = Vec3(1.0, 0.0, 0.0)    # Look target
up = Vec3(0.0, 1.0, 0.0)        # Up direction

# Right-handed coordinate system
q_rh = Quat.look_at_rh(eye, target, up)

# Left-handed coordinate system
q_lh = Quat.look_at_lh(eye, target, up)

# Or with direction vector
direction = (target - eye).normalize()
q_look_rh = Quat.look_to_rh(direction, up)
```

### Converting Quaternions Back

#### To Axis-Angle

```python
q = Quat.from_rotation_y(math.pi / 3)  # 60° around Y

# Get axis and angle
axis, angle = q.to_axis_angle()
print(f"Axis: {axis}, Angle: {math.degrees(angle)}°")

# Get scaled axis (axis * angle)
scaled_axis = q.to_scaled_axis()
```

#### To Euler Angles

```python
q = Quat.from_euler(EulerRot.XYZ, 0.1, 0.2, 0.3)

# Convert back (limited implementation)
try:
    angles = q.to_euler(EulerRot.XYZ)
    roll, pitch, yaw = angles
except NotImplementedError:
    print("Euler conversion not implemented for this order")
```

### Quaternion Operations

#### Basic Properties

```python
q = Quat.from_rotation_z(math.pi / 4)

# Length operations
length = q.length()              # Should be 1.0 for rotations
length_sq = q.length_squared()   # Faster than length()
is_unit = q.is_normalized()      # Check if unit quaternion

# Normalization
q_norm = q.normalize()           # Ensure unit length
```

#### Mathematical Operations

```python
q1 = Quat.from_rotation_x(math.pi / 4)
q2 = Quat.from_rotation_y(math.pi / 4)

# Dot product (cosine of half the angle between rotations)
dot_product = q1.dot(q2)

# Angle between quaternions
angle = q1.angle_between(q2)
print(f"Angle: {math.degrees(angle)}°")

# Conjugate (inverse for unit quaternions)
q_conj = q1.conjugate()
q_inv = q1.inverse()  # Same as conjugate for unit quaternions

# Quaternion multiplication (rotation composition)
combined = q2 * q1  # Apply q1 first, then q2
```

#### Vector Rotation

```python
# Rotate vectors with quaternions
vec = Vec3(1.0, 0.0, 0.0)
q = Quat.from_rotation_z(math.pi / 2)  # 90° around Z

rotated_vec = q * vec  # vec rotated by q
# Should be approximately Vec3(0, 1, 0)
```

### Quaternion Interpolation

#### Linear Interpolation (LERP)

```python
q1 = Quat.IDENTITY
q2 = Quat.from_rotation_z(math.pi / 2)

# Linear interpolation (faster but less smooth)
q_half = q1.lerp(q2, 0.5)  # Halfway between
```

### Spherical Linear Interpolation (SLERP)

```python
# Spherical interpolation (smoother for rotations)
q_half = q1.slerp(q2, 0.5)  # Halfway between

# Animation example
for t in [0.0, 0.25, 0.5, 0.75, 1.0]:
    q_t = q1.slerp(q2, t)
    # Use q_t for animation frame
```

#### Controlled Rotation

```python
# Rotate towards a target by a maximum angle
max_angle = math.pi / 4  # 45° maximum per step
q_step = q1.rotate_towards(q2, max_angle)
```

## Testing

```bash
python test_vec3.py    # Vec3 tests
python test_quat.py    # Quat tests
```
