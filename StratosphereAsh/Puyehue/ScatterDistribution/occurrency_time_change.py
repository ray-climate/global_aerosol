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
lat_ranges = [i for i in range(-80, -28, 2)]  # Adjusted to store just the starting values of each range

counts_matrix = np.zeros((len(unique_dates), len(lat_ranges)))

for date_idx, date in enumerate(unique_dates):
    for lat_idx, lat_start in enumerate(lat_ranges):  # Adjusted variable name
        lat_range = f"{lat_start} to {lat_start+2}"
        counts_matrix[date_idx, lat_idx] = latitude_count_per_date[date].get(lat_range, 0)

# Transpose the matrix for plotting with dates on x-axis
counts_matrix_T = counts_matrix.T

# Plotting
plt.figure(figsize=(25, 10))
plt.imshow(counts_matrix_T, cmap='jet', aspect='auto', origin='lower')
plt.colorbar(label='Occurrences', fraction=0.046, pad=0.04)
plt.yticks(np.arange(len(lat_ranges)), lat_ranges)  # Displaying the starting value of each range
plt.xticks(np.arange(len(unique_dates)), unique_dates, rotation=45)
plt.xticks(fontsize=20)
plt.yticks(fontsize=20)
plt.ylabel('Latitude', fontsize=25)
plt.xlabel('Date', fontsize=25)
plt.title('Occurrences of Stratospheric Aerosols ')
plt.tight_layout()
plt.savefig(FIG_DIR + '/aerosol_occurrence_time.png')





