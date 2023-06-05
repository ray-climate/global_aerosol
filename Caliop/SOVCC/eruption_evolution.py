#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    eruption_evolution.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        05/06/2023 17:11

# -*- coding:utf-8 -*-
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

# variable file location
variable_file_location = './thickness_data_extraction'
figure_save_location = './figures'

# Define time and latitude range
name = 'Caulle'
start_time = '2011-05-01'
end_time = '2011-06-30'
lat_top = 0
lat_bottom = -80

# create save_location folder if not exist
try:
    os.stat(figure_save_location)
except:
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

    all_data = all_data.append(data[['utc_time', 'thickness', 'latitude', 'ash_height']],
                               ignore_index=True)

# Remove rows with any NaN values
all_data = all_data.dropna()

# Filter data based on defined start_time, end_time, lat_top, and lat_bottom
all_data = all_data[(all_data['utc_time'] >= start_time) & (all_data['utc_time'] <= end_time) &
                    (all_data['latitude'] >= lat_bottom) & (all_data['latitude'] <= lat_top)]

# Sort the data by utc_time
all_data.sort_values('utc_time', inplace=True)

plt.figure(figsize=(10, 6))  # Set the plot size
plt.plot(all_data['utc_time'], all_data['thickness'], marker='o')
plt.xlabel('Time', fontsize=18)
plt.ylabel('Average Thickness', fontsize=18)
plt.grid(True)
plt.title('Average Thickness Over Time', fontsize=20)
plt.xticks(rotation=45)  # Rotate x-axis labels for better visibility
plt.tight_layout()  # Adjust subplot parameters to give specified padding

plt.savefig(figure_save_location + '/' + name + '_average_thickness_vs_time.png')