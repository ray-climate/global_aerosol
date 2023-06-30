#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    AOD_caliop_June18-19.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        30/06/2023 11:55

import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
from osgeo import gdal
import seaborn as sns
import pandas as pd
import numpy as np
import pathlib
import sys
import csv
import os

MYD04_base_path = "/neodc/modis/data/MYD04_L2/collection61"
input_path = '../Sahara2020Summer/aeolus_caliop_sahara2020_extraction_output/'
script_name = os.path.splitext(os.path.basename(os.path.abspath(__file__)))[0]
save_path = f'./figures/{script_name}_output/'
pathlib.Path(save_path).mkdir(parents=True, exist_ok=True)

lat1_caliop = 10.
lat2_caliop = 20.

caliop_aqua_hour_diff = 1.5 # 0.5 hour difference limit between CALIOP and Aqua
caliop_aqua_dis_threshold = 40. # 40 km distance threshold between CALIOP and Aqua

def find_closest_point_and_distance(lat_data, lon_data, point_lat, point_lon):
    distances = np.empty_like(lat_data, dtype=float)

    for i in range(lat_data.shape[0]):
        for j in range(lat_data.shape[1]):
            distances[i, j] = haversine(point_lat, point_lon, lat_data[i, j], lon_data[i, j])

    min_distance = np.min(distances)
    closest_point_index = np.unravel_index(np.argmin(distances), distances.shape)

    return closest_point_index, min_distance

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth's radius in kilometers

    # Convert latitudes and longitudes to radians
    lat1, lon1, lat2, lon2 = np.radians([lat1, lon1, lat2, lon2])

    # Calculate differences
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Apply Haversine formula
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

    return R * c  # Return distance in kilometers

for npz_file in os.listdir(input_path):
    if npz_file.endswith('.npz') & ('caliop_dbd_ascending_202006181612' in npz_file):

        lat_caliop_time1 = np.load(input_path + npz_file, allow_pickle=True)['lat']
        alt_caliop_time1 = np.load(input_path + npz_file, allow_pickle=True)['alt']
        beta_caliop_time1 = np.load(input_path + npz_file, allow_pickle=True)['beta']
        alpha_caliop_time1 = np.load(input_path + npz_file, allow_pickle=True)['alpha']
        dp_caliop_time1 = np.load(input_path + npz_file, allow_pickle=True)['dp']
        aod_caliop_time1 = np.load(input_path + npz_file, allow_pickle=True)['aod']

        lat_caliop = np.load(input_path + npz_file, allow_pickle=True)['lat']
        lon_caliop = np.load(input_path + npz_file, allow_pickle=True)['lon']
        aod_caliop = np.load(input_path + npz_file, allow_pickle=True)['aod']

        year_i = npz_file[-16:-12]
        month_i = npz_file[-12:-10]
        day_i = npz_file[-10:-8]
        hour_i = npz_file[-8:-6]
        minute_i = npz_file[-6:-4]

        MYD04_directory = os.path.join(MYD04_base_path, year_i, month_i, day_i)

        MODY04_colocation_file = []

        for file in os.listdir(MYD04_directory):

            matching_MYD04_file = os.path.join(MYD04_directory, file)
            hour_aqua = file[-26:-24]
            minute_aqua = file[-24:-22]

            if abs(int(hour_i) * 60 + int(minute_i) - int(hour_aqua) * 60 - int(
                    minute_aqua)) < caliop_aqua_hour_diff * 60:

                MYD04_latitude_file = 'HDF4_EOS:EOS_SWATH:"%s":mod04:Latitude' % matching_MYD04_file
                MYD04_longitude_file = 'HDF4_EOS:EOS_SWATH:"%s":mod04:Longitude' % matching_MYD04_file

                MYD04_latitude_data = gdal.Open(MYD04_latitude_file)
                MYD04_longitude_data = gdal.Open(MYD04_longitude_file)

                MYD04_latitude = MYD04_latitude_data.ReadAsArray()
                MYD04_longitude = MYD04_longitude_data.ReadAsArray()

                MYD04_latitude[MYD04_latitude == -999.] = np.nan
                MYD04_longitude[MYD04_longitude == -999.] = np.nan

                MYD04_lat_min = np.nanmin(MYD04_latitude)
                MYD04_lat_max = np.nanmax(MYD04_latitude)
                MYD04_lon_min = np.nanmin(MYD04_longitude)
                MYD04_lon_max = np.nanmax(MYD04_longitude)

                if (lat_caliop[0] > MYD04_lat_min) & (lat_caliop[0] < MYD04_lat_max) & (
                        lon_caliop[0] > MYD04_lon_min) & (lon_caliop[0] < MYD04_lon_max) & (
                        np.nanmin(MYD04_longitude[:, 0]) > np.nanmin(MYD04_longitude[:, -1])):
                    MODY04_colocation_file.append(matching_MYD04_file)

                if (lat_caliop[-1] > MYD04_lat_min) & (lat_caliop[-1] < MYD04_lat_max) & (
                        lon_caliop[-1] > MYD04_lon_min) & (lon_caliop[-1] < MYD04_lon_max) & (
                        np.nanmin(MYD04_longitude[:, 0]) > np.nanmin(MYD04_longitude[:, -1])):
                    MODY04_colocation_file.append(matching_MYD04_file)

        MODY04_colocation_file = list(set(MODY04_colocation_file))

        print("MODY04_colocation_file: ", MODY04_colocation_file)
        if len(MODY04_colocation_file) == 0:
            print('No colocation found')
            continue

        MYD04_lat_data = []
        MYD04_lon_data = []
        MYD04_aod_data = []

        for j in range(len(MODY04_colocation_file)):
            MYD04_lat_data_j = gdal.Open('HDF4_EOS:EOS_SWATH:"%s":mod04:Latitude' % MODY04_colocation_file[j])
            MYD04_lon_data_j = gdal.Open('HDF4_EOS:EOS_SWATH:"%s":mod04:Longitude' % MODY04_colocation_file[j])
            MYD04_aod_data_j = gdal.Open(
                'HDF4_EOS:EOS_SWATH:"%s":mod04:Optical_Depth_Land_And_Ocean' % MODY04_colocation_file[j])

            MYD04_lat_data.append(MYD04_lat_data_j.ReadAsArray())
            MYD04_lon_data.append(MYD04_lon_data_j.ReadAsArray())
            MYD04_aod_data.append(MYD04_aod_data_j.ReadAsArray())

        modis_aod_all = []
        modis_lat_all = []
        modis_lon_all = []

        for m in range(len(lat_caliop)):

            lat_m = lat_caliop[m]
            lon_m = lon_caliop[m]
            aod_m = aod_caliop[m]

            closest_point_index_list = []
            min_distance_list = []

            for n in range(len(MODY04_colocation_file)):
                closest_point_index_n, min_distance_n = find_closest_point_and_distance(MYD04_lat_data[n], MYD04_lon_data[n], lat_m, lon_m)
                closest_point_index_list.append(closest_point_index_n)
                min_distance_list.append(min_distance_n)

            closest_point_index = closest_point_index_list[np.argmin(min_distance_list)]
            min_distance = min_distance_list[np.argmin(min_distance_list)]
            modis_aod = MYD04_aod_data[np.argmin(min_distance_list)][closest_point_index]
            modis_lat = MYD04_lat_data[np.argmin(min_distance_list)][closest_point_index]
            modis_lon = MYD04_lon_data[np.argmin(min_distance_list)][closest_point_index]

            if (min_distance < caliop_aqua_dis_threshold) & (modis_aod > 0.):
                modis_aod_m = modis_aod * 0.001
            else:
                modis_aod_m = np.nan

            modis_aod_all.append(modis_aod_m)
            modis_lat_all.append(modis_lat)
            modis_lon_all.append(modis_lon)

np.savez_compressed('./output_aod_file.npz',
                    lat_caliop=lat_caliop,
                    lon_caliop=lon_caliop,
                    modis_lat_all=modis_lat_all,
                    modis_lon_all=modis_lon_all,
                    aod_caliop=aod_caliop,
                    modis_aod_all=modis_aod_all)

for npz_file in os.listdir(input_path):
    if npz_file.endswith('.npz') & ('caliop_dbd_descending_202006190412' in npz_file):

        lat_caliop_time2 = np.load(input_path + npz_file, allow_pickle=True)['lat']
        alt_caliop_time2 = np.load(input_path + npz_file, allow_pickle=True)['alt']
        beta_caliop_time2 = np.load(input_path + npz_file, allow_pickle=True)['beta']
        alpha_caliop_time2 = np.load(input_path + npz_file, allow_pickle=True)['alpha']
        dp_caliop_time2 = np.load(input_path + npz_file, allow_pickle=True)['dp']
        aod_caliop_time2 = np.load(input_path + npz_file, allow_pickle=True)['aod']

fontsize = 12
fig, ax = plt.subplots(figsize=(8, 6))
ax.plot(lat_caliop_time1, aod_caliop_time1, 'g.-',lw=3, markersize=5, label='CALIOP_time1')
ax.plot(lat_caliop_time2, aod_caliop_time2, 'b.-',lw=3, markersize=5, label='CALIOP_time2')
ax.plot(modis_lat_all, modis_aod_all, 'r.-',lw=3, markersize=5, label='MODIS')
ax.set_xlabel('Latitude', fontsize=fontsize)
ax.set_ylabel('Extinction [km$^{-1}$]', fontsize=fontsize)
ax.set_xlim(lat1_caliop, lat2_caliop)
ax.set_ylim(0, 5.)
# ax.set_title(f'layer between {layer[0]:.1f} km - {layer[1]:.1f} km', fontsize=fontsize, loc='left')
ax.tick_params(axis='both', labelsize=fontsize)
ax.legend(loc='best', fontsize=fontsize)
plt.savefig(save_path + f'CALIOP_AOD_June18.png', dpi=300)