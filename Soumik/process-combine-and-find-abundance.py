from datetime import datetime
from itertools import batched
from typing import Dict, Final, List, Set, Tuple
from csv import DictReader

import concurrent.futures

from model.model_handcrafted import process_abundance_h
from constants.misc import STATISTICS_COMM_PIPE
from criterion.photon_count import photon_count_from_hdul
from criterion.geotail import is_not_during_geotail
from scripts.equidistant_points_generator import fibonacci_sphere
from constants.output_dirs import OUTPUT_DIR_CLASS_FITS, OUTPUT_DIR_FIBONACCI_FITS, OUTPUT_DIR_TRUTH_FITS
from constants.mongo import COLLECTION_CLASS_FITS
from helpers.download import download_file_from_file_server
from helpers.combine_fits_mod import combine_fits
from helpers.query_class import get_class_fits_at_lat_lon
from os.path import isfile
from astropy.io import fits
from astropy.table import Table


increment: Final[float] = 0.1

latitude_start: Final[float] = 30
latitude_end: Final[float] = 50

longitude_start: Final[float] = 80
longitude_end: Final[float] = 100


def get_stuff_from_fits_header(hdul_file_path: str) -> Dict[str, float | int]:
    # solarang, emission_angle, photon_count

    with fits.open(hdul_file_path) as hdul:
        photon_count = photon_count_from_hdul(hdul)

        table = Table.read(hdul["SPECTRUM"])
        solar_zenith_angle = float(table.meta["SOLARANG"])
        emission_angle = float(table.meta["EMISNANG"])
        altitude = float(table.meta["SAT_ALT"])
        exposure = float(table.meta["EXPOSURE"])

        al_peak_height = float(table.meta.get("PEAKH_AL",0))
        al_peak_count = int(table.meta.get("PEAKC_AL",-1))
        mg_peak_height = float(table.meta.get("PEAKH_MG",0))
        mg_peak_count = int(table.meta.get("PEAKC_MG"),-1)
        si_peak_height = float(table.meta.get("PEAKH_SI",0))
        si_peak_count = int(table.meta.get("PEAKC_SI"),-1)
        ca_peak_height = float(table.meta.get("PEAKH_MG",0))
        ca_peak_count = int(table.meta.get("PEAKC_MG"),-1)

        mid_utc = datetime.strptime(table.meta["MID_UTC"], "%Y-%m-%dT%H:%M:%S.%f").timestamp()

        return 


# latitude,longitude,al,mg,si,fe
def generate_combined_fits_for_lat_lon(
    latitude: float, longitude: float, true_mg: float, true_al: float, true_si: float, true_fe: float, redo: bool
) -> bool:
    combined_fits_path = f"{OUTPUT_DIR_FIBONACCI_FITS}/{latitude:.3f}_{longitude:.3f}.fits"
    if not redo and isfile(combined_fits_path):
        print(f"already generated: {combined_fits_path}")
        return True

    docs = get_class_fits_at_lat_lon(latitude, longitude)

    visible_element_peaks: Set[str] = set()

    for doc in docs:
        for key in doc["visible_peaks"].keys():
            visible_element_peaks.add(key)

    print(visible_element_peaks)

    file_paths: List[str] = list()

    for doc in docs:
        if download_file_from_file_server(doc, COLLECTION_CLASS_FITS, OUTPUT_DIR_CLASS_FITS):
            file_paths.append(f"{OUTPUT_DIR_CLASS_FITS}/{doc["path"].split("/")[-1]}")

    metadata = {"latitude": latitude, "longitude": longitude, "visible_peaks": visible_element_peaks}
    if combine_fits(file_paths, combined_fits_path, metadata, method):
        print(f"generated: {combined_fits_path}")
        dict = process_abundance_h(combined_fits_path)
        wt_dict = dict["wt"]
        wt_mg = wt_dict["Wt_Mg"]
        wt_al = wt_dict["Wt_Al"]
        wt_si = wt_dict["Wt_Si"]
        wt_ca = wt_dict["Wt_Ca"]
        wt_fe = wt_dict["Wt_Fe"]

        stuff = get_stuff_from_fits_header(combined_fits_path)

        with open(STATISTICS_COMM_PIPE, "w") as pipe:
            pipe.write(f"{latitude},{longitude},{wt_mg},{wt_al},{wt_si},{wt_ca},{wt_fe},{true_mg},{true_al},{true_si},{true_fe}\n")

        return True
    else:
        print(f"could not generate: {combined_fits_path}")
        return False


def do_in_parallel(lat_lon_dicts: List[Dict[str, float]]):
    count = 0

    with concurrent.futures.ProcessPoolExecutor() as executor:
        for lat_lon_dict_batch in batched(lat_lon_dicts, 32):
            future_to_doc = {
                executor.submit(
                    generate_combined_fits_for_lat_lon, lld["lat"], lld["lon"], lld["mg"], lld["al"], lld["si"], lld["fe"], True
                ): lld
                for lld in lat_lon_dict_batch
            }
            concurrent.futures.wait(future_to_doc, timeout=None, return_when=concurrent.futures.ALL_COMPLETED)

            count += 32
            print(count)


def read_lat_lon_file(csv_file_path: str) -> List[Tuple[float, float]]:
    coordinates: List[Tuple[float, float]] = list()

    with open(csv_file_path, mode="r") as file:
        reader = DictReader(file, ["latitude", "longitude"])
        for row in reader:
            # Convert latitude and longitude to float and add as a tuple
            coordinates.append((float(row["latitude"]), float(row["longitude"])))

    return coordinates


if __name__ == "__main__":
    # lat_lon_pairs: List[Tuple[float, float]] = fibonacci_sphere(400000)

    # lat_lon_pairs = lat_lon_pairs[:40000]  # get only 10% of data

    # latitude = latitude_start
    # while latitude < latitude_end:
    #     latitude += increment

    #     longitude = longitude_start
    #     while longitude < longitude_end:
    #         longitude += increment

    #         lat_lon_pairs.append((latitude, longitude))

    lat_lon_pairs = read_lat_lon_file("data-generated/script_inputs/fibonacci-points.csv")

    # do_in_parallel(lat_lon_pairs)

    for method in ["average", "rms", "weighted_average"]:
        generate_combined_fits_for_lat_lon(16.10, -39.09, 1, 2, 3, 4, True)
