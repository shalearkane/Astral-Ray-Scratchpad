from typing import Optional, Tuple
import pandas as pd
from datetime import datetime

from helpers.utilities import to_datetime

solar_flares = pd.read_csv("data-generated/goes/solar_flares_class_split.csv")
solar_flares["start_time"] = pd.to_datetime(solar_flares["start_time"])
solar_flares["end_time"] = pd.to_datetime(solar_flares["end_time"])
solar_flares["class_alphabet"] = solar_flares["class_alphabet"].astype("category")
solar_flares["class_scale"] = solar_flares["class_scale"].astype("float")
solar_flares.sort_values("start_time")


def get_flare_class(start_time: datetime, end_time: Optional[datetime] = None) -> Tuple[str, float]:
    """Finds the key for a given time in a DataFrame with 'start_time', 'end_time', and 'key' columns.

    Args:
      df: The pandas DataFrame.
      time: The time to check.

    Returns:
      The key if found, otherwise None.
    """

    # Find the index of the first start_time greater than or equal to the given time
    matching_rows = solar_flares[(solar_flares["start_time"] <= start_time) & (solar_flares["end_time"] >= end_time)]

    if not matching_rows.empty:
        return matching_rows["class_alphabet"].iloc[0], matching_rows["class_scale"].iloc[0]
    else:
        return "None", 0


def is_during_a_solar_flare(docs: list[dict]) -> list[dict]:
    results: list[dict] = list()

    # Check each given time
    for class_observation in docs:
        if any(
            (solar_flares["start_time"] <= class_observation["parsedStartTime"])
            & (class_observation["parsedStartTime"] <= solar_flares["end_time"])
        ):
            results.append(class_observation)

    return results


if __name__ == "__main__":

    class_obv: list[dict] = [
        {"parsedStartTime": to_datetime("2019-07-15 11:40:00"), "parsedEndTime": to_datetime("2019-07-15 11:41:00")},
        {"parsedStartTime": to_datetime("2023-12-01 12:00:00"), "parsedEndTime": to_datetime("2023-12-01 12:00:08")},
    ]

    df = is_during_a_solar_flare(class_obv)
    print(df)
