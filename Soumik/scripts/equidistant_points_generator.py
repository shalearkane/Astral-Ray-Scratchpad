import math
from typing import List, Tuple


def fibonacci_sphere(samples: int = 1000) -> List[Tuple[float, float]]:
    points = []
    golden_ratio = (1 + math.sqrt(5)) / 2  # Golden ratio

    for i in range(samples):
        # Calculate latitude (phi) using the angle along the z-axis
        phi = math.acos(1 - 2 * (i + 0.5) / samples)  # Latitude in radians

        # Calculate longitude (theta) based on the golden ratio
        theta = 2 * math.pi * (i / golden_ratio)  # Longitude in radians

        # Convert to degrees
        latitude = math.degrees(phi - math.pi / 2)  # Shift latitude to [-90, 90]
        longitude = math.degrees(theta % (2 * math.pi))  # Wrap longitude to [0, 360]

        points.append((latitude, longitude))

    return points


if __name__ == "__main__":
    samples = 200000  # Number of points to generate
    equidistant_points = fibonacci_sphere(samples)
    print(equidistant_points[:10])
