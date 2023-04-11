#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    caliop_modis_aod.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        30/03/2023 19:11

import matplotlib.pyplot as plt
from osgeo import gdal
import numpy as np
import glob
import csv
import os
import re

"/neodc/modis/data/MYD04_L2/collection61/2020/06/14/"
CALIOP_path = './aeolus_caliop_sahara2020_extraction_output/'
MYD04_base_path = "/neodc/modis/data/MYD04_L2/collection61"
specific_filename = 'caliop_dbd_ascending_202006201727'

def mtile_cal(lat, lon):

    x_step = -463.31271653
    y_step = 463.31271653
    # m_y0, m_x0 = -20015109.354, 10007554.677

    tile_width = 1111950.5196666666
    # m_x0, m_y0 = -20015109.35579742, -10007554.677898709
    m_x0, m_y0 = -20015109.35579742, -10007554.677898709

    outProj = Proj('+proj=sinu +lon_0=0 +x_0=0 +y_0=0 +a=6371007.181 +b=6371007.181 +units=m +no_defs')
    inProj = Proj(init='epsg:4326')
    ho, vo = transform(inProj, outProj, np.array(lon).ravel(), np.array(lat).ravel())
    h = ((ho - m_x0) / tile_width).astype(int)
    v = 17 - ((vo - m_y0) / tile_width).astype(int)
    print(h[0], v[0])
    return f"{h[0]:02}", f"{v[0]:02}"

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

caliop_aqua_hour_diff = 1.5 # 0.5 hour difference limit between CALIOP and Aqua
caliop_aqua_dis_threshold = 40. # 40 km distance threshold between CALIOP and Aqua

caliop_filename = []
caliop_lat_all = []
caliop_lon_all = []
caliop_aod_all = []
modis_aod_all = []
distance_all = []

for npz_file in os.listdir(CALIOP_path):
    if npz_file.endswith('%s.npz'%specific_filename):
        print(npz_file)
        lat_caliop = np.load(CALIOP_path + npz_file, allow_pickle=True)['lat']
        lon_caliop = np.load(CALIOP_path + npz_file, allow_pickle=True)['lon']
        aod_caliop = np.load(CALIOP_path + npz_file, allow_pickle=True)['aod']

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

            if abs(int(hour_i) * 60 + int(minute_i) - int(hour_aqua) * 60 - int(minute_aqua)) < caliop_aqua_hour_diff * 60:

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

                if (lat_caliop[0] > MYD04_lat_min) & (lat_caliop[0] < MYD04_lat_max) & (lon_caliop[0] > MYD04_lon_min) & (lon_caliop[0] < MYD04_lon_max) & (np.nanmin(MYD04_longitude[:,0]) > np.nanmin(MYD04_longitude[:,-1])):
                    MODY04_colocation_file.append(matching_MYD04_file)

                if (lat_caliop[-1] > MYD04_lat_min) & (lat_caliop[-1] < MYD04_lat_max) & (lon_caliop[-1] > MYD04_lon_min) & (lon_caliop[-1] < MYD04_lon_max) & (np.nanmin(MYD04_longitude[:,0]) > np.nanmin(MYD04_longitude[:,-1])):
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

            if (min_distance < caliop_aqua_dis_threshold) & (modis_aod > 0.):
                modis_aod_m = modis_aod * 0.001
            else:
                modis_aod_m = np.nan

            caliop_filename.append(npz_file)
            caliop_lat_all.append(lat_m)
            caliop_lon_all.append(lon_m)
            caliop_aod_all.append(aod_m)
            distance_all.append(min_distance)
            modis_aod_all.append(modis_aod_m)
            print(npz_file, lat_m, lon_m, min_distance, aod_m, modis_aod_m)

# save npz_file, lat_m, lon_m, aod_m, modis_aod * 0.001 in a csv file

with open(CALIOP_path + '%s.csv'%specific_filename, 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    # Write the header
    csv_writer.writerow(['caliop_npz_file', 'lat_caliop', 'lon_caliop', 'distance', 'aod_caliop', 'aod_modis'])
    for k in range(len(caliop_filename)):
        csv_writer.writerow([caliop_filename[k], caliop_lat_all[k], caliop_lon_all[k], distance_all[k], caliop_aod_all[k], modis_aod_all[k]])



""" 
#tile number searching for MCD19A2 products not neeeded anymore
tile_h1, tile_v1 = mtile_cal(lat[0], lon[0])
print("MODIS Tile: ", tile_h1, tile_v1)
tile_h2, tile_v2 = mtile_cal(lat[-1], lon[-1])
print("MODIS Tile: ", tile_h1, tile_v1)
# use glob to find "*h{tile_h}v{tile_v}*.hdf" in MCD19A2_directory
MCD19A2_file1 = glob.glob(MCD19A2_directory + f"/*h{tile_h1}v{tile_v1}*.hdf")[0]
MCD19A2_file2 = glob.glob(MCD19A2_directory + f"/*h{tile_h2}v{tile_v2}*.hdf")[0]

# check if the two files are the same, and delete one of them if they are the same
if MCD19A2_file1 == MCD19A2_file2:
    os.remove(MCD19A2_file2)
    print("The two files are the same, and the second file is deleted.")

# check if MCD19A2_file1 exists
if os.path.exists(MCD19A2_file1):
    print("%s file found." % MCD19A2_file1)
# check if MCD19A2_file2 exists
if os.path.exists(MCD19A2_file2):
    print("%s file found." % MCD19A2_file2)

modis_aod_file = 'HDF4_EOS:EOS_SWATH:"%s":mod04:Optical_Depth_Land_And_Ocean' % MCD19A2_file1
"""


