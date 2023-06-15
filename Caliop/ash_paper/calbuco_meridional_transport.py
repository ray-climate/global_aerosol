#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    calbuco_meridional_transport.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        13/06/2023 23:26

from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib.ticker import FuncFormatter
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
variable_file_location = '../SOVCC/filtered_data_continuous_10'
figure_save_location = './figures'

# Define time and latitude range
name = 'Calbuco'
start_time = '2015-04-22'
end_time = '2015-05-02'
lat_top = 0
lat_bottom = -50

# create save_location folder if not exist
if not os.path.exists(figure_save_location):
    os.mkdir(figure_save_location)

files = [file for file in os.listdir(variable_file_location) if file.endswith('.csv')]

# Initiate empty DataFrame to store all data
all_data = pd.DataFrame(columns=['utc_time', 'thickness', 'latitude', 'longitude', 'ash_height'])

for file in files:
    data = pd.read_csv(variable_file_location + '/' + file)
    print(f"Processing file {file}")

    for column in ['utc_time', 'thickness', 'latitude', 'longitude', 'ash_height']:  # include 'extinction'
        if column == 'utc_time':
            # Convert utc_time to datetime format
            data[column] = pd.to_datetime(data[column], format='%Y-%m-%d %H:%M:%S')
        else:
            data[column] = pd.to_numeric(data[column], errors='coerce')

    all_data = all_data.append(data[['utc_time', 'thickness', 'latitude', 'longitude', 'ash_height']], ignore_index=True)  # include 'extinction' and 'AOD'

# Remove rows with any NaN values
all_data = all_data.dropna()

# Filter data based on defined start_time, end_time, lat_top, and lat_bottom
all_data = all_data[(all_data['utc_time'] >= start_time) & (all_data['utc_time'] <= end_time) &
                    (all_data['latitude'] >= lat_bottom) & (all_data['latitude'] <= lat_top)]

# Group data by utc_time, calculate mean longitude, ash_height and thickness for each utc_time
grouped_data = all_data.groupby('utc_time').agg({'longitude':'mean', 'ash_height':'mean', 'thickness':'mean'}).reset_index()

# Create a colormap
cmap = plt.cm.get_cmap('jet')
grouped_data['date_num'] = mdates.date2num(grouped_data['utc_time'])
norm = Normalize(vmin=grouped_data['date_num'].min(), vmax=grouped_data['date_num'].max())

# Create a new figure
fig, ax = plt.subplots(figsize=(10,4))

# Group by each day and plot ash_height over longitude
for name, group in grouped_data.groupby(grouped_data['utc_time'].dt.date):
    group = group.sort_values('longitude')
    for i in range(len(group) - 1):  # iterate over each pair of points
        x = group['longitude'].iloc[i:i+2]
        y = group['ash_height'].iloc[i:i+2]
        linewidth = group['thickness'].iloc[i:i+2].mean() * 5
        ax.plot(x, y, marker='o', linestyle='-', color=cmap(norm(mdates.date2num(name))), linewidth=linewidth)

# Set title, x and y labels
ax.set_title('Ash height from Calbuco eruption in 2015')
ax.set_xlabel('Longitude (deg)')
ax.set_ylabel('Altitude (km)')
ax.set_ylim(12, 22)
ax.set_xlim(-80, 60)
# Optional: rotate x labels if they overlap
plt.xticks(rotation=45)

# Create custom legend
sm = ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax, orientation='vertical', label='Date', shrink=0.5, pad=0.05)
cbar.ax.invert_yaxis()

# Format colorbar labels as dates
formatter = FuncFormatter(lambda x, pos: mdates.num2date(x).strftime('%Y-%m-%d'))
cbar.ax.yaxis.set_major_formatter(formatter)

# Save figure
plt.savefig(figure_save_location + '/' + 'ash_height_over_longitude.png', dpi=300)