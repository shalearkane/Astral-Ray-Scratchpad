import pandas as pd
from datetime import datetime

from helpers.utilities import to_datetime

solar_flares = pd.read_csv("data-generated/goes/solar_flares.csv")
solar_flares["start_time"] = pd.to_datetime(solar_flares["start_time"])
solar_flares["end_time"] = pd.to_datetime(solar_flares["end_time"])


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
