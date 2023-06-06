#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    eruption_evolution.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        05/06/2023 17:11

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
variable_file_location = './thickness_data_extraction'
figure_save_location = './figures'

# Define time and latitude range
name = 'Caulle'
start_time = '2011-06-15'
end_time = '2011-06-20'
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

start_date = pd.to_datetime(start_time)
grouped_data_day = all_data.groupby(pd.Grouper(key='utc_time', freq='D')).agg({'thickness': ['mean', 'std']})
grouped_data_day.columns = ['thickness_mean', 'thickness_std']

grouped_data_day_days = (grouped_data_day.index - start_date).days  # new Series representing days since start

# Set up colormap
cmap = plt.get_cmap("jet")
norm = Normalize(vmin=grouped_data_utc['count'].min(), vmax=grouped_data_utc['count'].max())

fig, ax1 = plt.subplots(figsize=(8, 8))  # Set the plot size

# Scatter plot with time-based x-axis
# sc = ax1.scatter(grouped_data_utc.index, grouped_data_utc['thickness'], c=grouped_data_utc['count'], cmap=cmap, norm=norm, alpha=0.5)
# Scatter plot with time-based x-axis
sc = ax1.scatter(grouped_data_utc.index, grouped_data_utc['thickness'], c=grouped_data_utc['count'], cmap=cmap, norm=norm, alpha=0.3, s=5*grouped_data_utc['count'])

ax1.set_ylabel('Ash layer thickness', fontsize=18)
ax1.set_ylim(0, 4)  # set ylim correctly
ax1.grid(True)

# create an inset_axes instance with a width of "5%" and a height of "50%"
# located at (0, 0.6)
axins = inset_axes(ax1,
                   width="50%",  # width = 5% of parent_bbox width
                   height="5%",  # height : 50%
                   loc='upper left',
                   bbox_to_anchor=(0.05, 0.55, 0.4, 0.4),
                   bbox_transform=ax1.transAxes,
                   borderpad=0
                   )

plt.colorbar(sc, cax=axins, orientation='horizontal', label='Counts')


ax1.tick_params(axis='both', which='major', labelsize=18)
ax1.set_xticklabels([])  # Hide ax1 xticklabels
ax1.set_title(f"{name}", fontsize=20)
ax2 = ax1.twiny()  # Create a twin x-axis sharing the y-axis
ax2.xaxis.tick_bottom()  # Move ax2 xticks to bottom
ax2.xaxis.set_label_position('bottom')  # Move ax2 xlabel to bottom

# Error bar plot with day-based x-axis
ax2.errorbar(grouped_data_day_days, grouped_data_day['thickness_mean'], yerr=grouped_data_day['thickness_std'], fmt='o', color='black', markeredgecolor='black', capsize=3, elinewidth=2.4)
start_time_dt = datetime.strptime(start_time, '%Y-%m-%d')
formatted_start_time = start_time_dt.strftime('%d/%m/%Y')

ax2.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))  # Ensure the ticks are integers
ax2.set_xlabel('Days Since T0 (' + formatted_start_time + ')', fontsize=18)
ax2.tick_params(axis='both', which='major', labelsize=18)
ax2.set_xlim(0, 50)
fig.tight_layout()

plt.savefig(figure_save_location + '/' + name + '_thickness_for_each_utc_time.png')







