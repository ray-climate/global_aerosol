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
start_time = '2011-06-10'
end_time = '2011-07-31'
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

# Iterate over the rows to check for latitude criterion
for i, row in all_data.iterrows():
    nearby_records = all_data[(np.abs(all_data['latitude'] - row['latitude']) <= 1) &
                              (all_data['utc_time'] == row['utc_time'])]
    if nearby_records.shape[0] < 5:
        all_data.drop(i, inplace=True)
    if i % 1000 == 0:  # Print progress for every 1000 rows
        print(f"Processed {i} rows")

# Average the thickness for same utc_time
all_data = all_data.groupby('utc_time').mean().reset_index()

grouped_data = all_data.groupby(pd.Grouper(key='utc_time', freq='D'))['thickness'].agg(['mean', 'std'])

plt.figure(figsize=(10, 6))  # Set the plot size
plt.plot(all_data['utc_time'], all_data['thickness'], 'ro')
plt.errorbar(grouped_data.index, grouped_data['mean'], yerr=grouped_data['std'], fmt='o')
plt.xlabel('Time', fontsize=18)
plt.ylabel('Average Thickness', fontsize=18)
plt.grid(True)
plt.title('Average Thickness Over Time', fontsize=20)
plt.xticks(rotation=45)  # Rotate x-axis labels for better visibility
plt.ylim(0, 5.)
plt.tight_layout()  # Adjust subplot parameters to give specified padding
plt.savefig(figure_save_location + '/' + name + '_average_thickness_vs_time.png')

# Ash Height Plot
plt.figure(figsize=(10, 6))  # Set the plot size
plt.plot(all_data['utc_time'], all_data['ash_height'], marker='o')
plt.xlabel('Time', fontsize=18)
plt.ylabel('Average Ash Height', fontsize=18)
plt.grid(True)
plt.title('Average Ash Height Over Time', fontsize=20)
plt.xticks(rotation=45)  # Rotate x-axis labels for better visibility
plt.tight_layout()  # Adjust subplot parameters to give specified padding
plt.savefig(figure_save_location + '/' + name + '_average_ash_height_vs_time.png')



