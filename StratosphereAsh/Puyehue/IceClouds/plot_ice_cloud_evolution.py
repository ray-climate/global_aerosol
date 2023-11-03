#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    plot_ice_cloud_evolution.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        03/11/2023 11:56

from datetime import datetime, timedelta
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import csv
import os

# Constants for altitude ranges
ALTITUDE_RANGES = {
    'range1': (-20, -40),
    'range2': (-40, -60),
    'range3': (-60, -80)
}

INPUT_PATH = './csv'
FIGURE_OUTPUT_PATH = './figures'

# Create figures directory if not present
if not os.path.exists(FIGURE_OUTPUT_PATH):
    os.makedirs(FIGURE_OUTPUT_PATH)

# Initialize a dictionary to hold data for different altitude ranges
data_by_altitude = {key: {'dates': [], 'depolarization': [], 'depolarization_std': []} for key in ALTITUDE_RANGES}

# Read data from files and organize it by date and altitude range
start_date = datetime(2011, 4, 1)
end_date = datetime(2011, 9, 30)

current_date = start_date

while current_date <= end_date:
    for file in os.listdir(INPUT_PATH):
        if file.endswith('.csv') and current_date.strftime('%Y-%m-%d') in file:
            with open(os.path.join(INPUT_PATH, file), 'r') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  # skip the header

                for row in reader:
                    latitude, altitude, depolarization = float(row[0]), float(row[2]), float(row[3])

                    # Check which altitude range the current row belongs to
                    for key, (min_alt, max_alt) in ALTITUDE_RANGES.items():
                        if min_alt <= latitude < max_alt:
                            data_by_altitude[key]['dates'].append(current_date)
                            data_by_altitude[key]['depolarization'].append(depolarization)

    # Increase current_date by 5 days
    current_date += timedelta(days=5)

# Process data to calculate the mean and std for each altitude range
for altitude_range, data in data_by_altitude.items():
    # Only continue if there are data points
    if data['dates']:
        # Convert lists to numpy arrays for vectorized operations
        depolarization = np.array(data['depolarization'])

        # Calculate mean and std for the 5-day period
        data['depolarization_mean'] = np.mean(depolarization)
        data['depolarization_std'] = np.std(depolarization)
        # Ensure that dates are datetime objects and not strings
        data['dates'] = [datetime.strptime(date_str, '%Y-%m-%d') for date_str in data['dates']]
    else:
        data['depolarization_mean'] = None
        data['depolarization_std'] = None

# Debug: Print out the dates to ensure they are correct
for altitude_range, data in data_by_altitude.items():
    print(f"Dates for {altitude_range}: {data['dates']}")

# Plotting
plt.figure(figsize=(12, 5))

# Colors for the different altitude ranges
colors = ['green', 'blue', 'purple']

# Plot the mean depolarization with std for each altitude range
for (altitude_range, data), color in zip(data_by_altitude.items(), colors):
    if data['depolarization_mean'] is not None:
        plt.errorbar(data['dates'], data['depolarization_mean'], yerr=data['depolarization_std'], fmt='o', color=color, label=f'Altitude {ALTITUDE_RANGES[altitude_range][0]} to {ALTITUDE_RANGES[altitude_range][1]}')

# Formatting the date to make it readable
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=5))
plt.gcf().autofmt_xdate()  # Rotation

plt.title('Depolarization Over Time by Altitude Range')
plt.xlabel('Date')
plt.ylabel('Depolarization (mean ± std)')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(FIGURE_OUTPUT_PATH, 'ice_clouds_depolarization_by_altitude.png'))
plt.show()





