from redis_work_queue import KeyPrefix, WorkQueue

step1_checks_job_queue = WorkQueue(KeyPrefix("STEP1_CHECKS_JOB_QUEUE"))
step2_xrf_line_intensity_job_queue = WorkQueue(KeyPrefix("STEP2_XRF_LINE_INTENSITY_JOB_QUEUE"))
step3_x2_abund_job_queue = WorkQueue(KeyPrefix("STEP3_X2_ABUND_JOB_QUEUE"))
create_job_queue = WorkQueue(KeyPrefix("CREATE_JOB_QUEUE"))

backend_fail_queue = WorkQueue(KeyPrefix("BACKEND_FAIL"))
backend_2_process_queue = WorkQueue(KeyPrefix("BACKEND_PROCESS"))
backend_3_output_queue = WorkQueue(KeyPrefix("BACKEND_OUTPUT"))
backend_1_check_queue = WorkQueue(KeyPrefix("BACKEND_CHECK"))


REDIS_HOST = "192.168.32.116"
