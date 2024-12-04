from constants.mongo import COLLECTION_CLASS_FITS
from constants.output_dirs import OUTPUT_DIR_CLASS_FITS, TO_PROCESS_FILE_INDEXES
from helpers.download import download_file_from_file_server
from helpers.query_class import get_class_fits_for_flare_class
import os


def download_flare_classes(flare_class: str = "X", minimum_flare_scale: float = 0.0) -> list[str]:
    os.makedirs(OUTPUT_DIR_CLASS_FITS, exist_ok=True)
    class_fits = get_class_fits_for_flare_class(flare_class, minimum_flare_scale)

    file_paths: list[str] = list()

    for fits_file in class_fits:
        if download_file_from_file_server(fits_file, COLLECTION_CLASS_FITS, OUTPUT_DIR_CLASS_FITS):
            file_paths.append(os.path.join(OUTPUT_DIR_CLASS_FITS, fits_file["path"].split("/")[-1]))

    return file_paths


if __name__ == "__main__":
    flare_class = "X"
    minimum_flare_scale = 0.0
    os.makedirs(TO_PROCESS_FILE_INDEXES, exist_ok=True)
    file_paths = download_flare_classes(flare_class, minimum_flare_scale)

    with open(os.path.join(TO_PROCESS_FILE_INDEXES, f"flare-class-{flare_class}-{minimum_flare_scale}.csv"), "w") as f:
        for file_path in file_paths:
            f.write(f"{file_path}\n")
