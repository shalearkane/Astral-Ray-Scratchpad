import redis
from redis_work_queue import KeyPrefix, WorkQueue
from redis_work_queue import Item

db = redis.Redis(host="127.0.0.1")

work_queue = WorkQueue(KeyPrefix("example_work_queue"))
json_item = Item.from_json_data(["something"])
work_queue.add_item(db, json_item)
