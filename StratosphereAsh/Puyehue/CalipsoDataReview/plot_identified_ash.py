#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    plot_identified_ash.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        11/10/2023 11:22

import pandas as pd
import datetime
import logging
import sys
import os
sys.path.append('../../../')
from getColocationData.get_caliop import *

def get_script_name():
    return sys.modules['__main__'].__file__
# Get the name of the script
script_name = get_script_name()
# Split the script name into a base name and an extension
script_base, script_ext = os.path.splitext(script_name)

# Add the .log extension to the base name
log_filename = script_base + '.log'
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                    filemode='w',
                    filename=log_filename,
                    level=logging.INFO)
# Get a logger object
logger = logging.getLogger()

CALIPSO_location = "/gws/nopw/j04/qa4ecv_vol3/CALIPSO/asdc.larc.nasa.gov/data/CALIPSO/LID_L2_05kmAPro-Standard-V4-51/"
variable_file_location = '../../../Caliop/SOVCC/filtered_data_continuous_10/'
figure_save_location = './figures'

# Function to extract datetime from filename
def extract_datetime_from_filename(filename):
    datetime_str = filename.split('.')[1]
    if datetime_str.endswith("ZN") or datetime_str.endswith("ZD"):
        datetime_str = datetime_str[:-2]
    return datetime.datetime.strptime(datetime_str, "%Y-%m-%dT%H-%M-%S")

def get_closest_file_for_utc(utc_time):
    year = utc_time.strftime('%Y')
    month = utc_time.strftime('%m')
    day = utc_time.strftime('%d')

    specific_day_folder = os.path.join(CALIPSO_location, year, month)

    # Check if specific day folder exists
    if not os.path.exists(specific_day_folder):
        return None

    # List all HDF files for the specific day
    all_files = [f for f in os.listdir(specific_day_folder) if
                 f.endswith('.hdf') and f.startswith(f"CAL_LID_L2_05kmAPro-Standard-V4-51.{year}-{month}")]

    # If there are no files for that month
    if not all_files:
        return None

    # Extract datetimes from filenames
    file_datetimes = [extract_datetime_from_filename(f) for f in all_files]

    # Determine the closest file by computing the timedelta
    min_diff = datetime.timedelta(days=365)  # Arbitrary large number
    closest_file = None

    for file, file_datetime in zip(all_files, file_datetimes):
        time_diff = abs(utc_time - file_datetime)

        if time_diff < min_diff:
            min_diff = time_diff
            closest_file = os.path.join(specific_day_folder, file)

    return closest_file

# create save_location folder if not exist
if not os.path.exists(figure_save_location):
    os.mkdir(figure_save_location)

start_date = '2011-07-01'
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

closest_files = []

for time in unique_utc_times:
    print('Identified ash for time: ', time)
    closest_file = get_closest_file_for_utc(time)
    print('---------------- Closest file: ', closest_file)
    if closest_file:
        closest_files.append(closest_file)

    (footprint_lat_caliop, footprint_lon_caliop,
     alt_caliop, beta_caliop, alpha_caliop,
     aerosol_type_caliop, feature_type_caliop) \
        = extract_variables_from_caliop(closest_file, logger)
    print(footprint_lat_caliop)


print(closest_files)

