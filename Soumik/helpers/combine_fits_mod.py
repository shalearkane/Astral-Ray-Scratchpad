import numpy as np
import os
import math
from astropy.io import fits
from typing import List, Tuple, Final
from astropy.table import Table
from datetime import datetime
from helpers.utilities import set_default_values_to_class_fits
from criterion.photon_count import photon_count_from_hdul

CHANNELS: Final[int] = 2048


def deg_to_rad(degrees: float) -> float:
    return (degrees * math.pi) / 180.0


def rad_to_deg(radians: float) -> float:
    return (radians * 180.0) / math.pi


def process_hdul(hdul, method: str) -> Tuple[np.ndarray, float, float, float, float, float]:
    data = hdul["SPECTRUM"].data
    photon_counts = data["COUNTS"]
    table = Table.read(hdul["SPECTRUM"])
    solar_zenith_angle = float(table.meta["SOLARANG"])
    emission_angle = float(table.meta["EMISNANG"])
    altitude = float(table.meta["SAT_ALT"])
    exposure = float(table.meta["EXPOSURE"])
    mid_utc = datetime.strptime(table.meta["MID_UTC"], "%Y-%m-%dT%H:%M:%S.%f").timestamp()

    solar_zenith = 1.0 / math.sin(deg_to_rad(solar_zenith_angle))
    emission = 1.0 / math.sin(deg_to_rad(emission_angle))

    if method == "average":
        return photon_counts, solar_zenith, emission, altitude, exposure, mid_utc

    elif method == "rms":
        return photon_counts**2, solar_zenith**2, emission**2, altitude**2, exposure**2, mid_utc

    elif method == "weighted_average":
        weight = photon_count_from_hdul(hdul)
        return photon_counts * weight, solar_zenith * weight, emission * weight, altitude * weight, exposure * weight, mid_utc

    else:
        raise ValueError(f"Unknown method: {method}")


def calculate_aggregate(
    files_used: int,
    photon_counts_sum: np.ndarray,
    solar_zenith_angles_cosec_sum: float,
    emission_angles_cosec_sum: float,
    altitude_sum: float,
    exposure_sum: float,
    mid_utc_in_seconds_sum: float,
    weights_sum: float,
    method: str,
) -> Tuple[np.ndarray, float, float, float, float, float]:
    if method == "average":
        photon_counts_avg = photon_counts_sum / files_used
        solar_zenith_angles_cosec_avg = solar_zenith_angles_cosec_sum / files_used
        emission_angles_cosec_avg = emission_angles_cosec_sum / files_used
        altitude_avg = altitude_sum / files_used
        exposure_avg = exposure_sum / files_used

    elif method == "rms":
        photon_counts_avg = np.sqrt(photon_counts_sum / files_used)
        solar_zenith_angles_cosec_avg = math.sqrt(solar_zenith_angles_cosec_sum / files_used)
        emission_angles_cosec_avg = math.sqrt(emission_angles_cosec_sum / files_used)
        altitude_avg = math.sqrt(altitude_sum / files_used)
        exposure_avg = math.sqrt(exposure_sum / files_used)

    elif method == "weighted_average":
        photon_counts_avg = photon_counts_sum / weights_sum
        solar_zenith_angles_cosec_avg = solar_zenith_angles_cosec_sum / weights_sum
        emission_angles_cosec_avg = emission_angles_cosec_sum / weights_sum
        altitude_avg = altitude_sum / weights_sum
        exposure_avg = exposure_sum / weights_sum

    else:
        raise ValueError(f"Unknown ideology: {method}")

    solar_zenith_angle = rad_to_deg(math.asin(1.0 / solar_zenith_angles_cosec_avg))
    emission_angle = rad_to_deg(math.asin(1.0 / emission_angles_cosec_avg))
    mid_utc_in_seconds_avg = mid_utc_in_seconds_sum / files_used

    return photon_counts_avg, solar_zenith_angle, emission_angle, altitude_avg, exposure_avg, mid_utc_in_seconds_avg


def combine_fits(fits_files: List[str], output_fits_path: str, metadata: dict, minimum_photon_count: int = 3000, method: str = "rms") -> bool:
    try:
        if len(fits_files) == 0:
            return False

        photon_counts_sum = np.zeros(CHANNELS, dtype=np.float64)
        solar_zenith_angles_cosec_sum = 0
        emission_angles_cosec_sum = 0
        altitude_sum = 0
        exposure_sum = 0
        mid_utc_in_seconds_sum = 0
        weights_sum = 0
        files_used = 0

        for file_path in fits_files:
            with fits.open(file_path) as hdul:
                if photon_count_from_hdul(hdul) < minimum_photon_count:
                    continue

                files_used += 1
                photon_counts, solar_zenith, emission, altitude, exposure, mid_utc = process_hdul(hdul, method)

                photon_counts_sum += photon_counts
                solar_zenith_angles_cosec_sum += solar_zenith
                emission_angles_cosec_sum += emission
                altitude_sum += altitude
                exposure_sum += exposure
                mid_utc_in_seconds_sum += mid_utc

                if method == "weighted_average":
                    weights_sum += photon_count_from_hdul(hdul)

        if files_used == 0:
            return False

        photon_counts, solar_zenith_angle, emission_angle, altitude_avg, exposure_avg, mid_utc_in_seconds_avg = calculate_aggregate(
            files_used,
            photon_counts_sum,
            solar_zenith_angles_cosec_sum,
            emission_angles_cosec_sum,
            altitude_sum,
            exposure_sum,
            mid_utc_in_seconds_sum,
            weights_sum,
            method,
        )

        mid_utc = datetime.fromtimestamp(mid_utc_in_seconds_avg).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]

        hdu = fits.BinTableHDU.from_columns(
            [
                fits.Column(name="CHANNEL", format="1I", array=np.arange(CHANNELS)),
                fits.Column(name="COUNTS", format="1D", array=photon_counts),
            ]
        )

        hdu.header["SOLARANG"] = solar_zenith_angle
        hdu.header["EMISNANG"] = emission_angle
        hdu.header["MID_UTC"] = mid_utc
        hdu.header["SAT_ALT"] = altitude_avg
        hdu.header["EXPOSURE"] = exposure_avg

        # custom header
        hdu.header["FILE_CNT"] = files_used
        hdu.header["TARG_LAT"] = float(metadata.get("lat", 0.0))
        hdu.header["TARG_LON"] = float(metadata.get("lon", 0.0))

        hdu = set_default_values_to_class_fits(hdu)
        hdu.writeto(output_fits_path, overwrite=True)

    except Exception:
        import traceback

        print(traceback.format_exc())
        return False
    else:
        return True


if __name__ == "__main__":
    folder_path = "/home/sm/Public/Inter-IIT/Astral-Ray-Scratchpad/Soumik/data/class"
    output_fits_path = "combined.fits"
    fits_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(".fits")]
    combine_fits(fits_files, output_fits_path, {})
