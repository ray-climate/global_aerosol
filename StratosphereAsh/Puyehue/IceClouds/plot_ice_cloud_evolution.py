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

NORTHERN_LATITUDE = -20
SOUTHERN_LATITUDE = -80
MIN_ALTITUDE = 9
MAX_ALTITUDE = 16.

INPUT_PATH = './csv'
FIGURE_OUTPUT_PATH = './figures'

# Create csv saving directory if not present
if not os.path.exists(FIGURE_OUTPUT_PATH):
    os.mkdir(FIGURE_OUTPUT_PATH)

# Initialize dictionary to hold depolarization data
depolarization_data = {}

# Define the date range for every five days
start_date = datetime(2011, 4, 1)
end_date = datetime(2011, 9, 30)
current_date = start_date

while current_date <= end_date:
    depolarization_data[current_date] = {'-20_to_-40': [], '-40_to_-60': [], '-60_to_-80': []}
    current_date += timedelta(days=5)
print(depolarization_data)
quit()
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

                if file_date in depolarization_data and SOUTHERN_LATITUDE <= latitude <= NORTHERN_LATITUDE and MIN_ALTITUDE <= altitude <= MAX_ALTITUDE:
                    if -40 < latitude <= -20:
                        depolarization_data[file_date]['-20_to_-40'].append(depolarization)
                    elif -60 < latitude <= -40:
                        depolarization_data[file_date]['-40_to_-60'].append(depolarization)
                    elif -80 < latitude <= -60:
                        depolarization_data[file_date]['-60_to_-80'].append(depolarization)

# Plotting
plt.figure(figsize=(12, 5))

for date, data in depolarization_data.items():
    for lat_range, depol_list in data.items():
        if depol_list:  # if the list is not empty
            mean_depol = np.mean(depol_list)
            std_depol = np.std(depol_list)
            color = ''
            if lat_range == '-20_to_-40':
                color = 'blue'
            elif lat_range == '-40_to_-60':
                color = 'green'
            elif lat_range == '-60_to_-80':
                color = 'purple'

            plt.errorbar(date, mean_depol, yerr=std_depol, fmt='o', color=color, label=lat_range if date == start_date else "")

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
