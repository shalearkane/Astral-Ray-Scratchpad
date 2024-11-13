from datetime import datetime
import pandas as pd
from datetime import datetime, timedelta
from constants.mongo import *
from pymongo import MongoClient
from astropy.io import fits
from astropy.table import Table


def fetch_candidate_xsm(start_time: datetime, end_time: datetime):
    date = start_time.dt.date
    xsm_fits = MongoClient(MONGO_URI)[DATABASE_NAME][COLLECTION_CLASS_FITS]
    cursor = xsm_fits.find({"DATE": date})

    return [doc for doc in cursor]


def met_to_utc(met_seconds):
    mission_start_utc = datetime(2017, 1, 1, 0, 0, 0)
    utc_time = mission_start_utc + timedelta(seconds=met_seconds)
    return utc_time


def fetch_xsm_gti(xsm) -> str:

    return "hello"


def get_good_times(gti: str) -> pd.DataFrame:

    with fits.open(gti, memmap=True) as hdu_list:
        # Extract the data from the second HDU (index 1) as a FITS_rec array
        hdu_data = hdu_list[1].data
        # Convert the FITS_rec array to a DataFrame
        df = pd.DataFrame(hdu_data)
        ## the outputs should be in two columns
        df["START"] = df["START"].apply(met_to_utc)
        df["STOP"] = df["STOP"].apply(met_to_utc)

    return df


def check_time_intersect(
    start_time_of_goes_flare: datetime,
    end_time_of_goes_flare: datetime,
    gti: pd.DataFrame,
):





    return output_df

    # df=pd.read_csv(csv_path_goes)

    # df['Start_Time'] = pd.to_datetime(df['Start_Time'])
    # df['Peak_Time'] = pd.to_datetime(df['Peak_Time'])
    # df['End_Time'] = pd.to_datetime(df['End_Time'])

    # df['date_only'] = df['start_date'].dt.date

    # xsm_fits_all = MongoClient(MONGO_URI)[DATABASE_NAME][COLLECTION_CLASS_FITS]
    # cursor = class_fits_all.find().batch_size(1000).limit(10)
