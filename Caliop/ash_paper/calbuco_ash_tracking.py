#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    calbuco_ash_tracking.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        13/06/2023 16:31

from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
from matplotlib import gridspec
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd
import numpy as np
import os

# variable file location
variable_file_location = '../SOVCC/thickness_data_extraction_extinction'
figure_save_location = './figures'

# Define time and latitude range
name = 'Calbuco'
start_time = '2015-04-22'
end_time = '2015-06-25'
lat_top = 0
lat_bottom = -50

# create save_location folder if not exist
if not os.path.exists(figure_save_location):
    os.mkdir(figure_save_location)

files = [file for file in os.listdir(variable_file_location) if file.endswith('.csv')]

# Initiate empty DataFrame to store all data
all_data = pd.DataFrame(columns=['utc_time', 'thickness', 'latitude', 'ash_height', 'extinction'])

for file in files:
    data = pd.read_csv(variable_file_location + '/' + file)
    print(f"Processing file {file}")

    for column in ['utc_time', 'thickness', 'latitude', 'longitude', 'ash_height', 'extinction']:  # include 'extinction'
        if column == 'utc_time':
            # Convert utc_time to datetime format
            data[column] = pd.to_datetime(data[column], format='%Y-%m-%dT%H-%M-%S')
        else:
            data[column] = pd.to_numeric(data[column], errors='coerce')

    # Calculate AOD by multiplying 'thickness' and 'extinction'
    data['AOD'] = data['thickness'] * data['extinction']

    all_data = all_data.append(data[['utc_time', 'thickness', 'latitude', 'longitude', 'ash_height', 'extinction', 'AOD']], ignore_index=True)  # include 'extinction' and 'AOD'

# Remove rows with any NaN values
all_data = all_data.dropna()

# Filter data based on defined start_time, end_time, lat_top, and lat_bottom
all_data = all_data[(all_data['utc_time'] >= start_time) & (all_data['utc_time'] <= end_time) &
                    (all_data['latitude'] >= lat_bottom) & (all_data['latitude'] <= lat_top)]

# Continued from your script...
# Group data by 'utc_time' and calculate mean 'latitude' and 'longitude'
grouped_data = all_data.groupby('utc_time').agg({'latitude': 'mean', 'longitude': 'mean'}).reset_index()

# Convert 'utc_time' to numeric for color mapping
grouped_data['utc_time'] = grouped_data['utc_time'].apply(lambda x: mdates.date2num(x))

# Plotting
fig, ax = plt.subplots(figsize=(10,10))
cmap = plt.get_cmap('coolwarm')  # Blue to red color map

# Normalizing 'utc_time' to 0-1 for color mapping
norm = Normalize(vmin=grouped_data['utc_time'].min(), vmax=grouped_data['utc_time'].max())
sm = ScalarMappable(norm=norm, cmap=cmap)

# Plot mean latitudes and longitudes with colors corresponding to 'utc_time'
scatter = ax.scatter(x=grouped_data['longitude'], y=grouped_data['latitude'], c=grouped_data['utc_time'], cmap=cmap)

# Add a colorbar
cbar = plt.colorbar(scatter)
cbar.ax.set_yticklabels(pd.to_datetime(cbar.get_ticks()).strftime(date_format='%Y-%m-%d'))

# Labeling the axes
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')

# Saving the figure
plt.savefig(f"{figure_save_location}/global_plot_calbuco.png")

