from redis_work_queue import Item
from redis_work_queue import KeyPrefix, WorkQueue
import redis


db = redis.Redis(host="127.0.0.1")

work_queue = WorkQueue(KeyPrefix("example_work_queue"))

while True:
    # Wait for a job with no timeout and a lease time of 5 seconds.
    job: Item = work_queue.lease(db, 5)
    try:
        print(job)
    except Exception:
        work_queue.complete(db, job)
    # Mark successful jobs as complete
    work_queue.complete(db, job)
