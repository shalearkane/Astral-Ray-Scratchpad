from redis import Redis
from redis_work_queue import Item
from constants.redis_queue import REDIS_HOST, backend_1_check_queue


db = Redis(host=REDIS_HOST)
try:
    json_item = Item.from_json_data(id=1, data={"_id": "67547045fc1f043674c87e44"})
    backend_1_check_queue.add_item(db, json_item)
except Exception:
    import traceback

    print(traceback.format_exc())
