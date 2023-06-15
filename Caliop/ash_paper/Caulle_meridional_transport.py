#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    Caulle_meridional_transport.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        15/06/2023 12:18

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
volcano_name = 'Caulle'
start_time = '2011-06-04'
end_time = '2011-08-01'
lat_top = 0
lat_bottom = -80

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
cmap = plt.cm.get_cmap('Reds')
grouped_data['date_num'] = mdates.date2num(grouped_data['utc_time'])
norm = Normalize(vmin=grouped_data['date_num'].min(), vmax=grouped_data['date_num'].max())

# Create a new figure for ash height over longitude
fig1, ax1 = plt.subplots(figsize=(10,6))

# Group by each day and plot ash_height over longitude
for name, group in grouped_data.groupby(grouped_data['utc_time'].dt.date):
    group = group.sort_values('longitude')
    for i in range(len(group) - 1):  # iterate over each pair of points
        x = group['longitude'].iloc[i:i+2]
        y = group['ash_height'].iloc[i:i+2]
        linewidth = group['thickness'].iloc[i:i+2].mean() * 5
        ax1.plot(x, y, marker='o', linestyle='-', color=cmap(norm(mdates.date2num(name))), linewidth=linewidth)

# Set title, x and y labels
ax1.set_title('Ash height over longitude')
ax1.set_xlabel('Longitude')
ax1.set_ylabel('Ash height')
ax1.set_ylim(12, 22)
ax1.set_xlim(-80, 60)

# Create custom legend
sm = ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax1, orientation='vertical', label='Date')
cbar.ax.invert_yaxis()

# Format colorbar labels as dates
formatter = FuncFormatter(lambda x, pos: mdates.num2date(x).strftime('%Y-%m-%d'))
cbar.ax.yaxis.set_major_formatter(formatter)

# Save figure
plt.savefig(figure_save_location + '/%s'%volcano_name + '_ash_height_over_longitude.png', dpi=300)

# Create a new figure for average thickness over time
fig2, ax2 = plt.subplots(figsize=(10,6))

# Plot the average thickness per day over time
grouped_by_day = grouped_data.groupby(grouped_data['utc_time'].dt.date)['thickness'].mean().reset_index()
grouped_by_day['utc_time'] = pd.to_datetime(grouped_by_day['utc_time'])
ax2.plot(grouped_by_day['utc_time'], grouped_by_day['thickness'])

# Set title, x and y labels
ax2.set_title('Average thickness over time')
ax2.set_xlabel('Date')
ax2.set_ylabel('Average thickness')

# Save figure
plt.savefig(figure_save_location + '/%s'%volcano_name + '_average_thickness_over_time.png', dpi=300)
