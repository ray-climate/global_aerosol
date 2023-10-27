#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    occurrency_time_change.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        27/10/2023 21:07

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
                except:
                    continue

# Bucket the latitudes into 2-degree intervals
def get_latitude_bucket(lat):
    for i in range(-80, -28, 2):  # goes up to -28 to ensure -30 is included in the last bucket
        if i <= lat < i+2:
            return f"{i} to {i+2}"
    return None

latitude_count_per_date = defaultdict(lambda: defaultdict(int))

for date, lat in zip(dates_all, lats_all):
    if -80 <= lat <= -30:
        bucket = get_latitude_bucket(lat)
        latitude_count_per_date[date][bucket] += 1

# Display the counts
for date, counts in latitude_count_per_date.items():
    print(f"For date {date}:")
    for lat_range, count in sorted(counts.items()):
        print(f"Latitude range {lat_range}: {count} occurrences")
    print("----")

# Create a 2D matrix to store counts
unique_dates = sorted(list(set(dates_all)))
lat_ranges = [i for i in range(-80, -28, 2)]

counts_matrix = np.zeros((len(unique_dates), len(lat_ranges)))

for date_idx, date in enumerate(unique_dates):
    for lat_idx, lat_start in enumerate(lat_ranges):
        lat_range = f"{lat_start} to {lat_start+2}"
        counts_matrix[date_idx, lat_idx] = latitude_count_per_date[date].get(lat_range, 0)

# Replace 0 with nan for proper colormap visualization
counts_matrix[counts_matrix == 0] = np.nan

# Transpose the matrix for plotting with dates on x-axis
counts_matrix_T = counts_matrix.T

# Modify the colormap
colormap = plt.cm.RdYlBu_r  # or any other colormap you like
colormap.set_bad(color='white')

# Plotting
plt.figure(figsize=(25, 10))
X, Y = np.meshgrid(np.arange(counts_matrix_T.shape[1] + 1), np.arange(counts_matrix_T.shape[0] + 1))
plt.pcolormesh(X, Y, counts_matrix_T, cmap=colormap, shading='auto')

cbar = plt.colorbar(label='Occurrences', fraction=0.046, pad=0.04, shrink=0.6)
cbar.ax.tick_params(labelsize=20)
cbar.set_label('Occurrences', size=25)

# Selecting 10 evenly spaced ticks for x and y axis
y_ticks = np.linspace(0.5, len(lat_ranges) - 0.5, 10)
y_ticklabels = [lat_ranges[int(i)] for i in y_ticks]
plt.yticks(y_ticks, y_ticklabels, fontsize=25)

x_ticks = np.linspace(0.5, len(unique_dates) - 0.5, 10)
x_ticklabels = [unique_dates[int(i)] for i in x_ticks]
plt.xticks(x_ticks, x_ticklabels, rotation=45, fontsize=25)

plt.ylabel('Latitude [$^\circ$]', fontsize=28)
plt.xlabel('Date', fontsize=28)
plt.title('Occurrences of Stratospheric Aerosols', fontsize=28)
plt.tight_layout()
plt.savefig(FIG_DIR + '/aerosol_occurrence_time.png')




