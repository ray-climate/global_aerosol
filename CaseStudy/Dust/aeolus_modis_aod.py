#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    aeolus_modis_aod.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        05/04/2023 18:59

import matplotlib.pyplot as plt
from osgeo import gdal
import numpy as np
import glob
import csv
import os
import re

AEOLUS_path = './aeolus_caliop_sahara2020_extraction_output/'
MYD04_base_path = "/neodc/modis/data/MYD04_L2/collection61"

def round_to_nearest_5_minutes(hour, minute):
    total_minutes = int(hour) * 60 + int(minute)
    rounded_minutes = round(total_minutes / 5) * 5
    rounded_hour = rounded_minutes // 60
    rounded_minute = rounded_minutes % 60
    return f"{rounded_hour:02}", f"{rounded_minute:02}"

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

def find_closest_point_and_distance(lat_data, lon_data, point_lat, point_lon):
    distances = np.empty_like(lat_data, dtype=float)

    for i in range(lat_data.shape[0]):
        for j in range(lat_data.shape[1]):
            distances[i, j] = haversine(point_lat, point_lon, lat_data[i, j], lon_data[i, j])

    min_distance = np.min(distances)
    closest_point_index = np.unravel_index(np.argmin(distances), distances.shape)

    return closest_point_index, min_distance

aeolus_aqua_hour_diff = 6. # 0.5 hour difference limit between CALIOP and Aqua
caliop_aqua_dis_threshold = 100. # 40 km distance threshold between CALIOP and Aqua

aeolus_filename = []
aeolus_lat_all = []
aeolus_lon_all = []
aeolus_aod_all = []
modis_aod_all = []
distance_all = []

for npz_file in os.listdir(AEOLUS_path):
    if npz_file.startswith('aeolus_') & ('ing' in npz_file) & npz_file.endswith('.npz'):

        alt_aeolus = np.load(AEOLUS_path + npz_file, allow_pickle=True)['alt']
        lat_aeolus = np.load(AEOLUS_path + npz_file, allow_pickle=True)['lat']
        lon_aeolus = np.load(AEOLUS_path + npz_file, allow_pickle=True)['lon']
        alpha_aeolus = np.load(AEOLUS_path + npz_file, allow_pickle=True)['alpha']

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

            if abs(int(hour_i) * 60 + int(minute_i) - int(hour_aqua) * 60 - int(minute_aqua)) < aeolus_aqua_hour_diff * 60:

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

                if (lat_aeolus[0] > MYD04_lat_min) & (lat_aeolus[0] < MYD04_lat_max) & (lon_aeolus[0] > MYD04_lon_min) & (lon_aeolus[0] < MYD04_lon_max) & (np.nanmin(MYD04_longitude[:,0]) > np.nanmin(MYD04_longitude[:,-1])):
                    MODY04_colocation_file.append(matching_MYD04_file)

                if (lat_aeolus[-1] > MYD04_lat_min) & (lat_aeolus[-1] < MYD04_lat_max) & (lon_aeolus[-1] > MYD04_lon_min) & (lon_aeolus[-1] < MYD04_lon_max) & (np.nanmin(MYD04_longitude[:,0]) > np.nanmin(MYD04_longitude[:,-1])):
                    MODY04_colocation_file.append(matching_MYD04_file)

        MODY04_colocation_file = list(set(MODY04_colocation_file))

        if len(MODY04_colocation_file) == 0:
            print('No colocation found')
            continue

        MYD04_lat_data = []
        MYD04_lon_data = []
        MYD04_aod_data = []

        for j in range(len(MODY04_colocation_file)):

            MYD04_lat_data_j = gdal.Open('HDF4_EOS:EOS_SWATH:"%s":mod04:Latitude' % MODY04_colocation_file[j])
            MYD04_lon_data_j = gdal.Open('HDF4_EOS:EOS_SWATH:"%s":mod04:Longitude' % MODY04_colocation_file[j])
            MYD04_aod_data_j = gdal.Open('HDF4_EOS:EOS_SWATH:"%s":mod04:Optical_Depth_Land_And_Ocean' % MODY04_colocation_file[j])

            MYD04_lat_data.append(MYD04_lat_data_j.ReadAsArray())
            MYD04_lon_data.append(MYD04_lon_data_j.ReadAsArray())
            MYD04_aod_data.append(MYD04_aod_data_j.ReadAsArray())

        for m in range(len(lat_aeolus)):

            lat_m = lat_aeolus[m]
            lon_m = lon_aeolus[m]
            alt_m = alt_aeolus[m]
            alpha_m = alpha_aeolus[m]

            closest_point_index_list = []
            min_distance_list = []
            print(lat_m, lon_m)
            print(alt_m)
            print(alpha_m)
            quit()
            for n in range(len(MODY04_colocation_file)):
                closest_point_index_n, min_distance_n = find_closest_point_and_distance(MYD04_lat_data[n], MYD04_lon_data[n], lat_m, lon_m)
                closest_point_index_list.append(closest_point_index_n)
                min_distance_list.append(min_distance_n)

            closest_point_index = closest_point_index_list[np.argmin(min_distance_list)]
            min_distance = min_distance_list[np.argmin(min_distance_list)]
            modis_aod = MYD04_aod_data[np.argmin(min_distance_list)][closest_point_index]

            if (min_distance < caliop_aqua_dis_threshold) & (modis_aod > 0.):
                aeolus_filename.append(npz_file)
                aeolus_lat_all.append(lat_m)
                aeolus_lon_all.append(lon_m)
                aeolus_aod_all.append(aod_m)
                distance_all.append(min_distance)
                modis_aod_all.append(modis_aod * 0.001)
                print(npz_file, lat_m, lon_m, min_distance, aod_m, modis_aod * 0.001)

# save npz_file, lat_m, lon_m, aod_m, modis_aod * 0.001 in a csv file

with open(AEOLUS_path + 'aeolus_modis_aod_crs.csv', 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    # Write the header
    csv_writer.writerow(['caliop_npz_file', 'lat_caliop', 'lon_caliop', 'distance', 'aod_caliop', 'aod_modis'])
    for k in range(len(aeolus_filename)):
        csv_writer.writerow([aeolus_filename[k], aeolus_lat_all[k], aeolus_lon_all[k], distance_all[k], aeolus_aod_all[k], modis_aod_all[k]])
