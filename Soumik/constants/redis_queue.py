from redis_work_queue import KeyPrefix, WorkQueue

step1_checks_job_queue = WorkQueue(KeyPrefix("STEP1_CHECKS_JOB_QUEUE"))
step2_xrf_line_intensity_job_queue = WorkQueue(KeyPrefix("STEP2_XRF_LINE_INTENSITY_JOB_QUEUE"))
step3_ml_prediction_job_queue = WorkQueue(KeyPrefix("STEP3_ML_PREDICTION_JOB_QUEUE"))
step4_x2_abund_job_queue = WorkQueue(KeyPrefix("STEP4_X2_ABUND_JOB_QUEUE"))
create_job_queue = WorkQueue(KeyPrefix("CREATE_JOB_QUEUE"))
sr_process = WorkQueue(KeyPrefix("SR_PROCESS"))

backend_0_fail_queue = WorkQueue(KeyPrefix("BACKEND_FAIL"))
backend_1_filter_queue = WorkQueue(KeyPrefix("BACKEND_FILTER"))
backend_2_xrf_line_queue = WorkQueue(KeyPrefix("BACKEND_XRF_LINE"))
backend_3_prediction_queue = WorkQueue(KeyPrefix("BACKEND_PREDICTION"))
backend_4_x2_abund_compare_queue = WorkQueue(KeyPrefix("BACKEND_X2_ABUND"))
backend_5_sr_process_queue = WorkQueue(KeyPrefix("BACKEND_SR"))


REDIS_HOST = "192.168.154.116"
