from dataclasses import dataclass
import astropy.io.fits as aif
from astropy.table import Table
from constants.class_fits import *


@dataclass
class CLASS_HEADER:
    latitude_0: float
    latitude_1: float
    latitude_2: float
    latitude_3: float

    longitude_0: float
    longitude_1: float
    longitude_2: float
    longitude_3: float


with aif.open("ch2_cla_l1_20210827T210316000_20210827T210332000_1024.fits") as hdul:
    t = Table.read(hdul["SPECTRUM"])

    for key, value in t.meta.items():
        print(f"{key} = {value}")

    ch = CLASS_HEADER(
        float(t.meta[V0_LAT]),
        float(t.meta[V1_LAT]),
        float(t.meta[V2_LAT]),
        float(t.meta[V3_LAT]),
        float(t.meta[V0_LON]),
        float(t.meta[V1_LON]),
        float(t.meta[V2_LON]),
        float(t.meta[V3_LON]),
    )