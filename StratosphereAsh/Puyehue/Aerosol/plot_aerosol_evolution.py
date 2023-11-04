#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    plot_aerosol_evolution.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        04/11/2023 00:25

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

INPUT_PATH = './csv_ALay'
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

                try:
                    latitude = float(row[0])
                    alt_base = float(row[2])
                    alt_top = float(row[3])
                    depolarization = float(row[5])
                    aerosol_type = float(row[6])
                    CAD = float(row[7])
                    file_date = datetime.strptime(file.split('.')[1][0:10], '%Y-%m-%d')
                    aligned_date = align_to_interval(file_date, start_date)

                    if (SOUTHERN_LATITUDE <= latitude <= NORTHERN_LATITUDE) and (MIN_ALTITUDE <= alt_base <= MAX_ALTITUDE) and (MIN_ALTITUDE <= alt_top <= MAX_ALTITUDE) and (2. <= aerosol_type <= 4.) & (abs(CAD) > 40):
                        if -40 < latitude <= -20:
                            depolarization_data[aligned_date]['-20_to_-40'].append(depolarization)
                        elif -60 < latitude <= -40:
                            depolarization_data[aligned_date]['-40_to_-60'].append(depolarization)
                        elif -80 < latitude <= -60:
                            depolarization_data[aligned_date]['-60_to_-80'].append(depolarization)
                except:
                    pass

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
        if len(depolarization_data[date][lat_range]) > 10:  # Check if more than 10 data points are present
            mean_depol = np.mean(depolarization_data[date][lat_range])
            std_depol = np.std(depolarization_data[date][lat_range])
            plot_data[lat_range]['dates'].append(date)
            plot_data[lat_range]['means'].append(mean_depol)
            plot_data[lat_range]['stds'].append(std_depol)

# Convert datetime objects to the format Matplotlib expects for dates
for lat_range in plot_data:
    plot_data[lat_range]['dates'] = mdates.date2num(plot_data[lat_range]['dates'])

# ... [previous code remains unchanged]
# ... [previous code remains unchanged]

# Set up the figure and subplots
fig, axs = plt.subplots(3, 1, figsize=(16, 18))  # Changed to create a 3x1 subplot grid
fig.suptitle('2011 Puyehue: Stratospheric Aerosol Depolarization Ratio between 9 and 16 km', fontsize=20)  # Main title

colors = {'-20_to_-40': 'tab:blue', '-40_to_-60': 'tab:green', '-60_to_-80': 'tab:red'}

# Larger font size
font_size_title = 18  # Title font size
font_size_label = 18  # Label font size
font_size_ticks = 16  # Ticks font size
font_size_legend = 18  # Legend font size

for i, (lat_range, color) in enumerate(colors.items()):
    formatted_label = "Latitude: " + lat_range.replace("_to_", "$^{\circ}$S to ").replace("-", "") + "$^{\circ}$S"
    # Check if there is data to plot
    if len(plot_data[lat_range]['dates']) > 0:  # This ensures the array is not empty
        axs[i].errorbar(
            plot_data[lat_range]['dates'], plot_data[lat_range]['means'],
            yerr=plot_data[lat_range]['stds'],
            fmt='o', capsize=5, elinewidth=2, markeredgewidth=2,
            color=color, label='Depolarization Ratio', linestyle='none'
        )
    # Set x-axis limits to the specified range for each subplot
    axs[i].set_xlim([mdates.date2num(datetime(2011, 4, 1)), mdates.date2num(datetime(2011, 10, 1))])

    # Set x-ticks to the first day of each month for each subplot
    axs[i].xaxis.set_major_locator(mdates.MonthLocator(bymonthday=1))
    axs[i].xaxis.set_minor_locator(mdates.MonthLocator())

    # Formatting the date to make it readable for each subplot
    axs[i].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    axs[i].xaxis.set_minor_formatter(mdates.DateFormatter('%m-%d'))
    fig.autofmt_xdate()  # Rotate the dates
    axs[i].set_ylim(0, 0.8)

    axs[i].set_title(formatted_label, fontsize=font_size_title)
    axs[i].set_xlabel('Date', fontsize=font_size_label)
    axs[i].set_ylabel('Particulate Depolarization Ratio', fontsize=font_size_label)
    # axs[i].legend(loc='upper right', fontsize=font_size_legend)
    axs[i].tick_params(axis='both', which='major', labelsize=font_size_ticks)
    axs[i].tick_params(axis='both', which='minor', labelsize=font_size_ticks)

    axs[i].grid(True, linestyle='--')  # Set grid to dashed line

# Adjust the layout so there is no overlap, and the main title is properly spaced

plt.tight_layout(rect=[0, 0.03, 1, 0.97])
# Save the figure
plt.savefig(os.path.join(FIGURE_OUTPUT_PATH, 'aerosol_depolarization_over_time_subplot.png'))

