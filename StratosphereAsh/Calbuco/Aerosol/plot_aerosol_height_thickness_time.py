#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    plot_aerosol_height_thickness_time.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        07/11/2023 21:18

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
MAX_ALTITUDE = 25.

# Define the reference date
reference_date = datetime(2015, 4, 22)

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
start_date = datetime(2015, 4, 1)
end_date = datetime(2015, 5, 31)

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
                    if SOUTHERN_LATITUDE <= latitude < NORTHERN_LATITUDE and MIN_ALTITUDE <= alt_base <= MAX_ALTITUDE and MIN_ALTITUDE <= alt_top <= MAX_ALTITUDE and 2. <= aerosol_type <= 2. and abs(CAD) > 20:
                        height = (alt_top + alt_base) / 2.
                        thickness = (alt_top - alt_base)
                        aerosol_layer_data[aligned_date].append((height, thickness))

                except ValueError:
                    # Handle any conversion errors
                    pass

# Prepare lists to hold the mean values
unique_dates = sorted(aerosol_layer_data.keys())
mean_dates = []
mean_heights = []
mean_thicknesses = []

# Calculate mean height and thickness for each date
for date in unique_dates:
    day_data = aerosol_layer_data[date]
    heights = []
    thicknesses = []

    for height, thickness in day_data:
        heights.append(height)
        thicknesses.append(thickness)

    if len(thicknesses) > 10:
        # Compute means
        mean_height = np.mean(heights)
        mean_thickness = np.mean(thicknesses)

        # Compute the days since the reference date
        days_since_reference = (date - reference_date).days

        # Append the means to the lists
        mean_dates.append(days_since_reference)
        mean_heights.append(mean_height)
        mean_thicknesses.append(mean_thickness)

# Convert to numpy arrays
mean_dates = np.array(mean_dates)
mean_heights = np.array(mean_heights)
mean_thicknesses = np.array(mean_thicknesses)

mean_thickness_lower = mean_heights - mean_thicknesses / 2.
mean_thickness_upper = mean_heights + mean_thicknesses / 2.

# Plotting
fig, ax = plt.subplots(figsize=(10, 10))

# Plot the mean height
ax.plot(mean_dates, mean_heights, '*-', label='Mean Aerosol Layer Height', color='#FF5900')

# Plot the mean thickness as shadow
ax.fill_between(mean_dates, mean_thickness_lower, mean_thickness_upper, color='#FF5900', alpha=0.6,
                label='Mean Aerosol Layer Thickness')

# Labels and title
plt.xlabel('Days since Eruption', fontsize=18)
plt.ylabel('Height [km]', fontsize=18)
plt.title('Stratospheric Ash Layer Height and Thickness', fontsize=20)
plt.xlim(0, 100)
plt.ylim(0, 20)
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)
plt.legend(loc='upper right', fontsize=16)

# Tight layout
plt.tight_layout()
plt.savefig(os.path.join(FIGURE_OUTPUT_PATH, 'aerosol_layer_height_thickness_time.png'), dpi=300)

# Save the data to CSV
csv_output_path = os.path.join(FIGURE_OUTPUT_PATH, 'aerosol_data.csv')
with open(csv_output_path, 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    # Write header
    csvwriter.writerow(['Day Since Reference', 'Mean Height (km)', 'Mean Thickness (km)'])
    # Write data
    for i in range(len(mean_dates)):
        csvwriter.writerow([mean_dates[i], mean_heights[i], mean_thicknesses[i]])
