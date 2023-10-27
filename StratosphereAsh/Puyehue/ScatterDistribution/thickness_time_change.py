#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    thickness_time_change.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        27/10/2023 22:14

from collections import defaultdict
import matplotlib.pyplot as plt
from datetime import datetime
import seaborn as sns
import numpy as np
import pandas as pd
import argparse
import os

NORTHERN_LATITUDE = -30.
SOUTHERN_LATITUDE = -80.

INPUT_DIR = './csv'
FIG_DIR = './plots_time'

try:
    os.stat(FIG_DIR)
except:
    os.mkdir(FIG_DIR)

dates_all = []
lats_all = []
thickness_all = []

for file in os.listdir(INPUT_DIR):
    if file.endswith('.csv'):
        print('Reading file: %s' % file)

        # derive dates from file name
        date = file.split('.')[1][0:10]

        with open(INPUT_DIR + '/' + file, 'r') as f:
            lines = f.readlines()
            for line in lines[1:]:
                try:
                    if (float(line.split(',')[4]) > 0) &(float(line.split(',')[5]) > 0) & (float(line.split(',')[6]) >= 2.) & (float(line.split(',')[6]) <= 4.):
                        dates_all.append(date)
                        lats_all.append(float(line.split(',')[0]))
                        thickness_all.append(float(line.split(',')[3]) - float(line.split(',')[2]))
                except:
                    continue

# Bucket the latitudes into 2-degree intervals
def get_latitude_bucket(lat):
    for i in range(-80, -28, 2):
        if i <= lat < i+2:
            return f"{i} to {i+2}"
    return None

# We'll store both the counts and the sum of thicknesses in this dictionary
latitude_data_per_date = defaultdict(lambda: defaultdict(lambda: {'count': 0, 'thickness_sum': 0}))

for date, lat, thickness in zip(dates_all, lats_all, thickness_all):
    if -80 <= lat <= -30:
        bucket = get_latitude_bucket(lat)
        latitude_data_per_date[date][bucket]['count'] += 1
        latitude_data_per_date[date][bucket]['thickness_sum'] += thickness

# Display the average thickness
for date, data in latitude_data_per_date.items():
    print(f"For date {date}:")
    for lat_range, values in sorted(data.items()):
        average_thickness = values['thickness_sum'] / values['count'] if values['count'] else 0
        print(f"Latitude range {lat_range}: Average thickness = {average_thickness:.2f}")
    print("----")


# Create a 2D matrix to store average thickness values
unique_dates = sorted(list(set(dates_all)))
lat_ranges = [i for i in range(-80, -28, 2)]

thickness_matrix = np.zeros((len(unique_dates), len(lat_ranges)))

for date_idx, date in enumerate(unique_dates):
    for lat_idx, lat_start in enumerate(lat_ranges):
        lat_range = f"{lat_start} to {lat_start+2}"
        values = latitude_data_per_date[date].get(lat_range, None)
        if values:
            average_thickness = values['thickness_sum'] / values['count'] if values['count'] else 0
            thickness_matrix[date_idx, lat_idx] = average_thickness

# Replace 0 with nan for proper colormap visualization
thickness_matrix[thickness_matrix == 0] = np.nan

# Transpose the matrix for plotting with dates on x-axis
thickness_matrix_T = thickness_matrix.T

# Modify the colormap
colormap = plt.cm.RdYlBu_r  # or any other colormap you like
colormap.set_bad(color='white')

# Plotting
plt.figure(figsize=(25, 10))
X, Y = np.meshgrid(np.arange(thickness_matrix_T.shape[1] + 1), np.arange(thickness_matrix_T.shape[0] + 1))
plt.pcolormesh(X, Y, thickness_matrix_T, cmap=colormap, shading='auto', vmin=1., vmax=3.)

cbar = plt.colorbar(label='Average Thickness', fraction=0.046, pad=0.04, shrink=0.6, extend='both')
cbar.ax.tick_params(labelsize=20)
cbar.set_label('Average Thickness', size=25)

# Selecting 10 evenly spaced ticks for x and y axis
y_ticks = np.linspace(0.5, len(lat_ranges) - 0.5, 10)
y_ticklabels = [lat_ranges[int(i)] for i in y_ticks]
plt.yticks(y_ticks, y_ticklabels, fontsize=25)

x_ticks = np.linspace(0.5, len(unique_dates) - 0.5, 10)
x_ticklabels = [unique_dates[int(i)] for i in x_ticks]
plt.xticks(x_ticks, x_ticklabels, rotation=45, fontsize=25)

plt.ylabel('Latitude [$^\circ$]', fontsize=28)
plt.xlabel('Date', fontsize=28)
plt.title('Average Thickness of Stratospheric Aerosols', fontsize=28)
plt.tight_layout()
plt.savefig(FIG_DIR + '/aerosol_thickness_time.png')


