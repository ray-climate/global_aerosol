#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    plot_Hovmollerplot.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        04/06/2023 19:13

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

# variable file location
variable_file_location = './thickness_data_extraction'
figure_save_location = './figures'

# create save_location folder if not exist
try:
    os.stat(figure_save_location)
except:
    os.mkdir(figure_save_location)

files = [file for file in os.listdir(variable_file_location) if file.endswith('.csv')]

# Initiate empty DataFrame to store all data
all_data = pd.DataFrame(columns=['utc_time', 'thickness', 'latitude'])

for file in files:
    data = pd.read_csv(variable_file_location + '/' + file)
    print(f"Processing file {file}")

    for column in ['utc_time', 'thickness', 'latitude']:
        if column == 'utc_time':
            # Convert utc_time to datetime format
            data[column] = pd.to_datetime(data[column])
        else:
            data[column] = pd.to_numeric(data[column], errors='coerce')

    all_data = all_data.append(data[['utc_time', 'thickness', 'latitude']],
                               ignore_index=True)


# Remove rows with any NaN values
all_data = all_data.dropna()

# Define the bin edges for latitude
lat_bins = np.arange(-90, 91, 1)

# Bin the latitude data
all_data['latitude_bin'] = pd.cut(all_data['latitude'], bins=lat_bins)

# Group by the bins and utc_time (every 5 days) and calculate the mean thickness
all_data.set_index('utc_time', inplace=True)
grouped_data = all_data.groupby([pd.Grouper(freq='5D'), 'latitude_bin']).mean().reset_index()

# Pivot the data so that utc_time and latitude are the index and columns
pivoted_data = grouped_data.pivot(index='utc_time', columns='latitude_bin', values='thickness')

fig, ax = plt.subplots(figsize=(14, 10))

# Plot the pivoted data
c = ax.imshow(pivoted_data, aspect='auto', cmap='rainbow', origin='lower',
              extent=[-90, 90, 0, all_data.index.max()], vmin=0, vmax=4.)

ax.set_xlabel('Latitude', fontsize=18)
ax.set_ylabel('Time', fontsize=18)
ax.grid(True)
ax.set_xlim(-80, 80)
plt.tick_params(axis='both', which='major', labelsize=18)

# Adding a color bar
cbar = fig.colorbar(c, ax=ax, shrink=0.7, extend='both')
cbar.set_label('Ash Layer Thickness', fontsize=18)
cbar.ax.tick_params(labelsize=18)

plt.savefig(figure_save_location + '/' + 'average_thickness_vs_latitude_time.png')
