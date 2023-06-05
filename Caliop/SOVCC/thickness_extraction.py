#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    thickness_extraction.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        31/05/2023 10:28

import sys
sys.path.append('../../')

from Caliop.caliop import Caliop_hdf_reader
import pandas as pd
import numpy as np
import sys
import os

# set year from command line arugment
year = sys.argv[1]

# caliop location on CEDA
caliop_extracted_location = './caliop_ash_data_extraction'
save_location = './thickness_data_extraction'

# create save_location folder if not exist
try:
    os.stat(save_location)
except:
    os.mkdir(save_location)

def calculate_ash_mask_thickness(ash_mask, altitude):
    """
    Calculates thickness of ash mask based on altitude.

    Args:
        ash_mask: List of int
        altitude: List of float

    Returns:
        thicknesses: List of float
    """
    thicknesses = []  # Initialize thicknesses list
    mean_heights = []
    # Convert ash_mask and altitude to numpy arrays
    ash_mask = np.array(ash_mask)
    altitude = np.array(altitude)

    # Find indices of 1s
    one_indices = np.where(ash_mask == 1)[0]

    if len(one_indices) > 0:
        # Find all sequences of 1s
        sequences = np.split(one_indices, np.where(np.diff(one_indices) != 1)[0] + 1)

        for seq in sequences:
            # If the sequence has more than one element
            if len(seq) > 1:
                # Calculate thickness based on corresponding altitude
                min_index = seq[0]
                max_index = seq[-1]

                if min_index > 0:
                    max_altitude = altitude[min_index] + 0.5 * (altitude[min_index - 1] - altitude[min_index])
                else:
                    max_altitude = altitude[min_index]

                if max_index < len(altitude) - 1:
                    min_altitude = altitude[max_index] - 0.5 * (altitude[max_index] - altitude[max_index + 1])
                else:
                    min_altitude = altitude[max_index]

                thickness = max_altitude - min_altitude
                thicknesses.append(thickness)
                mean_heights.append(np.mean([max_altitude, min_altitude]))

    return thicknesses, mean_heights

# loop through all the sub year folder in caliop_location
latitude_all = []
longitude_all = []
thickness_all = []
ash_height_all = []
troppause_altitude_all = []
utc_time_all = []

for caliop_sub_folder in os.listdir(caliop_extracted_location + '/' + year):

    # print('---------> Reading caliop date: %s' %caliop_sub_folder)

    for file in os.listdir(caliop_extracted_location + '/' + year + '/' + caliop_sub_folder):
        # if file.endswith('.npz') & file.starts('CAL_LID_L2_05kmAPro-Standard-V4-20.2011-06'):
        if file.startswith('.npz'):
            print('---------> Reading caliop file: %s' %file)

            dataset = np.load(caliop_extracted_location + '/' + year + '/' + caliop_sub_folder + '/' + file)

            aerosol_type = dataset['caliop_v4_aerosol_type']
            feature_type = dataset['feature_type']
            altitude = dataset['orbit_l2_altitude']
            latitude = dataset['orbit_l2_latitude']
            longitude = dataset['orbit_l2_longitude']
            tropopause_altitude = dataset['orbit_l2_tropopause_height']
            utc_time = file[35:54]

            ash_mask = np.zeros((aerosol_type.shape))
            ash_mask[(feature_type == 4) & (aerosol_type == 2)] = 1

            for i in range(ash_mask.shape[1]):
                if np.sum(ash_mask[:, i]) > 1:
                    thickness_i, ash_height_i = calculate_ash_mask_thickness(ash_mask[:, i], altitude)
                    latitude_i = latitude[i]
                    longitude_i = longitude[i]
                    tropopause_altitude_i = tropopause_altitude[i]

                    utc_time_all.append(utc_time)
                    latitude_all.append(latitude_i)
                    longitude_all.append(longitude_i)
                    thickness_all.append(thickness_i)
                    ash_height_all.append(ash_height_i)
                    troppause_altitude_all.append(tropopause_altitude_i)

                    print(latitude_i, longitude_i, thickness_i, ash_height_i)

df = pd.DataFrame({
    'utc_time': utc_time_all,  # 'yyyy-mm-ddThh:mm:ssZ'
    'latitude': latitude_all,
    'longitude': longitude_all,
    'thickness': [','.join(map(str, t)) for t in thickness_all],
    'ash_height': [','.join(map(str, t)) for t in ash_height_all],
    'tropopause_altitude': troppause_altitude_all
})

df.to_csv(save_location + '/' + year + '_thickness.csv', index=False)



