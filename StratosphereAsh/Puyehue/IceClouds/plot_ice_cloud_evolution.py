#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    plot_ice_cloud_evolution.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        03/11/2023 11:56

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from matplotlib.patches import Patch
import numpy as np
import csv
import os
from collections import defaultdict

NORTHERN_LATITUDE = -20
SOUTHERN_LATITUDE = -80
MIN_ALTITUDE = 9
MAX_ALTITUDE = 16.

INPUT_PATH = './csv'
FIGURE_OUTPUT_PATH = './figures'

# Create csv saving directory if not present
if not os.path.exists(FIGURE_OUTPUT_PATH):
    os.mkdir(FIGURE_OUTPUT_PATH)

# Function to align dates to the nearest five-day interval start date
def align_to_interval(date, interval_start, days=5):
    days_since_start = (date - interval_start).days
    aligned_date = interval_start + timedelta(days=(days_since_start // days) * days)
    return aligned_date

# Initialize dictionary to hold depolarization data
depolarization_data = defaultdict(lambda: {'-20_to_-40': [], '-40_to_-60': [], '-60_to_-80': []})

# Define the date range for every five days
start_date = datetime(2011, 4, 1)
end_date = datetime(2011, 9, 30)

for file in os.listdir(INPUT_PATH):
    if file.endswith('.csv'):
        with open(os.path.join(INPUT_PATH, file), 'r') as f:
            reader = csv.reader(f)
            next(reader)  # Skip the header
            for row in reader:
                latitude = float(row[0])
                altitude = float(row[2])
                depolarization = float(row[3])
                file_date = datetime.strptime(file.split('.')[1][0:10], '%Y-%m-%d')
                aligned_date = align_to_interval(file_date, start_date)

                if SOUTHERN_LATITUDE <= latitude <= NORTHERN_LATITUDE and MIN_ALTITUDE <= altitude <= MAX_ALTITUDE:
                    if -40 < latitude <= -20:
                        depolarization_data[aligned_date]['-20_to_-40'].append(depolarization)
                    elif -60 < latitude <= -40:
                        depolarization_data[aligned_date]['-40_to_-60'].append(depolarization)
                    elif -80 < latitude <= -60:
                        depolarization_data[aligned_date]['-60_to_-80'].append(depolarization)

plot_data = {key: [] for key in depolarization_data[list(depolarization_data.keys())[0]].keys()}
dates = sorted(depolarization_data.keys())

for date in dates:
    for lat_range in plot_data.keys():
        plot_data[lat_range].append(depolarization_data[date][lat_range])

fig, ax = plt.subplots(figsize=(12, 5))

positions = range(len(dates))
boxplots = []

for i, (lat_range, color) in enumerate({'-20_to_-40': 'blue', '-40_to_-60': 'green', '-60_to_-80': 'purple'}.items()):
    bp = ax.boxplot(plot_data[lat_range], positions=np.array(positions) + i*0.2, widths=0.15, patch_artist=True, boxprops=dict(facecolor=color))
    boxplots.append(bp)

# Formatting dates for x-axis
ax.xaxis.set_major_locator(mdates.DayLocator(interval=(len(dates) // 10)))  # Show only 10 dates
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.xticks(rotation=45)

# Setting x-axis limits to frame our boxplot groups
ax.set_xlim(-0.5, len(dates) - 0.5)
ax.set_ylim(0., 0.8)
# Set the background grid to dashed line
ax.yaxis.grid(True, linestyle='--', which='major', color='grey', alpha=0.5)

# Legend
# Define the labels and colors in the same order as the boxplots were created
latitude_ranges = ['-20_to_-40', '-40_to_-60', '-60_to_-80']
colors = ['tab:blue', 'tab:green', 'tab:red']  # the colors used in the boxplots
labels = ['-20$^{\circ}$ to -40$^{\circ}$', '-40$^{\circ}$ to -60$^{\circ}$', '-60$^{\circ}$ to -80$^{\circ}$']

# Create a list of patch objects to be used as handles in the legend
legend_handles = [Patch(facecolor=color, label=label) for label, color in zip(labels, colors)]

# Create the legend on the plot
plt.legend(handles=legend_handles, loc='upper right', fontsize=16)

plt.title('2011 Puyehue: Ice Clouds Depolarization Ratio between 9 and 16 km', fontsize=18)
plt.xlabel('Date', fontsize=18)
plt.ylabel('Particulate Depolarization Ratio', fontsize=18)

# set tick label size
ax.tick_params(axis='both', which='major', labelsize=16)
ax.tick_params(axis='both', which='minor', labelsize=16)
plt.tight_layout()
plt.savefig(os.path.join(FIGURE_OUTPUT_PATH, 'ice_clouds_depolarization_over_time_boxplot.png'))
