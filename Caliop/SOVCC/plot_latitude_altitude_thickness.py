#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    plot_latitude_altitude_thickness.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        04/06/2023 15:04

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
from scipy.interpolate import griddata

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
all_data = pd.DataFrame(columns=['thickness', 'ash_height', 'latitude'])

for file in files:
    data = pd.read_csv(variable_file_location + '/' + file)
    print(f"Processing file {file}")

    for column in ['thickness', 'ash_height', 'latitude']:
        data[column] = pd.to_numeric(data[column], errors='coerce')

    all_data = all_data.append(data[['thickness', 'ash_height', 'latitude']], ignore_index=True)

# Remove rows with any NaN values
all_data = all_data.dropna()

# Now we are going to group the data by both latitude and ash_height
grouped_data = all_data.groupby(['latitude', 'ash_height']).mean().reset_index()

# Define the grid where we want to interpolate
grid_lat = np.linspace(grouped_data['latitude'].min(), grouped_data['latitude'].max(), 1000)
grid_height = np.linspace(grouped_data['ash_height'].min(), grouped_data['ash_height'].max(), 1000)
grid_lat, grid_height = np.meshgrid(grid_lat, grid_height)

# Interpolate the thickness over this grid using griddata
grid_thickness = griddata((grouped_data['latitude'], grouped_data['ash_height']), grouped_data['thickness'],
                          (grid_lat, grid_height), method='linear')

fig, ax = plt.subplots(figsize=(10, 8))

# Plot the interpolated data
c = ax.imshow(grid_thickness, extent=(grouped_data['latitude'].min(), grouped_data['latitude'].max(),
                                      grouped_data['ash_height'].min(), grouped_data['ash_height'].max()),
              origin='lower', aspect='auto', cmap='rainbow', vmin=0, vmax=4.)

ax.set_title('Average Thickness vs Latitude and Altitude', fontsize=20)
ax.set_xlabel('Latitude', fontsize=18)
ax.set_ylabel('Altitude', fontsize=18)
ax.grid(True)

# Adding a color bar
cbar = fig.colorbar(c, ax=ax)
cbar.set_label('Average Thickness', fontsize=18)

plt.savefig(figure_save_location + '/' + 'average_thickness_vs_latitude_altitude.png')

