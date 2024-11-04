import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from astropy.io import fits
import matplotlib.pyplot as plt

def convert_endian(arr):
    # If the array dtype is big-endian, change to little-endian
    if arr.dtype.byteorder == '>':
        return arr.byteswap().newbyteorder()
    return arr

def met_to_utc(met_seconds):
    mission_start_utc = datetime(2017, 1, 1, 0, 0, 0)
    utc_time = mission_start_utc + timedelta(seconds=met_seconds)
    return utc_time

file_path = '/home/pg/ISRO_Inter_IIT/XSM_files/ch2_xsm_20240711_v1_level2.pha'
with fits.open(file_path) as hdul:
    data = hdul[1].data

    # Applying endian conversion
    data = {name: convert_endian(data[name]) for name in data.names}

    single_columns = ['SPEC_NUM', 'EXPOSURE', 'TSTART', 'TSTOP', 'FILT_STATUS']
    array_columns = ['CHANNEL', 'COUNTS', 'STAT_ERR', 'SYS_ERR']

    df = pd.DataFrame({col: data[col] for col in single_columns})

    def array_to_str(arr):
        return ','.join(map(str, arr))

    for col in array_columns:
        df[col] = [array_to_str(row) for row in data[col]]

value=df.iloc[10]

channels = list(map(int, value['CHANNEL'].split(',')))
counts = list(map(float, value['COUNTS'].split(',')))

expanded_df = pd.DataFrame({
    'CHANNEL': channels,
    'COUNTS': counts,
    'TSTART':value['TSTART'],
    'TSTOP':value['TSTOP'],
    'FILT_STATUS':value['FILT_STATUS'],
    'SYS_ERR':sys_err,
    'STAT_ERR':stat_err
})

expanded_df['CHANNEL']=(expanded_df['CHANNEL']*16.5)/1000

expanded_df['ADJUSTED_COUNTS'] = expanded_df['COUNTS'] * expanded_df['CHANNEL']



# Plotting Channels vs Counts
plt.figure(figsize=(10, 6))
plt.plot(expanded_df['CHANNEL'], expanded_df['ADJUSTED_COUNTS'], marker='o', linestyle='-')
plt.xlabel('KeV')
plt.ylabel('FLux')
plt.title('KeV vs Flux')
plt.grid(True)
plt.show()