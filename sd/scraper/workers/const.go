package workers

import "time"

const CH2_IDS_TO_DOWNLOAD = "CH2_IDS_TO_DOWNLOAD" // REDIS_QUEUE
const PREFETCH_LIMIT = 100
const POLL_DURATION = 10 * time.Second
