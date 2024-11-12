import sys
sys.path.append(r'..')

from datetime import datetime
from pymongo import MongoClient
from Pratham.constants.mongo import *


def get_class_within_time_range(start_time: datetime, end_time: datetime) -> list[dict]:
    class_fits_accepted = MongoClient(MONGO_URI)[DATABASE_NAME][
        COLLECTION_CLASS_FITS_ACCEPTED
    ]

    cursor = class_fits_accepted.find(
        filter={
            "parsedStartTime": {"$gte": start_time},
            "parsedEndTime": {"$lte": end_time},
        }
    )

    return [doc for doc in cursor]


if __name__ == "__main__":
    start_time = datetime(2022, 10, 8, 10, 20, 15)
    end_time = datetime(2022, 11, 9, 10, 40, 15)
    print(get_class_within_time_range(start_time, end_time))
