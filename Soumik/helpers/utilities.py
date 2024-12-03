from datetime import datetime


def to_datetime(date_string: str) -> datetime:
    return datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")


def to_datetime_t(date_string: str) -> datetime:
    return datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%f")
