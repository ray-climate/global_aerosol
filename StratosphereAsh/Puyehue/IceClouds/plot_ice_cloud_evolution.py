#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    plot_ice_cloud_evolution.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        03/11/2023 11:56

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
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
                file_date = datetime.strptime(row[1], '%Y-%m-%d')  # Assuming the date is in the second column
                aligned_date = align_to_interval(file_date, start_date)

                if SOUTHERN_LATITUDE <= latitude <= NORTHERN_LATITUDE and MIN_ALTITUDE <= altitude <= MAX_ALTITUDE:
                    if -40 < latitude <= -20:
                        depolarization_data[aligned_date]['-20_to_-40'].append(depolarization)
                    elif -60 < latitude <= -40:
                        depolarization_data[aligned_date]['-40_to_-60'].append(depolarization)
                    elif -80 < latitude <= -60:
                        depolarization_data[aligned_date]['-60_to_-80'].append(depolarization)

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

# Plotting
plt.figure(figsize=(12, 5))
colors = {'-20_to_-40': 'blue', '-40_to_-60': 'green', '-60_to_-80': 'purple'}

for lat_range, color in colors.items():
    plt.errorbar(plot_data[lat_range]['dates'], plot_data[lat_range]['means'], yerr=plot_data[lat_range]['stds'],
                 fmt='o', color=color, label=f'Latitude {lat_range.replace("_to_", " to ")}')

# Formatting the date to make it readable
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=5))  # Set interval to 5 days
plt.gcf().autofmt_xdate()  # Rotation

plt.title('Depolarization Over Time')
plt.xlabel('Date')
plt.ylabel('Depolarization (mean ± std)')
plt.legend(title='Latitude Range')
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(FIGURE_OUTPUT_PATH, 'ice_clouds_depolarization_over_time.png'))
