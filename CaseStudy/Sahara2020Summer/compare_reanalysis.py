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

def find_closest_time(target_time, time_dict):
    closest_time = min(time_dict.keys(), key=lambda t: abs(target_time - t))
    return closest_time

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of the Earth in km
    lat1, lon1, lat2, lon2 = np.radians([lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return R * c

def find_closest_aod_index(lat, lon, lats, lons):
    distances = haversine(lat, lon, lats[:, np.newaxis], lons[np.newaxis, :])
    return np.unravel_index(np.argmin(distances, axis=None), distances.shape)

def find_closest_aod(lat, lon, aod_data, latitudes, longitudes):
    closest_index = find_closest_aod_index(lat, lon, latitudes, longitudes)
    return aod_data[closest_index]

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

# Example: Access AOD data for the closest time
time_to_find = datetime.datetime(2020, 6, 14, 12, 33)
closest_time = find_closest_time(time_to_find, time_aod_dict)
aod_data = time_aod_dict[closest_time]

print(f"Closest time found: {closest_time}")
print(f"AOD data for the closest time:")
print(aod_data)

for npz_file in os.listdir(caliop_path):
    if npz_file.endswith('.npz') & ('caliop_dbd_descending_202006150327' in npz_file):

        lat_caliop = np.load(caliop_path + npz_file, allow_pickle=True)['lat']
        lon_caliop = np.load(caliop_path + npz_file, allow_pickle=True)['lon']
        alt_caliop = np.load(caliop_path + npz_file, allow_pickle=True)['alt']
        beta_caliop = np.load(caliop_path + npz_file, allow_pickle=True)['beta']
        alpha_caliop = np.load(caliop_path + npz_file, allow_pickle=True)['alpha']
        dp_caliop = np.load(caliop_path + npz_file, allow_pickle=True)['dp']
        aod_caliop = np.load(caliop_path + npz_file, allow_pickle=True)['aod']

        # Find the closest CAMS AOD data for each CALIOP AOD data point
        closest_cams_aod_indices = np.array([
            find_closest_aod_index(lat, lon, latitudes, longitudes)
            for lat, lon in zip(lat_caliop, lon_caliop)
        ])

        # Average the CALIOP AOD data points that correspond to the same CAMS AOD data point
        unique_indices, unique_counts = np.unique(closest_cams_aod_indices, axis=0, return_counts=True)
        averaged_caliop_aod = np.array([
            np.mean(aod_caliop[np.all(closest_cams_aod_indices == index, axis=1)])
            for index in unique_indices
        ])

        # Find the corresponding CAMS AOD data for the averaged CALIOP AOD data points
        closest_cams_aod = np.array([
            find_closest_aod(lat, lon, aod_data, latitudes, longitudes)
            for lat, lon in zip(lat_caliop, lon_caliop)
        ])

        print("Averaged CALIOP AOD data:")
        print(averaged_caliop_aod)

        print("Closest CAMS AOD data:")
        print(closest_cams_aod)


