from pymongo import MongoClient
from constants.mongo import (
    MONGO_URI,
    DATABASE_ISRO,
    COLLECTION_XSM_PRIMARY,
)
from constants.misc import FILE_SERVER
import requests
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


def download_file(doc: dict):
    print(f"{FILE_SERVER}/primary_xsm/{doc["_id"]}")
    response = requests.get(f"{FILE_SERVER}/xsm_primary/{doc["_id"]}")
    response.raise_for_status()

    with open(f"data/xsm/{doc["path"].split("/")[-1]}", "wb") as f:
        f.write(response.content)


if __name__ == "__main__":
    start_time = datetime(2024, 8, 27, 0, 0, 0, tzinfo=timezone.utc)
    end_time = datetime(2024, 9, 27, 23, 59, 59, tzinfo=timezone.utc)
    list_of_docs = get_xsm_pha(start_time, end_time)
    for doc in list_of_docs:
        download_file(doc)
