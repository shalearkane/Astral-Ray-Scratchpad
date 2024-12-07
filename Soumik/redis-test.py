from redis import Redis
from redis_work_queue import Item
from constants.redis_queue import REDIS_HOST, check_queue


db = Redis(host=REDIS_HOST)
try:
    json_item = Item.from_json_data({"_id": "67547045fc1f043674c87e44"})
    check_queue.add_item(db, json_item)
    print(check_queue.queue_len(db))
except Exception:
    import traceback

    print(traceback.format_exc())
