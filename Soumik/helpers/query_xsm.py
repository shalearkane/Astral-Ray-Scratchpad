from pymongo import MongoClient
from helpers.download import download_file_from_file_server
from constants.mongo import (
    MONGO_URI,
    DATABASE_ISRO,
    COLLECTION_XSM_PRIMARY,
)
from datetime import datetime, timezone


def get_xsm_pha(start_time: datetime, end_time: datetime):
    class_fits_accepted = MongoClient(MONGO_URI)[DATABASE_ISRO][COLLECTION_XSM_PRIMARY]

    filter = {
        "parsedStartTime": {
            "$gte": start_time,
            "$lte": end_time,
        },
        "ext": "pha",
    }

    project = {"_id": 1, "path": 1}

    result = class_fits_accepted.find(filter=filter, projection=project)

    return [doc for doc in result]


if __name__ == "__main__":
    start_time = datetime(2024, 8, 27, 0, 0, 0, tzinfo=timezone.utc)
    end_time = datetime(2024, 9, 27, 23, 59, 59, tzinfo=timezone.utc)
    list_of_docs = get_xsm_pha(start_time, end_time)
    for doc in list_of_docs:
        download_file_from_file_server(doc, "primary_xsm", "data/xsm")