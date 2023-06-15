#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    Caulle_ash_tracking.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        15/06/2023 12:13

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
variable_file_location = '../SOVCC/filtered_data_continuous_10'
figure_save_location = './figures'

# Define time and latitude range
name = 'Calbuco'
start_time = '2011-06-15'
end_time = '2011-08-20'
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

from mpl_toolkits.basemap import Basemap
import matplotlib as mpl

# Continued from your script...
# Group data by 'utc_time' and calculate mean 'latitude' and 'longitude'
grouped_data = all_data.groupby('utc_time').agg({'latitude': 'mean', 'longitude': 'mean'}).reset_index()

# Convert 'utc_time' to numeric for color mapping
grouped_data['utc_time'] = grouped_data['utc_time'].apply(lambda x: mdates.date2num(x))

# Plotting
fig, ax = plt.subplots(figsize=(30,10))
m = Basemap(projection='cyl', resolution='l')

# Draw continents and countries
m.drawcoastlines()
m.drawcountries()
m.fillcontinents(color='lightgray')

# Draw parallels (latitude lines) and meridians (longitude lines)
m.drawparallels(np.arange(-90.,91.,30.), labels=[True,False,False,True], fontsize=18)
m.drawmeridians(np.arange(-180.,181.,60.), labels=[True,False,False,True], fontsize=18)

# Normalizing 'utc_time' to 0-1 for color mapping
norm = Normalize(vmin=grouped_data['utc_time'].min(), vmax=grouped_data['utc_time'].max())
cmap = plt.get_cmap('coolwarm_r')  # Blue to red color map
sm = ScalarMappable(norm=norm, cmap=cmap)

# Plot mean latitudes and longitudes with colors corresponding to 'utc_time'
scatter = m.scatter(x=grouped_data['longitude'], y=grouped_data['latitude'], c=grouped_data['utc_time'], cmap=cmap, latlon=True)

# Add a colorbar
cbar = plt.colorbar(scatter, shrink=0.6)

# Correcting the colorbar labels to date format and remove the time part
date_ticks = [mdates.num2date(tick).strftime('%Y-%m-%d') for tick in cbar.get_ticks()]
cbar.ax.set_yticklabels(date_ticks, fontsize=18)

# Saving the figure
plt.savefig(f"{figure_save_location}/global_plot_Caulle.png")

