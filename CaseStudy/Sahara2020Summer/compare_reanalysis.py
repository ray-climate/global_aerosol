#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    compare_reanalysis.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        28/04/2023 10:44

from netCDF4 import Dataset, num2date
import numpy as np
import datetime
import os

# Read the NetCDF file
filename = './CAMS_data/CAMS_AOD550_20200614-20200624.nc'
nc_file = Dataset(filename, 'r')

# Extract the variable to plot (assuming 'aod' is the variable name)
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
