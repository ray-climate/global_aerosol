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
from collections import defaultdict
import matplotlib.ticker as ticker
import numpy as np
import csv
import os

NORTHERN_LATITUDE = -20
SOUTHERN_LATITUDE = -80
MIN_ALTITUDE = 9
MAX_ALTITUDE = 16.

INPUT_PATH = './csv_new'
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

# ... [the rest of your code above remains unchanged]

# Prepare data for plotting
plot_data = {
    '-20_to_-40': {'dates': [], 'means': [], 'stds': []},
    '-40_to_-60': {'dates': [], 'means': [], 'stds': []},
    '-60_to_-80': {'dates': [], 'means': [], 'stds': []}
}

# Calculate the mean and std for each period and latitude range
for date in sorted(depolarization_data.keys()):
    for lat_range in depolarization_data[date]:
        if depolarization_data[date][lat_range]:  # if the list is not empty
            mean_depol = np.mean(depolarization_data[date][lat_range])
            std_depol = np.std(depolarization_data[date][lat_range])
            plot_data[lat_range]['dates'].append(date)
            plot_data[lat_range]['means'].append(mean_depol)
            plot_data[lat_range]['stds'].append(std_depol)

# Convert datetime objects to the format Matplotlib expects for dates
for lat_range in plot_data:
    plot_data[lat_range]['dates'] = mdates.date2num(plot_data[lat_range]['dates'])

# Plotting
plt.figure(figsize=(16, 6))
colors = {'-20_to_-40': 'tab:blue', '-40_to_-60': 'tab:green', '-60_to_-80': 'tab:red'}

for lat_range, color in colors.items():
    # Format the label to include the degree symbol and superscript
    formatted_label = lat_range.replace("_to_", "$^{\circ}$S to ").replace("-", "") + "$^{\circ}$S"
    plt.errorbar(plot_data[lat_range]['dates'], plot_data[lat_range]['means'], yerr=plot_data[lat_range]['stds'],
                 marker='o', capsize=12, color=color, label=formatted_label)

# Set x-axis limits to the specified range
plt.xlim([datetime(2011, 4, 1), datetime(2011, 10, 1)])

# Set x-ticks to the first day of each month
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(bymonthday=1))
plt.gca().xaxis.set_minor_locator(mdates.MonthLocator())

# Formatting the date to make it readable
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.gca().xaxis.set_minor_formatter(mdates.DateFormatter('%m-%d'))
plt.gcf().autofmt_xdate()  # Rotate the dates
plt.ylim(0, 0.8)

plt.title('2011 Puyehue: Ice Clouds Depolarization Ratio between 9 and 16 km', fontsize=18)
plt.xlabel('Date', fontsize=18)
plt.ylabel('Particulate Depolarization Ratio', fontsize=18)
plt.legend(loc='upper right', fontsize=16)
plt.tick_params(axis='both', which='major', labelsize=16)
plt.tick_params(axis='both', which='minor', labelsize=16)

plt.grid(True, linestyle='--')  # Set grid to dashed line
plt.tight_layout()
plt.savefig(os.path.join(FIGURE_OUTPUT_PATH, 'ice_clouds_depolarization_over_time.png'))