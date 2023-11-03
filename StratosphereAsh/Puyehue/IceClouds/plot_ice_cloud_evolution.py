#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    plot_ice_cloud_evolution.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        03/11/2023 11:56

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
import os

NORTHERN_LATITUDE = -20
SOUTHERN_LATITUDE = -80
MIN_ALTITUDE = 9
MAX_ALTITUDE = 16.

INPUT_PATH = './csv'
FIGURE_OUTPUT_PATH = './figures'

# Create csv saving directory if not present
if not os.path.exists(FIGURE_OUTPUT_PATH):
    os.mkdir(FIGURE_OUTPUT_PATH)

date = []
depolarization = []
depolarization_std = []

for file in os.listdir(INPUT_PATH):
    if file.endswith('.csv'):

        date_i = []
        latitude_i = []
        longitude_i = []
        altitude_i = []
        depolarization_i = []
        depolarization_std_i = []

        file_path = os.path.join(INPUT_PATH, file)
        print('Reading file: {}'.format(file_path))
        # skip the first row and read the data
        with open(file_path, 'r') as f:
            for line in f.readlines()[1:]:
                line = line.split(',')
                latitude_i.append(float(line[0]))
                longitude_i.append(float(line[1]))
                altitude_i.append(float(line[2]))
                depolarization_i.append(float(line[3]))

        # convert to numpy array
        latitude_i = np.array(latitude_i)
        longitude_i = np.array(longitude_i)
        altitude_i = np.array(altitude_i)
        depolarization_i = np.array(depolarization_i)

        # select the data within the range
        latitude_i_filter = latitude_i[(latitude_i >= SOUTHERN_LATITUDE) & (latitude_i <= NORTHERN_LATITUDE) & (altitude_i >= MIN_ALTITUDE) & (altitude_i <= MAX_ALTITUDE)]
        longitude_i_filter = longitude_i[(latitude_i >= SOUTHERN_LATITUDE) & (latitude_i <= NORTHERN_LATITUDE) & (altitude_i >= MIN_ALTITUDE) & (altitude_i <= MAX_ALTITUDE)]
        altitude_i_filter = altitude_i[(latitude_i >= SOUTHERN_LATITUDE) & (latitude_i <= NORTHERN_LATITUDE) & (altitude_i >= MIN_ALTITUDE) & (altitude_i <= MAX_ALTITUDE)]
        depolarization_i_filter = depolarization_i[(latitude_i >= SOUTHERN_LATITUDE) & (latitude_i <= NORTHERN_LATITUDE) & (altitude_i >= MIN_ALTITUDE) & (altitude_i <= MAX_ALTITUDE)]

        if np.size(latitude_i_filter) < 1:
            continue

        date_i = file.split('.')[1][0:10]
        date.append(date_i)
        depolarization.append(np.mean(depolarization_i_filter))
        depolarization_std.append(np.std(depolarization_i_filter))

        print('Date: {}, depolarization: {}, depolarization_std: {}'.format(date_i, np.mean(depolarization_i_filter), np.std(depolarization_i_filter)))

# plot the depolraization with std over the date

# Convert string dates to datetime objects
date_objects = [datetime.strptime(d, '%Y-%m-%d') for d in date]

# Sort the data by date
sorted_indices = np.argsort(date_objects)
sorted_dates = np.array(date_objects)[sorted_indices]
sorted_depolarization = np.array(depolarization)[sorted_indices]
sorted_depolarization_std = np.array(depolarization_std)[sorted_indices]

# Plotting
plt.figure(figsize=(12, 5))

# Plot the mean depolarization
plt.errorbar(sorted_dates, sorted_depolarization, yerr=sorted_depolarization_std, fmt='*', color='red')

# Formatting the date to make it readable
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=10))  # Adjust interval to suit your data
plt.gcf().autofmt_xdate()  # Rotation

plt.title('Depolarization Over Time')
plt.xlabel('Date')
plt.ylabel('Depolarization (mean ± std)')
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(FIGURE_OUTPUT_PATH, 'ice_clouds_depolarization_over_time.png'))






