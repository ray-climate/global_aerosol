#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    plot_aerosol_height_thickness_time.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        07/11/2023 10:27

from datetime import datetime, timedelta
from collections import defaultdict
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import os
import csv

# Constants
NORTHERN_LATITUDE = -20
SOUTHERN_LATITUDE = -40
MIN_ALTITUDE = 9
MAX_ALTITUDE = 16.

# Define the reference date
reference_date = datetime(2011, 6, 4)

# Paths
INPUT_PATH = './csv_ALay'
FIGURE_OUTPUT_PATH = './figures'

# Create output directory if not present
if not os.path.exists(FIGURE_OUTPUT_PATH):
    os.makedirs(FIGURE_OUTPUT_PATH)

# Function to align dates to the nearest five-day interval start date
def align_to_interval(date, interval_start, days=3):
    days_since_start = (date - interval_start).days
    aligned_date = interval_start + timedelta(days=(days_since_start // days) * days)
    return aligned_date

# Initialize dictionary to hold aerosol layer data
aerosol_layer_data = defaultdict(list)

# Define the date range for every five days
start_date = datetime(2011, 6, 1)
end_date = datetime(2011, 8, 30)

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

                    # Check latitude and altitude ranges, aerosol type, and CAD
                    if SOUTHERN_LATITUDE <= latitude < NORTHERN_LATITUDE and MIN_ALTITUDE <= alt_base <= MAX_ALTITUDE and MIN_ALTITUDE <= alt_top <= MAX_ALTITUDE and 2. <= aerosol_type <= 4. and abs(CAD) > 40:
                        height = (alt_top + alt_base) / 2.
                        thickness = (alt_top - alt_base)
                        aerosol_layer_data[aligned_date].append((height, thickness))

                except ValueError:
                    # Handle any conversion errors
                    pass

# Prepare the data for plotting
dates = []
heights = []
thickness_lower = []
thickness_upper = []

# Sort the dates for plotting
sorted_dates = sorted(aerosol_layer_data.keys())

# Process the data
for date in sorted_dates:
    for height, thickness in aerosol_layer_data[date]:
        days_since_reference = (date - reference_date).days
        dates.append(days_since_reference)
        heights.append(height)
        thickness_lower.append(height - thickness / 2.)
        thickness_upper.append(height + thickness / 2.)
        print(days_since_reference, height, height - thickness / 2.)

# Convert to numpy arrays for vectorized operations
dates = np.array(dates)
heights = np.array(heights)
thickness_lower = np.array(thickness_lower)
thickness_upper = np.array(thickness_upper)

# Plotting
fig, ax = plt.subplots(figsize=(10, 10))

# Plot the height
ax.plot(dates, heights, 'o', label='Aerosol Layer Height')

# Plot the thickness as shadow
ax.fill_between(dates, thickness_lower, thickness_upper, color='gray', alpha=0.5, label='Aerosol Layer Thickness')
ax.set_ylim(0, 20)
ax.set_xlim(0, 100)
# Labels and title
plt.xlabel('Days since 2011-06-04')
plt.ylabel('Height (km)')
plt.title('Aerosol Layer Height and Thickness Over Time')

# Show grid
plt.grid(True)

# Legend
plt.legend()

# Tight layout
plt.tight_layout()
plt.savefig(os.path.join(FIGURE_OUTPUT_PATH, 'aerosol_layer_height_thickness_time.png'), dpi=300)
