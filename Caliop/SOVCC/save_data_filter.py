#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    save_data_filter.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        05/06/2023 22:45

import pandas as pd
import numpy as np
import os

# variable file location
variable_file_location = './thickness_data_extraction'
data_save_location = './filtered_data'  # change to where you want to save the new csv file

# create save_location folder if not exist
try:
    os.stat(data_save_location)
except:
    os.mkdir(data_save_location)

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

# Iterate over the rows to check for latitude criterion
total_length = len(all_data)
for i, row in all_data.iterrows():
    all_data.loc[i, 'drop'] = len(all_data[(np.abs(all_data['latitude'] - row['latitude']) <= 1) &
                                           (all_data['utc_time'] == row['utc_time'])]) < 5
    if i % 1000 == 0:  # Print progress for every 1000 rows
        print(f"Processed {i} out of {total_length} rows")

# Keep only rows where drop is False
all_data = all_data[all_data['drop'] == False]

# Save the dataframe to csv file
all_data.to_csv(data_save_location + '/' + 'extracted_data.csv', index=False)
