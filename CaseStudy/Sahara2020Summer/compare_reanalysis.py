#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    compare_reanalysis.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        28/04/2023 10:44

from netCDF4 import Dataset, num2date
import numpy as np
import datetime
import pathlib
import os

# Read the NetCDF file
cams_filename = './CAMS_data/CAMS_AOD550_20200614-20200624.nc'
caliop_path = './aeolus_caliop_sahara2020_extraction_output/'

# Define output directory
script_name = os.path.splitext(os.path.abspath(__file__))[0]
save_path = f'{script_name}_output/'
pathlib.Path(save_path).mkdir(parents=True, exist_ok=True)

# Extract the variable to plot (assuming 'aod' is the variable name)
nc_file = Dataset(cams_filename, 'r')
aod = nc_file.variables['aod550'][:]
latitudes = nc_file.variables['latitude'][:]
longitudes = nc_file.variables['longitude'][:]
time_var = nc_file.variables['time']
times = num2date(time_var[:], time_var.units)

# Create a dictionary mapping the datetime objects to the corresponding AOD data
time_aod_dict = {times[i]: aod[i] for i in range(88)}

def find_closest_time(target_time, time_dict):
    closest_time = min(time_dict.keys(), key=lambda t: abs(target_time - t))
    return closest_time

# Example: Access AOD data for the closest time
time_to_find = datetime.datetime(2020, 6, 14, 12, 33)
closest_time = find_closest_time(time_to_find, time_aod_dict)
aod_data = time_aod_dict[closest_time]

print(f"Closest time found: {closest_time}")
print(f"AOD data for the closest time:")
print(aod_data)

def get_caliop_datetime(filename):
    datetime_str = filename[-16:-4]
    return datetime.datetime.strptime(datetime_str, "%Y%m%d%H%M%S")

for npz_file in os.listdir(caliop_path):
    if npz_file.endswith('.npz') & ('caliop_dbd_descending_202006150327' in npz_file):

        # Extract CALIOP datetime from the file name
        caliop_datetime = get_caliop_datetime(npz_file)

        # Find the closest AOD data from CAMS
        closest_time = find_closest_time(caliop_datetime, time_aod_dict)

        print(f"CALIOP datetime: {caliop_datetime}")
        print(f"Closest time found: {closest_time}")
        print(f"AOD data for the closest time:")

        lat_caliop = np.load(caliop_path + npz_file, allow_pickle=True)['lat']
        lon_caliop = np.load(caliop_path + npz_file, allow_pickle=True)['lon']
        alt_caliop = np.load(caliop_path + npz_file, allow_pickle=True)['alt']
        beta_caliop = np.load(caliop_path + npz_file, allow_pickle=True)['beta']
        alpha_caliop = np.load(caliop_path + npz_file, allow_pickle=True)['alpha']
        dp_caliop = np.load(caliop_path + npz_file, allow_pickle=True)['dp']
        aod_caliop = np.load(caliop_path + npz_file, allow_pickle=True)['aod']