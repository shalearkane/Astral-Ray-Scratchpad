from redis import Redis
from redis_work_queue import Item
from Soumik.constants.redis_queue import REDIS_HOST, check_queue


db = Redis(host=REDIS_HOST)
try:
    json_item = Item.from_dict({"_id": "672ebf88a0c52a0831b97b06"})
    check_queue.add_item(db, json_item)
    print(check_queue.queue_len(db))
except Exception:
    import traceback

    print(traceback.format_exc())
