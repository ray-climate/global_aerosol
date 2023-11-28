#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    plot_global_ash.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        28/11/2023 10:48

import csv
import sys
import logging
import argparse
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from matplotlib.gridspec import GridSpec

# Append the custom path to system path
sys.path.append('../../')
from getColocationData.get_caliop import *

ASH_LAYER_DATA_PATH = './ash_Layer_csv'
SAVE_FIGURE_PATH = './ash_Layer_figures'

# Create csv saving directory if not present
if not os.path.exists(SAVE_FIGURE_PATH):
    os.mkdir(SAVE_FIGURE_PATH)

# write a function to read through the csv files and extract the following parameters:
# caliop_lat, caliop_lon, caliop_Layer_Base, caliop_Layer_Top, caliop_Tropopause_Altitude, caliop_aerosol_type, caliop_CAD

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
        for row in reader:
            try:
                if (float(row[8]) == 2) & (float(row[9]) <= -20.):

                    caliop_Profile_Time.append(row[0])
                    caliop_lat.append(float(row[1]))
                    caliop_lon.append(float(row[2]))
                    caliop_Layer_Base.append(float(row[3]))
                    caliop_Layer_Top.append(float(row[4]))
                    caliop_Tropopause_Altitude.append(float(row[5]))
                    caliop_aerosol_type.append(float(row[8]))
                    caliop_CAD.append(float(row[9]))
            except:
                continue

    return caliop_Profile_Time, caliop_lat, caliop_lon, caliop_Layer_Base, caliop_Layer_Top, caliop_Tropopause_Altitude, caliop_aerosol_type, caliop_CAD

# Initialize lists to store data from all files
all_caliop_Profile_Time = []
all_caliop_lat = []
all_caliop_lon = []
all_caliop_Layer_Base = []
all_caliop_Layer_Top = []
all_caliop_Tropopause_Altitude = []
all_caliop_aerosol_type = []
all_caliop_CAD = []

# Iterate over all CSV files in the directory
for file in os.listdir(ASH_LAYER_DATA_PATH):
    if file.endswith(".csv") & file.__contains__('2011'):
        ash_layer_csv_file = os.path.join(ASH_LAYER_DATA_PATH, file)
        caliop_Profile_Time, caliop_lat, caliop_lon, caliop_Layer_Base, caliop_Layer_Top, caliop_Tropopause_Altitude, caliop_aerosol_type, caliop_CAD = read_ash_layer_csv(ash_layer_csv_file)

        # Append data from this file to the collective lists
        all_caliop_Profile_Time.extend(caliop_Profile_Time)
        all_caliop_lat.extend(caliop_lat)
        all_caliop_lon.extend(caliop_lon)
        all_caliop_Layer_Base.extend(caliop_Layer_Base)
        all_caliop_Layer_Top.extend(caliop_Layer_Top)
        all_caliop_Tropopause_Altitude.extend(caliop_Tropopause_Altitude)
        all_caliop_aerosol_type.extend(caliop_aerosol_type)
        all_caliop_CAD.extend(caliop_CAD)

        print('Processed file: ', ash_layer_csv_file)


# Step 1: Convert all_caliop_Profile_Time to datetime objects
caliop_times = [datetime.strptime(time, '%Y-%m-%d %H:%M:%S.%f') for time in all_caliop_Profile_Time]

# Define start and end times
start_time = datetime(2007, 1, 1)
end_time = datetime(2018, 12, 31)

# Calculate the number of 10-day intervals between start_time and end_time
num_intervals = (end_time - start_time).days // 10 + 1

# Define the bins for time and latitude
time_bins = mdates.date2num([start_time + timedelta(days=10*i) for i in range(num_intervals)])
lat_bins = np.arange(min(all_caliop_lat), max(all_caliop_lat) + 1, 1)

# Create a 2D histogram
hist, xedges, yedges = np.histogram2d(mdates.date2num(caliop_times), all_caliop_lat, bins=[time_bins, lat_bins])

# Plot
fig, ax = plt.subplots(figsize=(10, 6))
X, Y = np.meshgrid(xedges, yedges)
ax.pcolormesh(X, Y, hist.T, shading='auto')

# Format the time axis
ax.xaxis_date()
date_format = mdates.DateFormatter('%Y-%m-%d')
ax.xaxis.set_major_formatter(date_format)
plt.xticks(rotation=45)

plt.xlabel('Time')
plt.ylabel('Latitude')
plt.title('Occurrence over Time and Latitude (2007-2018)')
plt.colorbar(label='Number of Occurrences')
plt.savefig(os.path.join(SAVE_FIGURE_PATH, 'Occurrence_over_Time_and_Latitude_2007_2018.png'), dpi=300)