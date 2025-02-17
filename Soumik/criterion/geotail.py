from typing import Any, Dict, List
from ephem import Date, previous_full_moon, next_full_moon
from datetime import datetime


def check_if_not_in_geotail(dt: datetime) -> bool:
    previous_fm = Date(previous_full_moon(dt)).datetime()
    next_fm = Date(next_full_moon(dt)).datetime()

    if (abs(dt - previous_fm).days < 3) or (abs(next_fm - dt).days < 3):
        return False

    return True


def batch_geotail_filter(docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = list()

    for class_observation in docs:
        start_time = class_observation["parsedStartTime"]
        end_time = class_observation["parsedEndTime"]

        if check_if_not_in_geotail(start_time) and check_if_not_in_geotail(end_time):
            results.append(class_observation)

    return results


if __name__ == "__main__":
    date = datetime.strptime("2022-01-14 23:48:26.239464", "%Y-%m-%d %H:%M:%S.%f")
    print(check_if_not_in_geotail(date))

# dates of full moons
# 2022-01-14 23:48:25.239464
# 2022-02-13 16:56:29.218386
# 2022-03-15 07:17:32.553880
# 2022-04-13 18:55:00.884514
# 2022-05-13 04:14:07.101041
# 2022-06-11 11:51:43.585486
# 2022-07-10 18:37:35.224890
# 2022-08-09 01:35:41.569476
# 2022-09-07 09:59:00.194267
# 2022-10-06 20:54:56.164619
# 2022-11-05 11:02:07.315576
# 2022-12-05 04:08:09.199056
# 2023-01-03 23:07:52.481031
# 2023-02-02 18:28:31.157837
# 2023-03-04 12:40:18.633738
# 2023-04-03 04:34:28.605465
# 2023-05-02 17:34:00.621031
# 2023-06-01 03:41:41.269914
# 2023-06-30 11:38:38.221192
# 2023-07-29 18:31:36.174053
# 2023-08-28 01:35:33.888821
# 2023-09-26 09:57:29.345188
# 2023-10-25 20:24:00.492525
# 2023-11-24 09:16:16.659352
# 2023-12-24 00:33:10.338272
# 2024-01-22 17:53:57.068241
# 2024-02-21 12:30:22.256647
# 2024-03-22 07:00:16.416823
# 2024-04-20 23:48:55.940044
# 2024-05-20 13:53:05.253562
# 2024-06-19 01:07:48.966101
# 2024-07-18 10:17:04.647700
# 2024-08-16 18:25:44.062309
# 2024-09-15 02:34:24.104426
# 2024-10-14 11:26:21.318674
# 2024-11-12 21:28:28.524933
# 2024-12-12 09:01:38.391654
