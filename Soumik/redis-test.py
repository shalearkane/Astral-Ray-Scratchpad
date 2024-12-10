from redis import Redis
from redis_work_queue import Item
from constants.redis_queue import REDIS_HOST, backend_1_check_queue


db = Redis(host=REDIS_HOST)
try:
    json_item = Item.from_json_data(id=1, data={"_id": "6758728075f569d70cff2cf6", "clientId": "string"})
    backend_1_check_queue.add_item(db, json_item)
except Exception:
    import traceback

    print(traceback.format_exc())
