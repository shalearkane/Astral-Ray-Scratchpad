import csv
import json
from typing import Any, List, Dict, Tuple
import geopandas as gpd
from shapely import is_valid
from shapely.geometry import Polygon


def read_csv_to_polygons(csv_filepath: str) -> gpd.GeoDataFrame:
    """
    Reads a CSV file containing four points per row, creates an array of GeoPandas polygons.

    Args:
        csv_filepath: The path to the CSV file.

    Returns:
        A GeoDataFrame containing the polygons.
    """
    polygons: List[Polygon] = []
    mg_wts: List[float] = []
    al_wts: List[float] = []
    si_wts: List[float] = []
    fe_wts: List[float] = []

    with open(csv_filepath, "r") as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header row if it exists

        for row in reader:
            try:
                # Assuming each row contains 4 points: x1, y1, x2, y2, x3, y3, x4, y4
                # Point(longitude,latitude)
                points: List[Tuple[float, float]] = [
                    (float(row[1]), float(row[0])),
                    (float(row[3]), float(row[2])),
                    (float(row[5]), float(row[4])),
                    (float(row[7]), float(row[6])),
                ]
                polygons.append(Polygon(points))

                mg_wts.append(float(row[8]))
                al_wts.append(float(row[12]))
                si_wts.append(float(row[16]))
                fe_wts.append(float(row[18]))
            except (ValueError, IndexError) as e:
                print(f"Error reading row: {row}. Skipping. Error: {e}")
                continue

    gdf = gpd.GeoDataFrame({"mg_wt": mg_wts, "al_wt": al_wts, "si_wt": si_wts, "fe_wt": fe_wts, "geometry": polygons})
    gdf = gdf[gdf.is_valid]

    return gdf  # type: ignore


def get_area_percentage(query_polygon: Polygon, other_polygon: Polygon, query_polygon_area: float = 0) -> float:
    intersection = query_polygon.intersection(other_polygon)
    intersection_gdf = gpd.GeoDataFrame({"geometry": [intersection]})
    intersection_area = intersection_gdf["geometry"].iloc[0].area

    if query_polygon_area:
        area_percent = intersection_area / query_polygon_area
    else:
        area_percent = intersection_area / query_polygon.area

    return area_percent


def calculate_intersections(polygon_gdf: gpd.GeoDataFrame, doc: Dict[str, Any]) -> None:
    """
    Reads an array of JSON objects each containing four points, and calculates which of the polygons in the GeoDataFrame
    intersect with it, then prints the result.

    Args:
        polygon_gdf: The GeoDataFrame containing the polygons.
        json_data: A list of dictionaries, where each dictionary contains 'points' as a list of [x1, y1, x2, y2, x3, y3, x4, y4].
    """

    points: List[Tuple[float, float]] = [
        (doc["v0lon"], doc["v0lat"]),
        (doc["v1lon"], doc["v1lat"]),
        (doc["v2lon"], doc["v2lat"]),
        (doc["v3lon"], doc["v3lat"]),
    ]
    query_polygon: Polygon = Polygon(points)
    if not query_polygon.is_valid:
        return

    query_polygon_area = query_polygon.area

    intersecting_polygons = polygon_gdf[polygon_gdf.intersects(query_polygon)]

    avg_mg_wt: float = 0
    avg_al_wt: float = 0
    avg_si_wt: float = 0
    avg_fe_wt: float = 0
    total_area_percent: float = 0
    if not intersecting_polygons.empty:
        for _, polygon in intersecting_polygons.iterrows():
            area_percent = get_area_percentage(query_polygon, polygon["geometry"], query_polygon_area)

            avg_mg_wt += area_percent * polygon["mg_wt"]
            avg_al_wt += area_percent * polygon["al_wt"]
            avg_si_wt += area_percent * polygon["si_wt"]
            avg_fe_wt += area_percent * polygon["fe_wt"]

            total_area_percent += area_percent

    else:
        print(f"JSON record with points {points} does not intersect with any polygons.")


# Example Usage
if __name__ == "__main__":
    csv_file = (
        "/home/sm/Public/Inter-IIT/Astral-Ray-Scratchpad/Soumik/data/isro/elemental_abundances_by_isro.csv"  # Replace with your CSV file path
    )
    json_file = "/home/sm/Public/Inter-IIT/Astral-Ray-Scratchpad/Soumik/data-generated/script_inputs/ISRO.test_fits.json"  # Replace with your JSON file path

    polygon_geodataframe = read_csv_to_polygons(csv_file)
    # print(polygon_geodataframe.head())

    # exit()

    with open(json_file, "r") as f:
        json_data_list: List[Dict[str, Any]] = json.load(f)
        for data in json_data_list:
            calculate_intersections(polygon_geodataframe, data)
