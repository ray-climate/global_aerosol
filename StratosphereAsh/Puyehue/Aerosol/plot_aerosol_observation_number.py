#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    plot_aerosol_observation_number.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        03/11/2023 23:27

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

date_all = []
lat_all = []
alt_base_all = []
alt_top_all = []
depolarization_all = []
aerosol_type_all = []
CAD_all = []

# Dictionary to hold the count of valid depolarization values per day
valid_depolarization_count = defaultdict(int)

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

                    if (SOUTHERN_LATITUDE <= latitude <= NORTHERN_LATITUDE) & (MIN_ALTITUDE <= alt_base <= MAX_ALTITUDE) & (MIN_ALTITUDE <= alt_top <= MAX_ALTITUDE) & (2. <= aerosol_type <= 4.):
                        valid_depolarization_count[file_date] += 1
                except:
                    pass

# Sort the dictionary by date
sorted_valid_depolarization_count = dict(sorted(valid_depolarization_count.items()))

# Extract dates and counts for plotting
dates = list(sorted_valid_depolarization_count.keys())
counts = list(sorted_valid_depolarization_count.values())

# Plotting
plt.figure(figsize=(10, 5))
plt.plot(dates, counts, marker='o')
plt.xlabel('Date')
plt.ylabel('Number of Valid Depolarization Values')
plt.title('Valid Depolarization Values per Day')
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.gca().xaxis.set_major_locator(mdates.DayLocator())
plt.gcf().autofmt_xdate()  # Rotation
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(FIGURE_OUTPUT_PATH, 'valid_depolarization_values_per_day.png'))