#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    eruption_evolution.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        05/06/2023 17:11

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize

# variable file location
variable_file_location = './thickness_data_extraction'
figure_save_location = './figures'

# Define time and latitude range
name = 'Caulle'
start_time = '2011-06-10'
end_time = '2011-07-31'
lat_top = 0
lat_bottom = -80

# create save_location folder if not exist
if not os.path.exists(figure_save_location):
    os.mkdir(figure_save_location)

files = [file for file in os.listdir(variable_file_location) if file.endswith('.csv')]

# Initiate empty DataFrame to store all data
all_data = pd.DataFrame(columns=['utc_time', 'thickness', 'latitude', 'ash_height'])

for file in files:
    data = pd.read_csv(variable_file_location + '/' + file)
    print(f"Processing file {file}")

    for column in ['utc_time', 'thickness', 'latitude', 'ash_height']:
        if column == 'utc_time':
            # Convert utc_time to datetime format
            data[column] = pd.to_datetime(data[column], format='%Y-%m-%dT%H:%M:%S')
        else:
            data[column] = pd.to_numeric(data[column], errors='coerce')

    all_data = all_data.append(data[['utc_time', 'thickness', 'latitude', 'ash_height']], ignore_index=True)

# Remove rows with any NaN values
all_data = all_data.dropna()

# Filter data based on defined start_time, end_time, lat_top, and lat_bottom
all_data = all_data[(all_data['utc_time'] >= start_time) & (all_data['utc_time'] <= end_time) &
                    (all_data['latitude'] >= lat_bottom) & (all_data['latitude'] <= lat_top)]

# Group the data by each day and calculate the mean and standard deviation of thickness
grouped_data = all_data.groupby(pd.Grouper(key='utc_time', freq='D'))['thickness'].agg(['mean', 'std', 'count'])

# Set up colormap
cmap = plt.get_cmap("viridis")
norm = Normalize(vmin=grouped_data['count'].min(), vmax=grouped_data['count'].max())

fig, ax = plt.subplots(figsize=(10, 6))  # Set the plot size
sc = ax.scatter(grouped_data.index, grouped_data['mean'], c=grouped_data['count'], cmap=cmap, norm=norm)
plt.errorbar(grouped_data.index, grouped_data['mean'], yerr=grouped_data['std'], fmt='o', color='black')
plt.colorbar(ScalarMappable(norm=norm, cmap=cmap), ax=ax, label='Count')
plt.xlabel('Time', fontsize=18)
plt.ylabel('Average Thickness', fontsize=18)
plt.grid(True)
plt.title('Average Thickness Over Time', fontsize=20)
plt.xticks(rotation=45)  # Rotate x-axis labels for better visibility
plt.ylim(0, 5.)
plt.tight_layout()  # Adjust subplot parameters to give specified padding
plt.savefig(figure_save_location + '/' + name + '_average_thickness_vs_time.png')



