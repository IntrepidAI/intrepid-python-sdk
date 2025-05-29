from intrepid_python_sdk.simulator import Simulator, ObstacleType, Position, Rotation
import random
import math

hvt_position = Position(10, 8, 0)
attacker_id = 99
distance_from_hvt = 20


def generate_random_position_around_xy(base_position, offset_range=10):
    dx = random.uniform(-offset_range, offset_range)
    dy = random.uniform(-offset_range, offset_range)
    new_pos = Position(
        base_position.x + dx,
        base_position.y + dy,
        base_position.z  # z stays the same
    )
    return new_pos


def intersect_sphere_line(sphere_center, radius, line_point, line_dir):
    cx, cy, cz = sphere_center
    px, py, pz = line_point
    dx, dy, dz = line_dir

    # Vector from line point to sphere center
    ox, oy, oz = px - cx, py - cy, pz - cz

    # Coefficients for quadratic equation at^2 + bt + c = 0
    a = dx**2 + dy**2 + dz**2
    b = 2 * (ox * dx + oy * dy + oz * dz)
    c = ox**2 + oy**2 + oz**2 - radius**2

    # Discriminant
    discriminant = b**2 - 4 * a * c

    if discriminant < 0:
        return []  # No intersection
    elif discriminant == 0:
        t = -b / (2 * a)
        return [(px + t * dx, py + t * dy, pz + t * dz)]  # Tangent point
    else:
        sqrt_d = math.sqrt(discriminant)
        t1 = (-b - sqrt_d) / (2 * a)
        t2 = (-b + sqrt_d) / (2 * a)
        point1 = (px + t1 * dx, py + t1 * dy, pz + t1 * dz)
        point2 = (px + t2 * dx, py + t2 * dy, pz + t2 * dz)
        return [point1, point2]  # Two intersection points
