import numpy as np
import os
import math

import matplotlib.pyplot as plt
from astropy.io import fits
from typing import Final, List
from astropy.table import Table
from datetime import datetime

from criterion.photon_count import photon_count_from_hdul


CHANNELS: Final[int] = 2048


def deg_to_rad(degrees: float) -> float:
    """Converts degrees to radians.

    Args:
      degrees: The angle in degrees.

    Returns:
      The angle in radians.
    """

    return (degrees * math.pi) / 180.0


def rad_to_deg(radians: float) -> float:
    """Converts radians to degrees.

    Args:
      radians: The angle in radians.

    Returns:
      The angle in degrees.

    """

    return (radians * 180.0) / math.pi


def combine_fits(fits_files: List[str], output_fits_path: str, metadata: dict, minimum_photon_count: int = 3000) -> bool:
    try:
        if len(fits_files) == 0:
            print(f"No input files provided for {metadata.get("lat", 0.0)} {metadata.get("lat", 0.0)}")
            return False

        photon_counts_sum = np.zeros(CHANNELS, dtype=np.float64)
        solar_zenith_angles_cosec_sum: float = 0
        emission_angles_cosec_sum: float = 0
        altitude_sum: float = 0
        exposure_sum: float = 0
        mid_utc_in_seconds_sum: float = 0
        files_used: int = 0

        for file_path in fits_files:
            with fits.open(file_path) as hdul:
                data = hdul["SPECTRUM"].data  # type: ignore
                photon_counts = data["COUNTS"]
                energy_channel = data["CHANNEL"]

                # if photon count if below threshold, don't use it
                if photon_count_from_hdul(hdul) < minimum_photon_count:
                    continue
                else:
                    files_used += 1

                photon_counts_sum += photon_counts

                table = Table.read(hdul["SPECTRUM"])

                solar_zenith_angles_cosec_sum += 1.0 / math.sin(deg_to_rad(float(table.meta["SOLARANG"])))
                emission_angles_cosec_sum += 1.0 / math.sin(deg_to_rad(float(table.meta["EMISNANG"])))
                altitude_sum += float(table.meta["SAT_ALT"])
                exposure_sum += float(table.meta["EXPOSURE"])
                mid_utc_in_seconds_sum += datetime.strptime(table.meta["MID_UTC"], "%Y-%m-%dT%H:%M:%S.%f").timestamp()

        if files_used == 0:
            print(f"No input files with {minimum_photon_count} photon count at {metadata.get("lat", 0.0)} {metadata.get("lat", 0.0)}")
            return False

        solar_zenith_angles_cosec_avg = solar_zenith_angles_cosec_sum / files_used
        emission_angles_cosec_avg = emission_angles_cosec_sum / files_used
        altitude_avg = altitude_sum / files_used
        mid_utc_in_seconds_avg = mid_utc_in_seconds_sum / files_used

        solar_zenith_angle = rad_to_deg(math.asin(1.0 / solar_zenith_angles_cosec_avg))
        emission_angle = rad_to_deg(math.asin(1.0 / emission_angles_cosec_avg))
        mid_utc = datetime.fromtimestamp(mid_utc_in_seconds_avg).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]

        # Save the combined data to a new FITS file
        hdu = fits.BinTableHDU.from_columns(
            [
                fits.Column(name="CHANNEL", format="1I", array=energy_channel),
                fits.Column(name="COUNTS", format="1D", array=photon_counts_sum),
            ]
        )

        hdu.header["EXTNAME"] = "SPECTRUM"
        hdu.header["HDUCLASS"] = "OGIP"
        hdu.header["HDUCLAS1"] = "SPECTRUM"
        hdu.header["HDUVERS1"] = "1.1.0"
        hdu.header["HDUVERS"] = "1.1.0"
        hdu.header["HDUCLAS2"] = "TOTAL"
        hdu.header["HDUCLAS3"] = "COUNT"
        hdu.header["TLMIN1"] = 0
        hdu.header["TLMAX1"] = 2047
        hdu.header["TELESCOP"] = "CHANDRAYAAN-2"
        hdu.header["INSTRUME"] = "CLASS"
        hdu.header["FILTER"] = "none"
        hdu.header["EXPOSURE"] = exposure_sum
        hdu.header["AREASCAL"] = 1.0
        hdu.header["BACKFILE"] = "NONE"
        hdu.header["BACKSCAL"] = 1.0
        hdu.header["CORRFILE"] = "NONE"
        hdu.header["CORRSCAL"] = 1.0
        hdu.header["RESPFILE"] = "class_rmf_v1.rmf"
        hdu.header["ANCRFILE"] = "class_arf_v1.arf"
        hdu.header["PHAVERSN"] = "1992a"
        hdu.header["DETCHANS"] = 2048
        hdu.header["CHANTYPE"] = "PHA"
        hdu.header["POISSERR"] = True
        hdu.header["STAT_ERR"] = 0
        hdu.header["SYS_ERR"] = 0
        hdu.header["GROUPING"] = 0
        hdu.header["QUALITY"] = 0
        hdu.header["EQUINOX"] = 2000.0
        hdu.header["DATE"] = "Sun Dec  6 14:23:21 2020"
        hdu.header["PROGRAM"] = "CLASS_add_scds.pro"
        hdu.header["IPFILE"] = "CLA01D18CHO0195703016020032073056411_08.pld"
        hdu.header["DATASET"] = 249
        hdu.header["STARTIME"] = "20200201T000000114"
        hdu.header["ENDTIME"] = "20200201T000008114"
        hdu.header["TEMP"] = -43.7
        hdu.header["GAIN"] = 13.5
        hdu.header["SCD_USED"] = "0,1,2,3,4,5,6,7,8,9,10,11"
        hdu.header["MID_UTC"] = mid_utc
        hdu.header["SAT_ALT"] = altitude_avg
        hdu.header["SAT_LAT"] = 0.0
        hdu.header["SAT_LON"] = 0.0
        hdu.header["LST_HR"] = 9
        hdu.header["LST_MIN"] = 36
        hdu.header["LST_SEC"] = 48
        hdu.header["BORE_LAT"] = 0.0
        hdu.header["BORE_LON"] = 0.0
        hdu.header["V1_LAT"] = 0.0
        hdu.header["V0_LAT"] = 0.0
        hdu.header["V2_LAT"] = 0.0
        hdu.header["V3_LAT"] = 0.0
        hdu.header["V0_LON"] = 0.0
        hdu.header["V1_LON"] = 0.0
        hdu.header["V2_LON"] = 0.0
        hdu.header["V3_LON"] = 0.0
        hdu.header["SOLARANG"] = solar_zenith_angle
        hdu.header["PHASEANG"] = 0.0
        hdu.header["EMISNANG"] = emission_angle

        # custom header
        hdu.header["FILE_CNT"] = files_used
        hdu.header["TARG_LAT"] = float(metadata.get("lat", 0.0))
        hdu.header["TARG_LON"] = float(metadata.get("lon", 0.0))

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
