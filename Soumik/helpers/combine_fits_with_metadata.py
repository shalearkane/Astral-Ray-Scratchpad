import numpy as np
import os
import math
from astropy.io import fits
from typing import Any, Dict, List, Final, Tuple
from astropy.table import Table
from datetime import datetime
from helpers.utilities import set_default_values_to_class_fits
from criterion.photon_count import photon_count_from_hdul

CHANNELS: Final[int] = 2048


def deg_to_rad(degrees: float) -> float:
    return (degrees * math.pi) / 180.0


def rad_to_deg(radians: float) -> float:
    return (radians * 180.0) / math.pi


class HDUL_META:
    photon_counts: np.ndarray = np.zeros(CHANNELS, dtype=np.float64)

    solar_zenith_angle: float = 0
    emission_angle: float = 0
    solar_zenith_angle_cosec: float = 0
    emission_angle_cosec: float = 0

    altitude: float = 0
    exposure: float = 0
    mid_utc: float = 0

    peak_na_h: float = 0
    peak_na_c: int = 0

    peak_mg_h: float = 0
    peak_mg_c: int = 0

    peak_al_h: float = 0
    peak_al_c: int = 0

    peak_si_h: float = 0
    peak_si_c: int = 0

    peak_ca_h: float = 0
    peak_ca_c: int = 0

    peak_ti_h: float = 0
    peak_ti_c: int = 0

    peak_fe_h: float = 0
    peak_fe_c: int = 0


def hdul_meta_to_dict(hdul_meta: HDUL_META) -> dict:
    return {
        "photon_counts": int(hdul_meta.photon_counts.sum()),
        "solar_zenith_angle": hdul_meta.solar_zenith_angle,
        "emission_angle": hdul_meta.emission_angle,
        "solar_zenith_angle_cosec": hdul_meta.solar_zenith_angle_cosec,
        "emission_angle_cosec": hdul_meta.emission_angle_cosec,
        "altitude": hdul_meta.altitude,
        "exposure": hdul_meta.exposure,
        "mid_utc": hdul_meta.mid_utc,
        "peak_na_h": hdul_meta.peak_na_h,
        "peak_na_c": hdul_meta.peak_na_c,
        "peak_mg_h": hdul_meta.peak_mg_h,
        "peak_mg_c": hdul_meta.peak_mg_c,
        "peak_al_h": hdul_meta.peak_al_h,
        "peak_al_c": hdul_meta.peak_al_c,
        "peak_si_h": hdul_meta.peak_si_h,
        "peak_si_c": hdul_meta.peak_si_c,
        "peak_ca_h": hdul_meta.peak_ca_h,
        "peak_ca_c": hdul_meta.peak_ca_c,
        "peak_ti_h": hdul_meta.peak_ti_h,
        "peak_ti_c": hdul_meta.peak_ti_c,
        "peak_fe_h": hdul_meta.peak_fe_h,
        "peak_fe_c": hdul_meta.peak_fe_c,
    }


def process_hdul(hdul, metadata: Dict[str, Any], weight: int, method: str = "weighted_average") -> HDUL_META:
    computed_metadata = HDUL_META()

    data = hdul["SPECTRUM"].data
    computed_metadata.photon_counts = data["COUNTS"]
    table = Table.read(hdul["SPECTRUM"])

    solar_zenith_angle = float(table.meta["SOLARANG"])
    emission_angle = float(table.meta["EMISNANG"])
    computed_metadata.solar_zenith_angle_cosec = 1.0 / math.sin(deg_to_rad(solar_zenith_angle))
    computed_metadata.emission_angle_cosec = 1.0 / math.sin(deg_to_rad(emission_angle))

    computed_metadata.altitude = float(table.meta["SAT_ALT"])
    computed_metadata.exposure = float(table.meta["EXPOSURE"])
    computed_metadata.mid_utc = datetime.strptime(table.meta["MID_UTC"], "%Y-%m-%dT%H:%M:%S.%f").timestamp()

    if metadata["visible_peaks"].get("Na", False):
        computed_metadata.peak_na_c = 1
        computed_metadata.peak_na_h = metadata["visible_peaks"].get("Na", 0)

    if metadata["visible_peaks"].get("Mg", False):
        computed_metadata.peak_mg_c = 1
        computed_metadata.peak_mg_h = metadata["visible_peaks"].get("Mg", 0)

    if metadata["visible_peaks"].get("Al", False):
        computed_metadata.peak_al_c = 1
        computed_metadata.peak_al_h = metadata["visible_peaks"].get("Al", 0)

    if metadata["visible_peaks"].get("Si", False):
        computed_metadata.peak_si_c = 1
        computed_metadata.peak_si_h = metadata["visible_peaks"].get("Si", 0)

    if metadata["visible_peaks"].get("Ca", False):
        computed_metadata.peak_ca_c = 1
        computed_metadata.peak_ca_h = metadata["visible_peaks"].get("Ca", 0)

    if metadata["visible_peaks"].get("Ti", False):
        computed_metadata.peak_ti_c = 1
        computed_metadata.peak_ti_h = metadata["visible_peaks"].get("Ti", 0)

    if metadata["visible_peaks"].get("Fe", False):
        computed_metadata.peak_fe_c = 1
        computed_metadata.peak_fe_h = metadata["visible_peaks"].get("Fe", 0)

    if method == "average":
        pass

    elif method == "rms":
        computed_metadata.photon_counts **= 2
        computed_metadata.solar_zenith_angle_cosec **= 2
        computed_metadata.emission_angle_cosec **= 2
        computed_metadata.altitude **= 2
        computed_metadata.exposure **= 2

        computed_metadata.peak_na_h **= 2
        computed_metadata.peak_mg_h **= 2
        computed_metadata.peak_al_h **= 2
        computed_metadata.peak_si_h **= 2
        computed_metadata.peak_ca_h **= 2
        computed_metadata.peak_ti_h **= 2
        computed_metadata.peak_fe_h **= 2

    elif method == "weighted_average":
        computed_metadata.photon_counts *= weight
        computed_metadata.solar_zenith_angle_cosec *= weight
        computed_metadata.emission_angle_cosec *= weight
        computed_metadata.altitude *= weight
        computed_metadata.exposure *= weight

        computed_metadata.peak_na_h *= weight
        computed_metadata.peak_mg_h *= weight
        computed_metadata.peak_al_h *= weight
        computed_metadata.peak_si_h *= weight
        computed_metadata.peak_ca_h *= weight
        computed_metadata.peak_ti_h *= weight
        computed_metadata.peak_fe_h *= weight

    else:
        raise ValueError(f"Unknown method: {method}")

    return computed_metadata


def add_to_computed_metadata_average(comp_meta_avg: HDUL_META, computed_metadata: HDUL_META) -> HDUL_META:
    comp_meta_avg.photon_counts += computed_metadata.photon_counts
    comp_meta_avg.solar_zenith_angle_cosec += computed_metadata.solar_zenith_angle_cosec
    comp_meta_avg.emission_angle_cosec += computed_metadata.emission_angle_cosec
    comp_meta_avg.altitude += computed_metadata.altitude
    comp_meta_avg.exposure += computed_metadata.exposure
    comp_meta_avg.mid_utc += computed_metadata.mid_utc

    comp_meta_avg.peak_na_h += computed_metadata.peak_na_h
    comp_meta_avg.peak_na_c += computed_metadata.peak_na_c

    comp_meta_avg.peak_mg_h += computed_metadata.peak_mg_h
    comp_meta_avg.peak_mg_c += computed_metadata.peak_mg_c

    comp_meta_avg.peak_al_h += computed_metadata.peak_al_h
    comp_meta_avg.peak_al_c += computed_metadata.peak_al_c

    comp_meta_avg.peak_si_h += computed_metadata.peak_si_h
    comp_meta_avg.peak_si_c += computed_metadata.peak_si_c

    comp_meta_avg.peak_ca_h += computed_metadata.peak_ca_h
    comp_meta_avg.peak_ca_c += computed_metadata.peak_ca_c

    comp_meta_avg.peak_ti_h += computed_metadata.peak_ti_h
    comp_meta_avg.peak_ti_c += computed_metadata.peak_ti_c

    comp_meta_avg.peak_fe_h += computed_metadata.peak_fe_h
    comp_meta_avg.peak_fe_c += computed_metadata.peak_fe_c

    return comp_meta_avg


def calculate_aggregate(
    files_used: int,
    comp_meta_avg: HDUL_META,
    weights_sum: float,
    method: str,
) -> HDUL_META:
    if method == "average":
        comp_meta_avg.photon_counts = np.sqrt(comp_meta_avg.photon_counts / files_used)
        comp_meta_avg.solar_zenith_angle_cosec = comp_meta_avg.solar_zenith_angle_cosec / files_used
        comp_meta_avg.emission_angle_cosec = comp_meta_avg.emission_angle_cosec / files_used
        comp_meta_avg.altitude = comp_meta_avg.altitude / files_used
        comp_meta_avg.exposure = comp_meta_avg.exposure / files_used

        comp_meta_avg.peak_na_h = comp_meta_avg.peak_na_h / files_used
        comp_meta_avg.peak_mg_h = comp_meta_avg.peak_mg_h / files_used
        comp_meta_avg.peak_al_h = comp_meta_avg.peak_al_h / files_used
        comp_meta_avg.peak_si_h = comp_meta_avg.peak_si_h / files_used
        comp_meta_avg.peak_ca_h = comp_meta_avg.peak_ca_h / files_used
        comp_meta_avg.peak_ti_h = comp_meta_avg.peak_ti_h / files_used
        comp_meta_avg.peak_fe_h = comp_meta_avg.peak_fe_h / files_used

    elif method == "rms":
        comp_meta_avg.photon_counts = np.sqrt(comp_meta_avg.photon_counts / files_used)
        comp_meta_avg.solar_zenith_angle_cosec = math.sqrt(comp_meta_avg.solar_zenith_angle_cosec / files_used)
        comp_meta_avg.emission_angle_cosec = math.sqrt(comp_meta_avg.emission_angle_cosec / files_used)
        comp_meta_avg.altitude = math.sqrt(comp_meta_avg.altitude / files_used)
        comp_meta_avg.exposure = math.sqrt(comp_meta_avg.exposure / files_used)

        comp_meta_avg.peak_na_h = math.sqrt(comp_meta_avg.peak_na_h / files_used)
        comp_meta_avg.peak_mg_h = math.sqrt(comp_meta_avg.peak_mg_h / files_used)
        comp_meta_avg.peak_al_h = math.sqrt(comp_meta_avg.peak_al_h / files_used)
        comp_meta_avg.peak_si_h = math.sqrt(comp_meta_avg.peak_si_h / files_used)
        comp_meta_avg.peak_ca_h = math.sqrt(comp_meta_avg.peak_ca_h / files_used)
        comp_meta_avg.peak_ti_h = math.sqrt(comp_meta_avg.peak_ti_h / files_used)
        comp_meta_avg.peak_fe_h = math.sqrt(comp_meta_avg.peak_fe_h / files_used)

    elif method == "weighted_average":
        comp_meta_avg.photon_counts = comp_meta_avg.photon_counts / weights_sum
        comp_meta_avg.solar_zenith_angle_cosec = comp_meta_avg.solar_zenith_angle_cosec / weights_sum
        comp_meta_avg.emission_angle_cosec = comp_meta_avg.emission_angle_cosec / weights_sum
        comp_meta_avg.altitude = comp_meta_avg.altitude / weights_sum
        comp_meta_avg.exposure = comp_meta_avg.exposure / weights_sum

        comp_meta_avg.peak_na_h = comp_meta_avg.peak_na_h / weights_sum
        comp_meta_avg.peak_mg_h = comp_meta_avg.peak_mg_h / weights_sum
        comp_meta_avg.peak_al_h = comp_meta_avg.peak_al_h / weights_sum
        comp_meta_avg.peak_si_h = comp_meta_avg.peak_si_h / weights_sum
        comp_meta_avg.peak_ca_h = comp_meta_avg.peak_ca_h / weights_sum
        comp_meta_avg.peak_ti_h = comp_meta_avg.peak_ti_h / weights_sum
        comp_meta_avg.peak_fe_h = comp_meta_avg.peak_fe_h / weights_sum

    else:
        raise ValueError(f"Unknown ideology: {method}")

    comp_meta_avg.solar_zenith_angle = rad_to_deg(math.asin(1.0 / max(abs(comp_meta_avg.solar_zenith_angle_cosec), 1)))
    comp_meta_avg.emission_angle = rad_to_deg(math.asin(1.0 / max(abs(comp_meta_avg.emission_angle_cosec), 1)))
    comp_meta_avg.mid_utc = comp_meta_avg.mid_utc / files_used

    return comp_meta_avg


def combine_fits_with_meta(
    fits_files: List[str], fits_docs: List[Dict[str, Any]], output_fits_path: str, lat_lon_meta: dict, method: str = "weighted_average"
) -> Tuple[bool, HDUL_META]:
    comp_meta_avg = HDUL_META()
    weights_sum = 0
    files_used = 0
    try:
        if len(fits_files) == 0:
            print("No input files provided for {lat_lon_meta}")
            return False, comp_meta_avg

        if len(fits_files) != len(fits_docs):
            print(f"File List and Doc List mismatch for {lat_lon_meta}")
            return False, comp_meta_avg

        for file_path, metadata in zip(fits_files, fits_docs):
            with fits.open(file_path) as hdul:

                files_used += 1
                weight = photon_count_from_hdul(hdul)
                computed_metadata = process_hdul(hdul, metadata, weight, method)
                comp_meta_avg = add_to_computed_metadata_average(comp_meta_avg, computed_metadata)

                if method == "weighted_average":
                    weights_sum += weight

        if files_used == 0:
            return False, comp_meta_avg

        comp_meta_avg = calculate_aggregate(
            files_used,
            comp_meta_avg,
            weights_sum,
            method,
        )

        mid_utc = datetime.fromtimestamp(comp_meta_avg.mid_utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]

        hdu = fits.BinTableHDU.from_columns(
            [
                fits.Column(name="CHANNEL", format="1I", array=np.arange(CHANNELS)),
                fits.Column(name="COUNTS", format="1D", array=comp_meta_avg.photon_counts),
            ]
        )

        hdu.header["SOLARANG"] = comp_meta_avg.solar_zenith_angle
        hdu.header["EMISNANG"] = comp_meta_avg.emission_angle
        hdu.header["MID_UTC"] = mid_utc
        hdu.header["SAT_ALT"] = comp_meta_avg.altitude
        hdu.header["EXPOSURE"] = comp_meta_avg.exposure

        hdu.header["PEAKC_NA"] = comp_meta_avg.peak_na_c
        hdu.header["PEAKH_NA"] = comp_meta_avg.peak_na_h

        hdu.header["PEAKC_MG"] = comp_meta_avg.peak_mg_c
        hdu.header["PEAKH_MG"] = comp_meta_avg.peak_mg_h

        hdu.header["PEAKC_AL"] = comp_meta_avg.peak_al_c
        hdu.header["PEAKH_AL"] = comp_meta_avg.peak_al_h

        hdu.header["PEAKC_SI"] = comp_meta_avg.peak_si_c
        hdu.header["PEAKH_SI"] = comp_meta_avg.peak_si_h

        hdu.header["PEAKC_CA"] = comp_meta_avg.peak_ca_c
        hdu.header["PEAKH_CA"] = comp_meta_avg.peak_ca_h

        hdu.header["PEAKC_TI"] = comp_meta_avg.peak_ti_c
        hdu.header["PEAKH_TI"] = comp_meta_avg.peak_ti_h

        hdu.header["PEAKC_FE"] = comp_meta_avg.peak_fe_c
        hdu.header["PEAKH_FE"] = comp_meta_avg.peak_fe_h

        # custom header
        hdu.header["FILE_CNT"] = files_used
        hdu.header["TARG_LAT"] = float(lat_lon_meta.get("latitude", 0.0))
        hdu.header["TARG_LON"] = float(lat_lon_meta.get("longitude", 0.0))

        hdu = set_default_values_to_class_fits(hdu)
        hdu.writeto(output_fits_path, overwrite=True)

    except Exception:
        import traceback

        print(traceback.format_exc())
        return False, comp_meta_avg
    else:
        return True, comp_meta_avg


if __name__ == "__main__":
    folder_path = "/home/sm/Public/Inter-IIT/Astral-Ray-Scratchpad/Soumik/data/class"
    output_fits_path = "combined.fits"
    fits_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(".fits")]
    combine_fits_with_meta(fits_files, [], output_fits_path, {})
