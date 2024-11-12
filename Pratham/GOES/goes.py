from datetime import datetime
from typing import Tuple


def add_buffer_time(
    start_time: datetime, end_time: datetime
) -> Tuple[datetime, datetime]:
    time_diff = end_time - start_time

    new_start_time = start_time - time_diff
    new_end_time = end_time + time_diff

    return new_start_time, new_end_time
