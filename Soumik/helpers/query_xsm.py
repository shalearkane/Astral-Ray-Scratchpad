from pymongo import MongoClient
from helpers.download import download_file_from_file_server
from constants.mongo import (
    MONGO_URI,
    DATABASE_ISRO,
    COLLECTION_XSM_PRIMARY,
)
from datetime import datetime, timezone


def query_xsm_pha_within_date_range(start_time: datetime, end_time: datetime):
    xsm_collection = MongoClient(MONGO_URI)[DATABASE_ISRO][COLLECTION_XSM_PRIMARY]

    filter = {
        "parsedStartTime": {
            "$gte": start_time,
            "$lte": end_time,
        },
        "ext": "pha",
    }

    project = {"_id": 1, "path": 1}
    results = xsm_collection.find(filter=filter, projection=project)

    return [{"_id": result["_id"], "path": result["path"].split("/")[-1]} for result in results]


def query_relevant_xsm_pha(start_time: datetime, end_time: datetime):
    xsm_collection = MongoClient(MONGO_URI)[DATABASE_ISRO][COLLECTION_XSM_PRIMARY]

    filter = {
        "parsedStartTime": {
            "$lte": start_time,
        },
        "parsedEndTime": {
            "$gte": end_time,
        },
        "ext": "pha",
    }

    project = {"_id": 1, "path": 1}
    results = xsm_collection.find(filter=filter, projection=project)

    return [{"_id": result["_id"], "path": result["path"].split("/")[-1]} for result in results]


if __name__ == "__main__":
    start_time = datetime(2024, 8, 27, 0, 0, 0, tzinfo=timezone.utc)
    end_time = datetime(2024, 9, 27, 23, 59, 59, tzinfo=timezone.utc)
    list_of_docs = query_xsm_pha_within_date_range(start_time, end_time)
    for doc in list_of_docs:
        download_file_from_file_server(doc, "xsm_primary", "data/xsm")
