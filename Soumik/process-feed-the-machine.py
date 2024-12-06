from itertools import batched
from typing import Any, Dict, Final, List, Set, Tuple
from csv import DictReader

import concurrent.futures

from helpers.combine_fits_with_metadata import combine_fits_with_meta, hdul_meta_to_dict
from model.model_handcrafted import process_abundance_h
from constants.misc import STATISTICS_COMM_PIPE
from constants.output_dirs import OUTPUT_DIR_CLASS_FITS, OUTPUT_DIR_FIBONACCI_FITS
from constants.mongo import COLLECTION_CLASS_FITS, COLLECTION_DATA_COLLECTION, DATABASE_ISRO, MONGO_URI
from helpers.download import download_file_from_file_server
from helpers.query_class import get_class_fits_at_lat_lon
from os.path import isfile
from pymongo import MongoClient

increment: Final[float] = 0.1

latitude_start: Final[float] = 30
latitude_end: Final[float] = 50

longitude_start: Final[float] = 80
longitude_end: Final[float] = 100


def save_to_mongo(filepath: str, doc: Dict[str, Any]):
    data_collection = MongoClient(MONGO_URI)[DATABASE_ISRO][COLLECTION_DATA_COLLECTION]
    data_collection.find_one_and_update({"filepath": filepath}, {"$set": doc})


def generate_combined_fits_for_lat_lon(latitude: float, longitude: float, redo: bool) -> bool:
    combined_fits_filename = f"{latitude:.2f}_{longitude:.2f}.fits"
    combined_fits_path = f"{OUTPUT_DIR_FIBONACCI_FITS}/{combined_fits_filename}"
    if not redo and isfile(combined_fits_path):
        print(f"already generated: {combined_fits_path}")
        return True

    docs = get_class_fits_at_lat_lon(latitude, longitude)

    visible_element_peaks: Set[str] = set()

    for doc in docs:
        for key in doc["visible_peaks"].keys():
            visible_element_peaks.add(key)

    file_paths: List[str] = list()
    doc_list: List[Dict[str, Any]] = list()

    for doc in docs:
        if download_file_from_file_server(doc, COLLECTION_CLASS_FITS, OUTPUT_DIR_CLASS_FITS):
            file_paths.append(f"{OUTPUT_DIR_CLASS_FITS}/{doc["path"].split("/")[-1]}")
            doc_list.append(doc)

    metadata = {"latitude": latitude, "longitude": longitude, "visible_peaks": visible_element_peaks}
    success, computed_metadata = combine_fits_with_meta(file_paths, doc_list, combined_fits_path, metadata)
    if success:
        print(f"generated: {combined_fits_path}")
        abundance_dict = process_abundance_h(combined_fits_path)
        print(abundance_dict)
        wt_na = abundance_dict["wt"].get("Wt_Na", -1)
        wt_mg = abundance_dict["wt"].get("Wt_Mg", -1)
        wt_al = abundance_dict["wt"].get("Wt_Al", -1)
        wt_si = abundance_dict["wt"].get("Wt_Si", -1)
        wt_ca = abundance_dict["wt"].get("Wt_Ca", -1)
        wt_ti = abundance_dict["wt"].get("Wt_Ti", -1)
        wt_fe = abundance_dict["wt"].get("Wt_Fe", -1)

        mongo_doc: Dict[str, Any] = {
            "wt": {
                "na": wt_na,
                "mg": wt_mg,
                "al": wt_al,
                "si": wt_si,
                "ca": wt_ca,
                "fe": wt_fe,
                "ti": wt_ti,
            },
            "photon_count": int(computed_metadata.photon_counts.sum()),
            "computed_metadata": hdul_meta_to_dict(computed_metadata),
        }

        save_to_mongo(combined_fits_filename, mongo_doc)

        # with open(STATISTICS_COMM_PIPE, "w") as pipe:
        #     pipe.write(
        #         (
        #             f"{latitude:.3f},{longitude:.3f},"
        #             f"{wt_mg:.2f},{wt_al:.2f},{wt_si:.2f},{wt_ca:.2f},{wt_fe:.2f},"
        #             f"{int(computed_metadata.photon_counts.sum())},{computed_metadata.solar_zenith_angle:.2f},{computed_metadata.altitude:.2f},{computed_metadata.exposure:.2f},{computed_metadata.mid_utc},"
        #             f"{computed_metadata.peak_na_c},{computed_metadata.peak_na_h:.2f},"
        #             f"{computed_metadata.peak_mg_c},{computed_metadata.peak_mg_h:.2f},"
        #             f"{computed_metadata.peak_al_c},{computed_metadata.peak_al_h:.2f},"
        #             f"{computed_metadata.peak_si_c},{computed_metadata.peak_si_h:.2f},"
        #             f"{computed_metadata.peak_ca_c},{computed_metadata.peak_ca_h:.2f},"
        #             f"{computed_metadata.peak_ti_c},{computed_metadata.peak_ti_h:.2f},"
        #             f"{computed_metadata.peak_fe_c},{computed_metadata.peak_fe_h:.2f}"
        #             f"\n"
        #         )
        #     )

        return True
    else:
        print(f"could not generate: {combined_fits_path}")
        return False


def do_in_parallel(lat_lon_dicts: List[Tuple[float, float]]):
    count = 0

    with concurrent.futures.ProcessPoolExecutor() as executor:
        for lat_lon_dict_batch in batched(lat_lon_dicts, 32):
            future_to_doc = {
                executor.submit(generate_combined_fits_for_lat_lon, lat, lon, False): (lat, lon) for (lat, lon) in lat_lon_dict_batch
            }
            concurrent.futures.wait(future_to_doc, timeout=None, return_when=concurrent.futures.ALL_COMPLETED)

            count += 32
            print(count)


def read_lat_lon_file(csv_file_path: str) -> List[Tuple[float, float]]:
    coordinates: List[Tuple[float, float]] = list()

    with open(csv_file_path, mode="r") as file:
        reader = DictReader(file, ["latitude", "longitude", "al", "mg", "si", "fe"])
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

    lat_lon_pairs = read_lat_lon_file("scripts/points-mini.csv")
    do_in_parallel(lat_lon_pairs)

    # for method in ["average", "rms", "weighted_average"]:
    #     generate_combined_fits_for_lat_lon(16.10, -39.09, 1, 2, 3, 4, True)
