from datetime import datetime
from astropy.io.fits import BinTableHDU


def to_datetime(date_string: str) -> datetime:
    return datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")


def to_datetime_t(date_string: str) -> datetime:
    return datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%f")


def set_default_values_to_class_fits(hdu: BinTableHDU) -> BinTableHDU:
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
    hdu.header["PHASEANG"] = 0.0

    return hdu
