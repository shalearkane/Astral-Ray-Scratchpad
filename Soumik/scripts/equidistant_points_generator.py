import matplotlib
import pymongo
import math
import datetime
from typing import List, Tuple, Dict, Any
from pymongo.errors import BulkWriteError, ConnectionFailure
import matplotlib.pyplot as plt

matplotlib.use("Agg")

# Number of points to generate
NUM_POINTS: int = 262144


def fibonacci_sphere(samples: int) -> List[Tuple[str, str]]:
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

        if abs(latitude) > 85 or longitude > 355 or longitude < 5:
            continue

        longitude -= 180

        points.append((f"{latitude:.2f}", f"{longitude:.2f}"))
        # points.append((latitude, longitude))

    return points


def main() -> None:
    """Generates points, formats them, and stores them in MongoDB."""
    try:
        # Connect to MongoDB
        collection = pymongo.MongoClient("mongodb://192.168.156.59:27017")["ISRO"]["fibnacci_lat_lon_v2"]

        # Create unique compound index on latitude and longitude
        collection.create_index([("latitude", pymongo.ASCENDING), ("longitude", pymongo.ASCENDING)], unique=True)

        points_data: List[Dict[str, Any]] = []
        points_lat_lon: List[Tuple[str, str]] = fibonacci_sphere(NUM_POINTS)
        for latitude, longitude in points_lat_lon:
            point_data: Dict[str, Any] = {
                "latitude": latitude,
                "longitude": longitude,
                "status": False,
                "last_served": datetime.datetime(1970, 1, 1),
            }
            points_data.append(point_data)

        try:
            collection.insert_many(points_data, ordered=False)
            print(f"{len(points_data)} points generated and stored successfully.")
        except BulkWriteError as bwe:
            print(f"Bulk write error occurred: {bwe}")
            successful_inserts: int = bwe.details.get("nInserted", 0)
            print(f"Number of documents successfully inserted: {successful_inserts}")
            print("Duplicate key errors likely occurred for the remaining points.")

    except ConnectionFailure as e:
        print(f"Could not connect to MongoDB: {e}")


if __name__ == "__main__":
    main()

    # samples = 100  # Number of points to generate
    # equidistant_points = fibonacci_sphere(samples)
    # print(equidistant_points[:10])

    # latitudes = [point[0] for point in equidistant_points]
    # longitudes = [point[1] for point in equidistant_points]

    # # Plot the points on a 2D map
    # plt.figure(figsize=(10, 6))
    # plt.scatter(longitudes, latitudes, s=1, color="blue")  # Small dots for each point
    # plt.title("Equidistant Points on the Sphere (Fibonacci Lattice)", fontsize=14)
    # plt.xlabel("Longitude (°)", fontsize=12)
    # plt.ylabel("Latitude (°)", fontsize=12)
    # plt.grid(True)
    # plt.savefig("some1.png")
