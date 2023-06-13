#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    calbuco_meridional_transport.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        13/06/2023 23:26

from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from mpl_toolkits.basemap import Basemap
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
end_time = '2015-06-15'
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

# Group data by utc_time, calculate mean longitude, ash_height and thickness for each utc_time
grouped_data = all_data.groupby('utc_time').agg({'longitude':'mean', 'ash_height':'mean', 'thickness':'mean'}).reset_index()

# Get day of year from utc_time for coloring the points and lines in plot
grouped_data['day_of_year'] = grouped_data['utc_time'].dt.dayofyear

# Sort the data by utc_time
grouped_data.sort_values('utc_time', inplace=True)

# Create colormap for the day_of_year
cmap = plt.cm.viridis
norm = Normalize(vmin=grouped_data['day_of_year'].min(), vmax=grouped_data['day_of_year'].max())

# Create the figure and the axes
fig, ax = plt.subplots(figsize=(10,6))

# Plot lines with markers for each utc_time, color determined by day_of_year
ax.plot(grouped_data['longitude'], grouped_data['ash_height'], marker='o', linestyle='-', color=cmap(norm(grouped_data['day_of_year'].mean())))

# Add colorbar
cbar = plt.colorbar(ScalarMappable(norm=norm, cmap=cmap), ax=ax)
cbar.set_label('Day of Year')

# Add grid, title and labels
ax.grid(True)
ax.set_title('Mean Ash Height over Mean Longitude')
ax.set_xlabel('Mean Longitude')
ax.set_ylabel('Mean Ash Height')

# Save the figure
plt.tight_layout()
plt.savefig(os.path.join(figure_save_location, 'ash_height_vs_longitude.png'))
