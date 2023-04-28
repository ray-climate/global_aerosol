#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    compare_reanalysis.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        28/04/2023 10:44

from netCDF4 import Dataset, num2date
import matplotlib.pyplot as plt
from scipy.stats import kde
import scipy.stats
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

def get_caliop_datetime(filename):
    datetime_str = filename[-16:-4]
    return datetime.datetime.strptime(datetime_str, "%Y%m%d%H%M%S")

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

# Create lists to store all CAMS and CALIOP AOD values
all_cams_aod_values = []
all_caliop_aod_values = []

for npz_file in os.listdir(caliop_path):
    if npz_file.endswith('.npz') & ('dbd_descending' in npz_file):

        caliop_datetime = get_caliop_datetime(npz_file)
        # start_time = caliop_datetime.replace(hour=5, minute=0, second=0, microsecond=0)
        # end_time = caliop_datetime.replace(hour=20, minute=0, second=0, microsecond=0)

        # if five_am <= caliop_datetime <= eight_pm:
        print('Processing file: ', npz_file, '...')

        # Find the closest AOD data from CAMS
        closest_time = find_closest_time(caliop_datetime, time_aod_dict)
        aod_data = time_aod_dict[closest_time]

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

        # Append the CAMS and CALIOP AOD values for this file to the lists
        all_cams_aod_values.extend(list(closest_cams_aod.values()))
        all_caliop_aod_values.extend(list(averaged_caliop_aod.values()))

# # Create the scatter plot using all_cams_aod_values and all_caliop_aod_values
# fig, ax = plt.subplots(figsize=(10, 10))
# ax.scatter(all_cams_aod_values, all_caliop_aod_values, marker='o', color='red', alpha=0.8)
#
# # Set plot settings
# ax.set_xlabel('CAMS AOD', fontsize=14)
# ax.set_ylabel('CALIOP AOD', fontsize=14)
# ax.set_title('CAMS vs CALIOP AOD', fontsize=16)
# ax.tick_params(axis='both', which='major', labelsize=12)
# ax.set_xlim([0, 3.])
# ax.set_ylim([0, 3.])
#
# #
# # Display the plot
# plt.savefig(save_path + 'cams_vs_caliop_aod.png', dpi=300, bbox_inches='tight')

aod_min = [0.1, 0.5, 1.0]
aod_max = [0.5, 1.0, 2.0]
# Create the hexbin density plot
nbins = 1000
all_cams_aod_values = np.asarray(all_cams_aod_values)
all_caliop_aod_values = np.asarray(all_caliop_aod_values)

for i in range(len(aod_min)):
    x = all_cams_aod_values[(all_cams_aod_values > aod_min[i]) & (all_caliop_aod_values > aod_min[i]) & (all_cams_aod_values < aod_max[i]) & (all_caliop_aod_values < aod_max[i])]
    y = all_caliop_aod_values[(all_cams_aod_values > aod_min[i]) & (all_caliop_aod_values > aod_min[i]) & (all_cams_aod_values < aod_max[i]) & (all_caliop_aod_values < aod_max[i])]

    print(np.mean(x) - np.mean(y))
    print(np.mean(x))
    print(np.mean(y))

    # Calculate R-squared value
    slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(x, y)
    r_squared = r_value**2

    k = kde.gaussian_kde([x, y])
    xi, yi = np.mgrid[x.min():x.max():nbins * 1j, y.min():y.max():nbins * 1j]
    zi = k(np.vstack([xi.flatten(), yi.flatten()]))

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.pcolormesh(xi, yi, zi.reshape(xi.shape), shading='auto', cmap='RdYlBu_r')
    # Set plot settings
    ax.set_xlabel('CAMS AOD', fontsize=14)
    ax.set_ylabel('CALIOP AOD', fontsize=14)
    ax.set_title('CAMS vs CALIOP AOD Density', fontsize=16)
    ax.tick_params(axis='both', which='major', labelsize=12)
    ax.plot([0, 2.5], [0, 2.5], 'k--', linewidth=2)

    ax.set_xlim([aod_min[i], aod_max[i]])
    ax.set_ylim([aod_min[i], aod_max[i]])

    # Add R-squared value and the number of data points to the plot
    num_data = len(x)
    text = f"Nr: {num_data}"
    ax.text(0.05, 0.95, text, fontsize=12, transform=ax.transAxes, verticalalignment='top', color = 'white')

    # Add the fitted line
    x_line = np.linspace(0, 2.5, 100)
    y_line = slope * x_line + intercept
    ax.plot(x_line, y_line, 'r-', linewidth=2)

    # Display the plot
    plt.savefig(save_path + 'cams_vs_caliop_aod_density_%s_%s.png'%(aod_min[i], aod_max[i]), dpi=300, bbox_inches='tight')
