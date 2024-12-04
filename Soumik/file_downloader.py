from Soumik.constants.mongo import COLLECTION_CLASS_FITS
from helpers.download import download_file_from_file_server


download_file_from_file_server(
        {
            "_id": "672ebe78a0c52a0831ae4d54",
            "path": "../files/cla/data/calibrated/2024/07/31/ch2_cla_l1_20240731T131549098_20240731T131557098.fits",
        },
        COLLECTION_CLASS_FITS,
        ".",
    )
