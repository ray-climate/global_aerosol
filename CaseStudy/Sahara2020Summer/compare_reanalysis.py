#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    compare_reanalysis.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        28/04/2023 10:44

from netCDF4 import Dataset, num2date
import matplotlib.pyplot as plt
import numpy as np
import datetime
import pathlib
import os

def find_closest_time(target_time, time_dict):
    closest_time = min(time_dict.keys(), key=lambda t: abs(target_time - t))
    return closest_time

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth's radius in km
    lat1, lon1, lat2, lon2 = np.radians(lat1), np.radians(lon1), np.radians(lat2), np.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
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

        # Create a dictionary to store the unique CAMS AOD indices and corresponding averaged CALIOP AOD values
        unique_cams_caliop_aod = {}
        for lat, lon, caliop_aod_value in zip(lat_caliop, lon_caliop, aod_caliop):
            index = find_closest_aod_index(lat, lon, latitudes, longitudes)
            index_tuple = tuple(index)
            if index_tuple not in unique_cams_caliop_aod:
                unique_cams_caliop_aod[index_tuple] = [caliop_aod_value]
            else:
                unique_cams_caliop_aod[index_tuple].append(caliop_aod_value)

        # Calculate the averaged CALIOP AOD values for each unique CAMS AOD index
        averaged_caliop_aod = {k: np.mean(v) for k, v in unique_cams_caliop_aod.items()}

        # Find the corresponding CAMS AOD data for the unique indices
        closest_cams_aod = {}
        for index_tuple, avg_caliop_aod in averaged_caliop_aod.items():
            i, j = index_tuple
            closest_cams_aod[index_tuple] = aod_data[i, j]

        print("Averaged CALIOP AOD data:")
        print(averaged_caliop_aod)

        print("Closest CAMS AOD data:")
        print(closest_cams_aod)

# Extract the unique CAMS and corresponding averaged CALIOP AOD values
cams_aod_values = list(closest_cams_aod.values())
caliop_aod_values = list(averaged_caliop_aod.values())

# Create the scatter plot
fig, ax = plt.subplots(figsize=(10, 10))
ax.scatter(cams_aod_values, caliop_aod_values, marker='o', alpha=0.5)

# Set plot settings
ax.set_xlabel('CAMS AOD', fontsize=14)
ax.set_ylabel('CALIOP AOD', fontsize=14)
ax.set_title('CAMS vs CALIOP AOD', fontsize=16)
ax.tick_params(axis='both', which='major', labelsize=12)

# Display the plot
plt.savefig(save_path + 'cams_vs_caliop_aod.png', dpi=300, bbox_inches='tight')

