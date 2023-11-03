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


# Convert datetime objects to the format Matplotlib expects for dates
for lat_range in plot_data:
    plot_data[lat_range]['dates'] = mdates.date2num(plot_data[lat_range]['dates'])

# Create a 3x1 subplot figure
fig, axs = plt.subplots(3, 1, figsize=(16, 18), sharex=True)

# Set colors for each latitude range
colors = {
    '-20_to_-40': 'tab:blue',
    '-40_to_-60': 'tab:green',
    '-60_to_-80': 'tab:red'
}

# Loop over each latitude range and plot in a separate subplot
for i, lat_range in enumerate(colors.keys()):
    ax = axs[i]

    # Format the label to include the degree symbol and remove negative sign
    formatted_label = lat_range.replace("_to_", "$^{\circ}$S to ").replace("-", "") + "$^{\circ}$S"

    # Plot data
    ax.errorbar(plot_data[lat_range]['dates'], plot_data[lat_range]['means'],
                yerr=plot_data[lat_range]['stds'],
                fmt='o', capsize=5, elinewidth=2, markeredgewidth=2,
                color=colors[lat_range], label=formatted_label, linestyle='none')

    # Set the title for each subplot with the corresponding latitude range label
    ax.set_title(f'Ice Clouds Depolarization Ratio {formatted_label} between 9 and 16 km', fontsize=14)

    # Formatting the date for each subplot to make it readable
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonthday=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

    # Set the same x and y axis limits
    ax.set_xlim([datetime(2011, 4, 1), datetime(2011, 10, 1)])
    ax.set_ylim(0, 0.8)

    ax.grid(True, linestyle='--')
    ax.legend(loc='upper right', fontsize=12)
    ax.tick_params(axis='both', which='major', labelsize=12)

# Set common labels
plt.xlabel('Date', fontsize=18)
fig.text(0.04, 0.5, 'Particulate Depolarization Ratio', va='center', rotation='vertical', fontsize=18)

# Rotate date labels for the bottom subplot
plt.setp(axs[-1].get_xticklabels(), rotation=45, ha="right")

plt.tight_layout()
plt.savefig(os.path.join(FIGURE_OUTPUT_PATH, 'ice_clouds_depolarization_over_time.png'))