from typing import Final

# MongoDB connection details
MONGO_URI: Final[str] = "mongodb://localhost:27017"
DATABASE_ISRO: Final[str] = "ISRO"
COLLECTION_CLASS_FITS: Final[str] = "primary"
COLLECTION_CLASS_FITS_ACCEPTED: Final[str] = "class_fits_accepted"
COLLECTION_XSM_PRIMARY: Final[str] = "xsm_primary"

KEY_PASSED_CHECK: Final[str] = "passed_check"
KEY_IS_IN_GEOTAIL: Final[str] = "is_in_geotail"