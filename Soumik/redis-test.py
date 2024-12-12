from redis import Redis
from redis_work_queue import Item
from constants.redis_queue import REDIS_HOST, backend_1_filter_queue, backend_5_sr_process_queue, create_job_queue


db = Redis(host=REDIS_HOST)
try:
    json_item = Item.from_json_data(id=1, data={"_id": "675af68378ddd69bcb1c063f", "clientId": "string"})
    backend_1_filter_queue.add_item(db, json_item)
    create_job_queue.add_item(db, json_item)

    # json_item = Item.from_json_data({"lat": 20, "lon": 20, "clientId": "string"})
    # backend_5_sr_process_queue.add_item(db, json_item)
except Exception:
    import traceback

    print(traceback.format_exc())
