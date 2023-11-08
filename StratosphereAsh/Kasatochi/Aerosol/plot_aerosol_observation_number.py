#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    plot_aerosol_observation_number.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        08/11/2023 14:46

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from datetime import datetime
from collections import defaultdict
import os
import csv

# Constants
NORTHERN_LATITUDE = 80
SOUTHERN_LATITUDE = 40
MIN_ALTITUDE = 9
MAX_ALTITUDE = 25

# Define date range for xlim
start_date = datetime(2008, 8, 1)
end_date = datetime(2008, 9, 1)

INPUT_PATH = './csv_ALay'
FIGURE_OUTPUT_PATH = './figures'

# Create the output directory if it does not exist
if not os.path.exists(FIGURE_OUTPUT_PATH):
    os.mkdir(FIGURE_OUTPUT_PATH)

# Dictionaries to hold the count of valid values for each latitude range
valid_depolarization_counts = {
    (80, 60): defaultdict(int),
    (60, 50): defaultdict(int),
    (50, 40): defaultdict(int)
}

cad_greater_than_40_counts = {
    (80, 60): defaultdict(int),
    (60, 50): defaultdict(int),
    (50, 40): defaultdict(int)
}

# Process files
for file in os.listdir(INPUT_PATH):
    if file.endswith('.csv'):
        with open(os.path.join(INPUT_PATH, file), 'r') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                try:
                    latitude = float(row[0])
                    alt_base = float(row[2])
                    alt_top = float(row[3])
                    depolarization = float(row[5])
                    aerosol_type = float(row[6])
                    CAD = float(row[7])
                    date = datetime.strptime(file.split('.')[1][0:10], '%Y-%m-%d')

                    if (SOUTHERN_LATITUDE <= latitude <= NORTHERN_LATITUDE) and (MIN_ALTITUDE <= alt_base <= MAX_ALTITUDE) and (MIN_ALTITUDE <= alt_top <= MAX_ALTITUDE) and (2. <= aerosol_type <= 4.):
                        for lat_range in valid_depolarization_counts:
                            if lat_range[0] >= latitude >= lat_range[1]:
                                if depolarization > 0:
                                    valid_depolarization_counts[lat_range][date] += 1
                                if abs(CAD) > 20:
                                    cad_greater_than_40_counts[lat_range][date] += 1
                                break
                except ValueError:
                    pass  # or you can print an error message or log the error


# Define the figure and subplots
fig, axs = plt.subplots(3, 1, figsize=(16, 18))  # Changed to create a 3x1 subplot grid
fig.suptitle('2015 Calbuco: Number of Stratospheric Aerosol Layers between 9 and 25 km', fontsize=20)  # Main title

# Larger font size
font_size_title = 18  # Title font size
font_size_label = 18  # Label font size
font_size_ticks = 16  # Ticks font size
font_size_legend = 18  # Legend font size

latitude_titles = ["Latitude: 20$^{\circ}$S to 30$^{\circ}$S", "Latitude: 30$^{\circ}$S to 40$^{\circ}$S", "Latitude: 40$^{\circ}$S to 50$^{\circ}$S"]

# Plot data for each latitude range
for i, lat_range in enumerate(valid_depolarization_counts):

    # Sort data by date for the latitude ranges
    depolarization_dates, depolarization_counts = zip(*sorted(valid_depolarization_counts[lat_range].items()))
    cad_dates, cad_counts = zip(*sorted(cad_greater_than_40_counts[lat_range].items()))

    # Plot depolarization data on the respective subplot
    axs[i].plot(depolarization_dates, depolarization_counts, marker='*', color='b',markersize=10, label='All', linestyle='none')

    # Plot CAD data on the same subplot
    axs[i].plot(cad_dates, cad_counts, marker='+', color='r',markersize=15, label='CAD > 20', linestyle='none')

    axs[i].set_xlim(start_date, end_date)
    axs[i].set_ylim(0, 1000)

    axs[i].xaxis.set_major_locator(mdates.MonthLocator(bymonthday=1))
    axs[i].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

    axs[i].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    axs[i].xaxis.set_minor_formatter(mdates.DateFormatter('%m-%d'))
    fig.autofmt_xdate()  # Rotate the dates

    axs[i].set_xlabel('Date', fontsize=font_size_label)
    axs[i].set_ylabel("Number of Layers", fontsize=font_size_label)
    # axs[i].legend(loc='upper right', fontsize=font_size_legend)
    axs[i].tick_params(axis='both', which='major', labelsize=font_size_ticks)
    axs[i].tick_params(axis='both', which='minor', labelsize=font_size_ticks)
    axs[i].legend(loc='upper right', fontsize=font_size_legend)

    axs[i].set_title(latitude_titles[i], fontsize=font_size_title)
    axs[i].grid(True, linestyle='--')  # Set grid to dashed line


plt.tight_layout(rect=[0, 0.03, 1, 0.97])

# Save the figure
plt.savefig(os.path.join(FIGURE_OUTPUT_PATH, 'valid_depolarization_values_by_latitude.png'))
