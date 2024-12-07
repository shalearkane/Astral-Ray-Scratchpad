from redis_work_queue import KeyPrefix, WorkQueue

fail_queue = WorkQueue(KeyPrefix("FAIL"))
process_queue = WorkQueue(KeyPrefix("PROCESS"))
output_queue = WorkQueue(KeyPrefix("OUTPUT"))
check_queue = WorkQueue(KeyPrefix("CHECK"))


REDIS_HOST = "127.0.0.1"
