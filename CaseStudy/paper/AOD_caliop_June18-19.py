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

        print("MYD04_lat_data: ", MYD04_lat_data)
        print("MYD04_lon_data: ", MYD04_lon_data)
        print("MYD04_aod_data: ", MYD04_aod_data)


quit()

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
ax.set_xlabel('Latitude', fontsize=fontsize)
ax.set_ylabel('Extinction [km$^{-1}$]', fontsize=fontsize)
ax.set_xlim(lat1_caliop, lat2_caliop)
ax.set_ylim(0, 5.)
# ax.set_title(f'layer between {layer[0]:.1f} km - {layer[1]:.1f} km', fontsize=fontsize, loc='left')
ax.tick_params(axis='both', labelsize=fontsize)
ax.legend(loc='best', fontsize=fontsize)
plt.savefig(save_path + f'CALIOP_AOD_June18.png', dpi=300)