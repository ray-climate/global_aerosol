# -*- coding:utf-8 -*-
# @Filename:    plot_Hovmollerplot.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        04/06/2023 19:13

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

# variable file location
variable_file_location = './filtered_data'
figure_save_location = './figures'

# create save_location folder if not exist
try:
    os.stat(figure_save_location)
except:
    os.mkdir(figure_save_location)

files = [file for file in os.listdir(variable_file_location) if file.endswith('.csv')]

# Initiate empty DataFrame to store all data
all_data = pd.DataFrame(columns=['utc_time', 'thickness', 'latitude', 'ash_height'])  # add ash_height column

for file in files:
    data = pd.read_csv(variable_file_location + '/' + file)
    print(f"Processing file {file}")

    for column in ['utc_time', 'thickness', 'latitude', 'ash_height']:  # add ash_height column
        if column == 'utc_time':
            # Convert utc_time to datetime format
            data[column] = pd.to_datetime(data[column], format='%Y-%m-%dT%H-%M-%S')
        else:
            data[column] = pd.to_numeric(data[column], errors='coerce')

    all_data = all_data.append(data[['utc_time', 'thickness', 'latitude', 'ash_height']],  # add ash_height column
                               ignore_index=True)

# Remove rows with any NaN values
all_data = all_data.dropna()

# Define the bin edges for latitude
lat_bins = np.arange(-90, 92, 2)

# Bin the latitude data
all_data['latitude_bin'] = pd.cut(all_data['latitude'], bins=lat_bins, labels=(lat_bins[:-1] + 1/2))

# Group the utc_time to every 10 days
all_data['utc_time_bin'] = all_data['utc_time'].dt.floor('5D')

# Split data into two based on ash_height
data_low_height = all_data[all_data['ash_height'] < 20]
data_high_height = all_data[all_data['ash_height'] >= 20]

fig, axs = plt.subplots(2, 1, figsize=(20, 13))  # two subplots in two rows

# Iterate over the two dataframes
for ax, data, title in zip(axs, [data_low_height, data_high_height], ['Ash Height < 20km', 'Ash Height >= 20km']):

    # For each row, check if there are less than 5 thickness values within ±1° latitude and the same utc_time_bin
    # total_length = len(data)
    # for i, row in data.iterrows():
    #     data.loc[i, 'drop'] = len(data[(np.abs(data['latitude'] - row['latitude']) <= 1) &
    #                                    (data['utc_time_bin'] == row['utc_time_bin'])]) < 5
    #     if i % 1000 == 0:  # Print progress for every 1000 rows
    #         print(f"Processed {i} out of {total_length} rows")
    #
    # # data['drop'] = data.apply(lambda row: len(data[(np.abs(data['latitude'] - row['latitude']) <= 1) &
    # #                                                (data['utc_time_bin'] == row['utc_time_bin'])]) < 5, axis=1)
    # # Keep only rows where drop is False
    # data = data[data['drop'] == False]

    # Group by 'utc_time_bin' and 'latitude_bin' and calculate the mean
    grouped_data = data.groupby(['utc_time_bin', 'latitude_bin']).mean().reset_index()

    # Pivot the data so that utc_time_bin and latitude_bin are the index and columns
    pivoted_data = grouped_data.pivot(index='latitude_bin', columns='utc_time_bin', values='thickness')

    # Plot the pivoted data
    c = ax.pcolormesh(pivoted_data.columns, pivoted_data.index, pivoted_data.values, cmap='jet', vmin=0, vmax=4.)

    #####
    # grouped_data = data.groupby(['utc_time_bin', 'latitude_bin'])
    # # Filter groups that have less than 5 values
    # filtered_data = grouped_data.filter(lambda x: len(x) >= 5)
    # # Recalculate the mean
    # filtered_grouped_data = filtered_data.groupby(['utc_time_bin', 'latitude_bin']).mean().reset_index()
    # # Pivot the data so that utc_time_bin and latitude_bin are the index and columns
    # pivoted_data = filtered_grouped_data.pivot(index='latitude_bin', columns='utc_time_bin', values='thickness')

    # Plot the pivoted data
    # c = ax.pcolormesh(pivoted_data.columns, pivoted_data.index, pivoted_data.values, cmap='jet', vmin=0, vmax=4.)

    ax.set_xlabel('Time', fontsize=18)
    ax.set_ylabel('Latitude', fontsize=18)
    ax.set_title(title, fontsize=20)  # set title for each subplot
    ax.grid(True)
    ax.set_xlim(pivoted_data.columns.min(), pivoted_data.columns.max())  # Limit x-axis to the minimum and maximum time
    ax.set_ylim(-80, 80)  # Limit y-axis to the range of latitude you have
    ax.tick_params(axis='both', which='major', labelsize=18)

    # Adding a color bar
    cbar = fig.colorbar(c, ax=ax, shrink=0.7, extend='both')
    cbar.set_label('Ash Layer Thickness', fontsize=18)
    cbar.ax.tick_params(labelsize=18)

plt.subplots_adjust(left=0.15)
plt.savefig(figure_save_location + '/' + 'average_thickness_vs_latitude_time_clean.png')
