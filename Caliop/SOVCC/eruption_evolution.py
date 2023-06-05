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
from matplotlib.dates import date2num

# variable file location
variable_file_location = './thickness_data_extraction'
figure_save_location = './figures'

# Define time and latitude range
name = 'Caulle'
start_time = pd.to_datetime('2011-06-10')
end_time = pd.to_datetime('2011-07-31')
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
            data[column] = pd.to_datetime(data[column], format='%Y-%m-%dT%H-%M-%S')
        else:
            data[column] = pd.to_numeric(data[column], errors='coerce')

    all_data = all_data.append(data[['utc_time', 'thickness', 'latitude', 'ash_height']], ignore_index=True)

# Remove rows with any NaN values
all_data = all_data.dropna()

# Filter data based on defined start_time, end_time, lat_top, and lat_bottom
all_data = all_data[(all_data['utc_time'] >= start_time) & (all_data['utc_time'] <= end_time) &
                    (all_data['latitude'] >= lat_bottom) & (all_data['latitude'] <= lat_top)]

# Convert utc_time to number of days from start_time
all_data['utc_time'] = (all_data['utc_time'] - start_time).dt.days

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

# Group the data by each utc_time and calculate the mean and count of thickness
grouped_data_utc = all_data.groupby('utc_time').agg({'thickness': 'mean', 'count': 'first'})

# Set up colormap
cmap = plt.get_cmap("rainbow")
norm = Normalize(vmin=grouped_data_utc['count'].min(), vmax=grouped_data_utc['count'].max())

fig, ax = plt.subplots(figsize=(10, 6))  # Set the plot size
sc = ax.scatter(grouped_data_utc.index, grouped_data_utc['thickness'], c=grouped_data_utc['count'], cmap=cmap, norm=norm, alpha=0.5)
plt.colorbar(ScalarMappable(norm=norm, cmap=cmap), ax=ax, label='Count')
plt.xlabel(f'Time T0={start_time.date()}', fontsize=18)  # Modify x-label
plt.ylabel('Thickness', fontsize=18)
ax.set_ylim = (0, 4)
plt.grid(True)
plt.title('Thickness for Each UTC Time', fontsize=20)
plt.xticks(rotation=45)  # Rotate x-axis labels for better visibility
plt.tight_layout()  # Adjust subplot parameters to give specified padding
plt.savefig(figure_save_location + '/' + name + '_thickness_for_each_utc_time.png')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize
from matplotlib.dates import date2num

# variable file location
variable_file_location = './thickness_data_extraction'
figure_save_location = './figures'

# Define time and latitude range
name = 'Caulle'
start_time = pd.to_datetime('2011-06-10')
end_time = pd.to_datetime('2011-07-31')
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
            data[column] = pd.to_datetime(data[column], format='%Y-%m-%dT%H-%M-%S')
        else:
            data[column] = pd.to_numeric(data[column], errors='coerce')

    all_data = all_data.append(data[['utc_time', 'thickness', 'latitude', 'ash_height']], ignore_index=True)

# Remove rows with any NaN values
all_data = all_data.dropna()

# Filter data based on defined start_time, end_time, lat_top, and lat_bottom
all_data = all_data[(all_data['utc_time'] >= start_time) & (all_data['utc_time'] <= end_time) &
                    (all_data['latitude'] >= lat_bottom) & (all_data['latitude'] <= lat_top)]

# Convert utc_time to number of days from start_time
all_data['utc_time'] = (all_data['utc_time'] - start_time).dt.days

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

# Group the data by each utc_time and calculate the mean and count of thickness
grouped_data_utc = all_data.groupby('utc_time').agg({'thickness': 'mean', 'count': 'first'})

# Set up colormap
cmap = plt.get_cmap("rainbow")
norm = Normalize(vmin=grouped_data_utc['count'].min(), vmax=grouped_data_utc['count'].max())

fig, ax = plt.subplots(figsize=(10, 6))  # Set the plot size
sc = ax.scatter(grouped_data_utc.index, grouped_data_utc['thickness'], c=grouped_data_utc['count'], cmap=cmap, norm=norm, alpha=0.5)
plt.colorbar(ScalarMappable(norm=norm, cmap=cmap), ax=ax, label='Count')
plt.xlabel(f'Time T0={start_time.date()}', fontsize=18)  # Modify x-label
plt.ylabel('Thickness', fontsize=18)
ax.set_ylim = (0, 4)
plt.grid(True)
plt.title('Thickness for Each UTC Time', fontsize=20)
plt.xticks(rotation=45)  # Rotate x-axis labels for better visibility
plt.tight_layout()  # Adjust subplot parameters to give specified padding
plt.savefig(figure_save_location + '/' + name + '_thickness_for_each_utc_time.png')



