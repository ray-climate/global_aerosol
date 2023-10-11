#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    plot_identified_ash.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        11/10/2023 11:22

import pandas as pd
import os

variable_file_location = '../../../Caliop/SOVCC/filtered_data_continuous_10/'
figure_save_location = './figures'

# create save_location folder if not exist
if not os.path.exists(figure_save_location):
    os.mkdir(figure_save_location)

start_date = '2011-06-13'
end_date = '2011-08-20'
lat_north = 0
lat_south = -80

files = [file for file in os.listdir(variable_file_location) if file.endswith('.csv')]

# Initiate empty DataFrame to store all data
all_data = pd.DataFrame(columns=['utc_time', 'thickness', 'latitude', 'longitude', 'ash_height'])  # add ash_height column

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
all_data = all_data[(all_data['utc_time'] >= start_date) & (all_data['utc_time'] <= end_date) &
                    (all_data['latitude'] >= lat_south) & (all_data['latitude'] <= lat_north)]

unique_utc_times = all_data['utc_time'].drop_duplicates().reset_index(drop=True)
count_unique_utc_times = unique_utc_times.shape[0]
print(f'The number of unique utc_time values is: {count_unique_utc_times}')
print(unique_utc_times)

