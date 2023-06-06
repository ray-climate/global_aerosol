#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    box_caulle.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        06/06/2023 13:56

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
name = 'Puyehue-Cordón Caulle'
start_time = '2011-06-15'
end_time = '2011-08-05'
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
grouped_data_utc = all_data.groupby('utc_time').agg({'thickness': 'mean', 'ash_height': 'mean', 'count': 'first'})

start_date = pd.to_datetime(start_time)
grouped_data_day = all_data.groupby(pd.Grouper(key='utc_time', freq='D')).agg({'thickness': ['mean', 'std'], 'ash_height': ['mean', 'std']})

grouped_data_utc['day'] = (grouped_data_utc.index - start_date).days

# Define datetime variables
start_date = pd.to_datetime(start_time)
end_date = pd.to_datetime(end_time)

# Create new date range that spans entire period
full_date_range = pd.date_range(start=start_time, end=end_time, freq='D')

# Group data per day
thickness_data_per_day = all_data.groupby(all_data['utc_time'].dt.floor('D'))['thickness'].apply(list)
ash_height_data_per_day = all_data.groupby(all_data['utc_time'].dt.floor('D'))['ash_height'].apply(list)

# Reindex to full date range, filling missing days with empty lists
thickness_data_per_day = thickness_data_per_day.reindex(full_date_range, fill_value=[])
ash_height_data_per_day = ash_height_data_per_day.reindex(full_date_range, fill_value=[])

# Convert date range to days since start, for plotting
full_date_range_days = (full_date_range - start_date).days

# Initialize Figure and Axes
fig, ax = plt.subplots(nrows=2, ncols=1, figsize=(18, 12), sharex=True)
fig.subplots_adjust(hspace=0.1)

# Scatter plot with error bars for 'thickness'
ax[0].errorbar(grouped_data_day.index, grouped_data_day['thickness', 'mean'], yerr=grouped_data_day['thickness', 'std'],
               fmt='o', markersize=2, ecolor='black', capsize=3)
ax[0].set_ylabel('Ash layer thickness [km] (mean ± std)', fontsize=18)

# Boxplot for thickness
ax2 = ax[0].twinx()  # Create a twin y-axis sharing the x-axis
ax2.boxplot(thickness_data_per_day, positions=full_date_range_days, widths=0.6)
ax2.set_ylabel('Ash layer thickness [km] (boxplot)', fontsize=18)

# Scatter plot with error bars for 'ash_height'
ax[1].errorbar(grouped_data_day.index, grouped_data_day['ash_height', 'mean'], yerr=group_data_day['ash_height', 'std'],
               fmt='o', markersize=2, ecolor='black', capsize=3)
ax[1].set_ylabel('Ash height [km] (mean ± std)', fontsize=18)

# Boxplot for ash_height
ax4 = ax[1].twinx()  # Create a twin y-axis sharing the x-axis
ax4.boxplot(ash_height_data_per_day, positions=full_date_range_days, widths=0.6)
ax4.set_ylabel('Ash height [km] (boxplot)', fontsize=18)

# Final adjustments to the plot
plt.xlabel('Days since eruption', fontsize=18)
ax[0].xaxis.set_major_locator(mdates.MonthLocator())
ax[0].xaxis.set_minor_locator(mdates.WeekdayLocator())
ax[0].xaxis.set_major_formatter(mdates.DateFormatter('%b'))
ax[0].xaxis.set_minor_formatter(mdates.DateFormatter('%d'))

# Save Figure
plt.savefig(figure_save_location + '/' + name + '_box.png', dpi=300, bbox_inches='tight')

print('Completed!')

