from helpers.query import get_class_fits_at_lat_lon
from helpers.download import download_file_from_file_server
from constants.class_fits import (
    V0_LAT,
    V0_LON,
    V1_LAT,
    V1_LON,
    V2_LAT,
    V2_LON,
    V3_LAT,
    V3_LON,
)
from typing import List, Tuple


if __name__ == "__main__":
    list_of_docs = get_class_fits_at_lat_lon(20, 130)
    list_of_land_patches: List[List[Tuple[float, float]]] = list()
    for doc in list_of_docs:
        download_file_from_file_server(doc, "primary", "data/class")

        list_of_land_patches.append(
            [
                (doc[V0_LAT], doc[V0_LON]),
                (doc[V1_LAT], doc[V1_LON]),
                (doc[V2_LAT], doc[V2_LON]),
                (doc[V3_LAT], doc[V3_LON]),
            ]
        )

    # plot_quadrilaterals(list_of_land_patches, None, 0.05)
