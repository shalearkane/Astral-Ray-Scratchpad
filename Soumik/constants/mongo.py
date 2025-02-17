from typing import Final

# MongoDB connection details
MONGO_URI: Final[str] = "mongodb://192.168.154.59:27017"
DATABASE_ISRO: Final[str] = "ISRO"
COLLECTION_CLASS_FITS: Final[str] = "primary"
COLLECTION_CLASS_JOB: Final[str] = "job"
COLLECTION_CLASS_FITS_ACCEPTED: Final[str] = "class_fits_accepted"
COLLECTION_CLASS_FITS_TEST_FITS: Final[str] = "test_fits"
COLLECTION_CLASS_FITS_FLARE_CLASSIFIED: Final[str] = "class_fits_flare_classified"
COLLECTION_XSM_PRIMARY: Final[str] = "xsm_primary"
COLLECTION_DATA_COLLECTION: Final[str] = "data_collection"
COLLECTION_DATA_COLLECTION_V2: Final[str] = "data_collection_v2"
COLLECTION_DATA_COLLECTION_V3: Final[str] = "data_collection_v3"
COLLECTION_DATA_COLLECTION_V4: Final[str] = "data_collection_v4"

COLLECTION_FIBONACCI_LAT_LON: Final[str] = "fibnacci_lat_lon"
COLLECTION_FIBONACCI_LAT_LON_V2: Final[str] = "fibnacci_lat_lon_v2"

KEY_PASSED_CHECK: Final[str] = "passed_check"
KEY_IS_IN_GEOTAIL: Final[str] = "is_in_geotail"

COLLECTION_TEMP_FIBONACCI: Final[str] = "fibonacci_temp_process"
