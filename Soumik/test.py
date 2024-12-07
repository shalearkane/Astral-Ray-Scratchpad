from redis import Redis
from redis_work_queue import KeyPrefix, WorkQueue
from redis_work_queue import Item

db = Redis(host="127.0.0.1")

try:
    work_queue = WorkQueue(KeyPrefix("CHECK"))
    json_item = Item.from_json_data({"_id": "672eb942a0c52a083178d992"})
    work_queue.add_item(db, json_item)
    print(work_queue.queue_len(db))
except Exception:
    import traceback

    print(traceback.format_exc())
