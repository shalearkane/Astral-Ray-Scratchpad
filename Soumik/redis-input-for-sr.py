from dataclasses import dataclass
from typing import Dict, List


from constants.mongo import (
    DATABASE_ISRO,
    MONGO_URI,
    COLLECTION_TEMP_FIBONACCI,
)
from pymongo import MongoClient

from redis_work_queue import Item
from redis import Redis
from constants.redis_queue import (
    REDIS_HOST,
    sr_process,
    backend_5_sr_process_queue,
)


db = Redis(host=REDIS_HOST)

fibonacci_collection = MongoClient(MONGO_URI)[DATABASE_ISRO][COLLECTION_TEMP_FIBONACCI]


@dataclass
class BOUNDING_BOX:
    v0_lat: float
    v0_lon: float
    v1_lat: float
    v1_lon: float
    v2_lat: float
    v2_lon: float
    v3_lat: float
    v3_lon: float


def get_all_points_from_mongo(
    bbox: BOUNDING_BOX,
) -> List[Dict]:
    filter = {
        "$and": [
            {"lat": {"$lte": bbox.v0_lat}},
            {"lon": {"$gte": bbox.v0_lon}},
            {"lat": {"$gte": bbox.v1_lat}},
            {"lon": {"$gte": bbox.v1_lon}},
            {"lat": {"$gte": bbox.v2_lat}},
            {"lon": {"$lte": bbox.v2_lon}},
            {"lat": {"$lte": bbox.v3_lat}},
            {"lon": {"$lte": bbox.v3_lon}},
        ]
    }
    map = fibonacci_collection.find(filter, projection={"lat": 1, "lon": 1, "wt": 1, "_id": -1})

    return [{"lat": doc["lat"], "lon": doc["lon"], "wt": doc["wt"]} for doc in map]


def generate_rectangle_on_sphere(lat: float, lon: float) -> BOUNDING_BOX:
    return BOUNDING_BOX(30, 30, 10, 30, 10, 50, 30, 50)


def run_mapper():
    while True:
        print("Waiting for job ...")
        job: Item = backend_5_sr_process_queue.lease(db, 5)  # type: ignore
        try:
            doc = job.data_json()
            print(f"starting {doc}")

            patch = get_all_points_from_mongo(generate_rectangle_on_sphere(doc["lat"], doc["lon"]))
            print(patch)
            results = {"patch": patch}
            results["clientId"] = doc["clientId"]
            results_item = Item.from_json_data(id=job.id(), data=results)

            with open("redis-input-for-sr.json", "w") as f:
                import json

                f.write(json.dumps(results))

            sr_process.add_item(db, results_item)

        except Exception:
            import traceback

            print(traceback.format_exc())
        finally:
            backend_5_sr_process_queue.complete(db, job)


if __name__ == "__main__":
    run_mapper()
