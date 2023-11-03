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
import csv
import os

latitude_bands = [(-40, -20), (-60, -40), (-80, -60)]

MIN_ALTITUDE = 9
MAX_ALTITUDE = 16.

INPUT_PATH = './csv'
OUTPUT_PATH = './output'
FIGURE_OUTPUT_PATH = './figures'

# Create output saving directory if not present
if not os.path.exists(OUTPUT_PATH):
    os.mkdir(OUTPUT_PATH)

# Create csv saving directory if not present
if not os.path.exists(FIGURE_OUTPUT_PATH):
    os.mkdir(FIGURE_OUTPUT_PATH)

# A dictionary to hold data for each latitude range
data_by_latitude = {band: {'dates': [], 'means': [], 'std_devs': []} for band in latitude_bands}

for file in os.listdir(INPUT_PATH):
    if file.endswith('.csv'):
        file_path = os.path.join(INPUT_PATH, file)
        print('Reading file: {}'.format(file_path))
        with open(file_path, 'r') as f:
            lines = f.readlines()[1:]
            latitudes = np.array([float(line.split(',')[0]) for line in lines])
            altitudes = np.array([float(line.split(',')[2]) for line in lines])
            depolarizations = np.array([float(line.split(',')[3]) for line in lines])

        for band in latitude_bands:
            # Filter data within each latitude band and altitude range
            mask = (latitudes >= band[0]) & (latitudes < band[1]) & (altitudes >= MIN_ALTITUDE) & (
                        altitudes <= MAX_ALTITUDE)
            filtered_depolarizations = depolarizations[mask]

            if len(filtered_depolarizations) > 0:
                date_str = file.split('.')[1][0:10]
                mean_depol = np.mean(filtered_depolarizations)
                std_depol = np.std(filtered_depolarizations)
                data_by_latitude[band]['dates'].append(date_str)
                data_by_latitude[band]['means'].append(mean_depol)
                data_by_latitude[band]['std_devs'].append(std_depol)
                print('Date: {}, Latitude Range: {}, Mean Depolarization: {}, Std Dev: {}'.format(date_str, band,
                                                                                                  mean_depol,
                                                                                                  std_depol))

# Write to CSV files
for band in latitude_bands:
    output_file_path = os.path.join(OUTPUT_PATH, 'depolarization_summary_{}_to_{}.csv'.format(band[1], band[0]))
    with open(output_file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write the header
        writer.writerow(['Date', 'Depolarization Mean', 'Depolarization Std'])
        # Write the data
        for i in range(len(data_by_latitude[band]['dates'])):
            writer.writerow([
                data_by_latitude[band]['dates'][i],
                data_by_latitude[band]['means'][i],
                data_by_latitude[band]['std_devs'][i]
            ])
    print(f'Data saved to {output_file_path}')







