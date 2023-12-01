#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    plot_distance_above_tropopause.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        29/11/2023 21:55

import csv
import os
import sys
import logging
import argparse
import numpy as np
import proplot as pplt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.colors import LogNorm
from datetime import datetime, timedelta
from collections import defaultdict

# Append the custom path to system path
sys.path.append('../../')
from getColocationData.get_caliop import *

ASH_LAYER_DATA_PATH = './ash_Layer_csv_DN_flag'
SAVE_FIGURE_PATH = './ash_Layer_figures'

START_DATE = datetime.strptime('2011-06-04', '%Y-%m-%d')
END_DATE = datetime.strptime('2011-07-31', '%Y-%m-%d')

# Create csv saving directory if not present
if not os.path.exists(SAVE_FIGURE_PATH):
    os.mkdir(SAVE_FIGURE_PATH)

def read_ash_layer_csv(ash_layer_csv_file):
    """
    Read the ash layer csv file and return the following parameters: caliop_lat, caliop_lon, caliop_Layer_Base, caliop_Layer_Top, caliop_Tropopause_Altitude, caliop_aerosol_type, caliop_CAD

    :param ash_layer_csv_file: the csv file containing the ash layer data
    :return: caliop_Profile_Time, caliop_lat, caliop_lon, caliop_Layer_Base, caliop_Layer_Top, caliop_Tropopause_Altitude, caliop_aerosol_type, caliop_CAD
    """
    with open(ash_layer_csv_file, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # skip the header
        caliop_Profile_Time = [] # this is a string like "'2018-06-01 01:04:58.787400"
        caliop_lat = []
        caliop_lon = []
        caliop_Layer_Base = []
        caliop_Layer_Top = []
        caliop_Tropopause_Altitude = []
        caliop_aerosol_type = []
        caliop_CAD = []
        DN_flag = []

        for row in reader:
            try:
                profile_time = datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S.%f')
                lat = float(row[1])

                if (-80 <= lat <= -20) & (float(row[8]) == 2) & (float(row[9]) <= -20.) & (float(row[10]) == 1.) & (START_DATE <= profile_time <= END_DATE):

                    caliop_Profile_Time.append(row[0])
                    caliop_lat.append(float(row[1]))
                    caliop_lon.append(float(row[2]))
                    caliop_Layer_Base.append(float(row[3]))
                    caliop_Layer_Top.append(float(row[4]))
                    caliop_Tropopause_Altitude.append(float(row[5]))
                    caliop_aerosol_type.append(float(row[8]))
                    caliop_CAD.append(float(row[9]))
                    DN_flag.append(float(row[10]))

            except:
                continue

    return caliop_Profile_Time, caliop_lat, caliop_lon, caliop_Layer_Base, caliop_Layer_Top, caliop_Tropopause_Altitude, caliop_aerosol_type, caliop_CAD, DN_flag

def bin_and_filter_data(dates, lats, lons, *other_data):
    binned_data = defaultdict(lambda: defaultdict(list))

    for date, lat, lon, *other in zip(dates, lats, lons, *other_data):
        day = date.date()
        lat_bin = int(lat)
        lon_bin = int(lon)
        binned_data[day][(lat_bin, lon_bin)].append((date, lat, lon, *other))

    filtered_data = defaultdict(lambda: defaultdict(list))
    for day, bins in binned_data.items():
        for bin_key, values in bins.items():
            if len(values) >= 3:
                filtered_data[day][bin_key].extend(values)

    unpacked_data = {new_list: [] for new_list in
                     ['dates', 'lats', 'lons'] + ['list' + str(i) for i in range(len(other_data))]}
    for day, bins in filtered_data.items():
        for bin_key, values in bins.items():
            for value in values:
                unpacked_data['dates'].append(value[0])
                unpacked_data['lats'].append(value[1])
                unpacked_data['lons'].append(value[2])
                for i, val in enumerate(value[3:]):
                    unpacked_data['list' + str(i)].append(val)

    return [unpacked_data['dates'], unpacked_data['lats'], unpacked_data['lons']] + [unpacked_data['list' + str(i)] for
                                                                                     i in range(len(other_data))]


# Initialize lists to store data from all files
all_caliop_Profile_Time = []
all_caliop_lat = []
all_caliop_lon = []
all_caliop_Layer_Base = []
all_caliop_Layer_Top = []
all_caliop_Tropopause_Altitude = []
all_caliop_aerosol_type = []
all_caliop_CAD = []
all_caliop_DN_flag = []

# Iterate over all CSV files in the directory
for file in os.listdir(ASH_LAYER_DATA_PATH):
    if file.endswith(".csv") & file.startswith('stratosphere_aerosol_layers_2011'):
        ash_layer_csv_file = os.path.join(ASH_LAYER_DATA_PATH, file)
        caliop_Profile_Time, caliop_lat, caliop_lon, caliop_Layer_Base, caliop_Layer_Top, caliop_Tropopause_Altitude, caliop_aerosol_type, caliop_CAD, DN_flag = read_ash_layer_csv(ash_layer_csv_file)

        # Append data from this file to the collective lists
        all_caliop_Profile_Time.extend(caliop_Profile_Time)
        all_caliop_lat.extend(caliop_lat)
        all_caliop_lon.extend(caliop_lon)
        all_caliop_Layer_Base.extend(caliop_Layer_Base)
        all_caliop_Layer_Top.extend(caliop_Layer_Top)
        all_caliop_Tropopause_Altitude.extend(caliop_Tropopause_Altitude)
        all_caliop_aerosol_type.extend(caliop_aerosol_type)
        all_caliop_CAD.extend(caliop_CAD)
        all_caliop_DN_flag.extend(DN_flag)

        print('Number of detected ash layers from file {}: {}'.format(file, len(caliop_Profile_Time)))

# Step 1: Convert all_caliop_Profile_Time to datetime objects
caliop_times = [datetime.strptime(time, '%Y-%m-%d %H:%M:%S.%f') for time in all_caliop_Profile_Time]

# Filter and bin the data
caliop_times, all_caliop_lat, all_caliop_lon, all_caliop_Layer_Base, all_caliop_Layer_Top, all_caliop_Tropopause_Altitude, all_caliop_aerosol_type, all_caliop_CAD, all_caliop_DN_flag = bin_and_filter_data(caliop_times, all_caliop_lat, all_caliop_lon, all_caliop_Layer_Base, all_caliop_Layer_Top, all_caliop_Tropopause_Altitude, all_caliop_aerosol_type, all_caliop_CAD, all_caliop_DN_flag)
layer_base_minus_tropopause = (np.array(all_caliop_Layer_Top) + np.array(all_caliop_Layer_Base)) / 2. - np.array(all_caliop_Tropopause_Altitude)
data = layer_base_minus_tropopause

# Set a custom style for the plot
# pplt.rc.update({
#     'figure.facecolor': 'white',  # Background color
#     'axes.labelcolor': 'black',   # Label color
#     'axes.edgecolor': 'black',   # Axis edge color
#     'xtick.color': 'black',      # X-axis tick color
#     'ytick.color': 'black',      # Y-axis tick color
#     'grid.alpha': 0.5,           # Grid lines transparency
# })

# Set up the figure using ProPlot
fig, ax = pplt.subplots(refwidth=4, refaspect=(3, 2))

# Set title, xlabel, and ylabel
ax.format(suptitle='Ash Layer Base to Tropopause Distance Histogram', xlabel='Distance [km]', ylabel='Frequency')

# Create a histogram plot
ax.hist(
    layer_base_minus_tropopause, pplt.arange(min(layer_base_minus_tropopause), max(layer_base_minus_tropopause), 0.2),
    filled=True, alpha=0.7, edgecolor='black',
    cycle=('indigo9', 'gray3', 'red9'), legend='ul', labels=['Data']
)


# Save the figure
save_path = os.path.join(SAVE_FIGURE_PATH, 'base_above_tropopause_hist.png')
fig.savefig(save_path, dpi=300)
# fig, ax = plt.subplots(figsize=(18, 18))
#
# plt.hist(layer_base_minus_tropopause, bins=50, color='blue', edgecolor='black')
# plt.title('Ash Layer Base to Tropopause Distance [km]')
# plt.xlabel('Distance [km]')
# plt.ylabel('Frequency')
# plt.savefig(os.path.join(SAVE_FIGURE_PATH, 'base_above_tropopause_hist.png'), dpi=300)
#
#
# X, Y = np.meshgrid(xedges, yedges)
# mesh = ax.pcolormesh(X, Y, hist.T, shading='auto', cmap='plasma', norm=LogNorm())
# # mesh = ax.pcolormesh(X, Y, hist.T, shading='auto', cmap='plasma', vmin=20, vmax=100)
# # Format the time axis
# ax.xaxis_date()
# date_format = mdates.DateFormatter('%Y-%m-%d')
# ax.xaxis.set_major_formatter(date_format)
# plt.xticks(rotation=45, fontsize=16)
# plt.yticks(fontsize=16)
# plt.ylim([-80., 80.])
# plt.xlabel('Time', fontsize=18)
# plt.ylabel('Latitude', fontsize=18)
# plt.title('Occurrence of Stratospheric Aerosol Layers from CALIOP [Night]', fontsize=18)
#
# # Add colorbar with reference to the mesh
# cbar = plt.colorbar(mesh, extend='both', shrink=0.7)
# cbar.set_label('Ash Layer Occurrences', fontsize=16)  # Change the font size of the colorbar label
# cbar.ax.tick_params(labelsize=14)
# plt.tight_layout()
# plt.savefig(os.path.join(SAVE_FIGURE_PATH, 'Occurrence_over_Time_and_Latitude_2007_2018_night.png'), dpi=300)