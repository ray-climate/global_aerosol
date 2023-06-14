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
end_time = '2015-05-02'
lat_top = 0
lat_bottom = -50

# create save_location folder if not exist
if not os.path.exists(figure_save_location):
    os.mkdir(figure_save_location)

files = [file for file in os.listdir(variable_file_location) if file.endswith('.csv')]

# Initiate empty DataFrame to store all data
all_data = pd.DataFrame(columns=['utc_time', 'thickness', 'latitude', 'longitude', 'ash_height', 'extinction'])

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

# Iterate over the rows to check for latitude criterion
all_data['count'] = np.nan
for i, row in all_data.iterrows():
    nearby_records = all_data[(np.abs(all_data['latitude'] - row['latitude']) <= 1) &
                              (all_data['utc_time'] == row['utc_time'])]
    if nearby_records.shape[0] < 5:
        all_data.drop(i, inplace=True)
    else:
        all_data.loc[i, 'count'] = nearby_records.shape[0]
    if i % 1000 == 0:  # Print progress for every 1000 rows
        print(f"Processed {i} rows")

# Group data by utc_time, calculate mean longitude, ash_height and thickness for each utc_time
grouped_data = all_data.groupby('utc_time').agg({'longitude':'mean', 'ash_height':'mean', 'thickness':'mean'}).reset_index()

# Sort the data by utc_time
grouped_data = grouped_data.sort_values('utc_time')

# Create a new figure
fig, ax = plt.subplots(figsize=(10,6))

# Group by each day and plot ash_height over longitude
for name, group in grouped_data.groupby(grouped_data['utc_time'].dt.date):
    group = group.sort_values('longitude')
    ax.plot(group['longitude'], group['ash_height'], marker='o', linestyle='-', label=name)

# Set title, x and y labels
ax.set_title('Ash height over longitude')
ax.set_xlabel('Longitude')
ax.set_ylabel('Ash height')
ax.set_xlim(-80, 30)
# Optional: rotate x labels if they overlap
plt.xticks(rotation=45)

# Optional: Add a legend
ax.legend()

# Save figure
plt.savefig(figure_save_location + '/' + 'ash_height_over_longitude.png', dpi=300)