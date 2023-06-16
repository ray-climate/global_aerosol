#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    ash_thickness_extraction_v2.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        15/06/2023 14:54

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
caliop_extracted_location = './caliop_ash_data_extraction_extended_v1'
save_location = './ash_thickness_data_extraction_v1'

# create save_location folder if not exist
try:
    os.stat(save_location)
except:
    os.mkdir(save_location)

def calculate_ash_mask_thickness(ash_mask, altitude, extinction):
    """
    Calculates thickness of ash mask based on altitude.

    Args:
        ash_mask: List of int
        altitude: List of float

    Returns:
        thicknesses: List of float
    """
    thicknesses = []  # Initialize thicknesses list
    weighted_extinctions = []  # Initialize weighted extinction list
    mean_heights = []
    # Convert ash_mask and altitude to numpy arrays
    ash_mask = np.array(ash_mask)
    altitude = np.array(altitude)
    extinction = np.array(extinction)

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
                extinction_mask = extinction[seq]
                altitude_mask = altitude[seq]
                altitude_diff = -np.diff(altitude_mask)
                altitude_diff = np.append(altitude_diff, altitude_diff[-1])

                weighted_extinctions.append(np.sum(altitude_diff * extinction_mask) / thickness)
                mean_heights.append(np.mean([max_altitude, min_altitude]))

    return thicknesses, mean_heights, weighted_extinctions


# loop through all the sub year folder in caliop_location
# location parameter
utc_time_all = []
latitude_all = []
longitude_all = []
altitude_all = []
# layer parameters
thickness_all = []
ash_height_all = []
troppause_altitude_all = []
# optical parameters
extinction_all = []
backscatter_all = []
depolarisation_all = []
# type parameters
aerosol_type_all = []
feature_type_all = []

for caliop_sub_folder in os.listdir(caliop_extracted_location + '/' + year):

    print('---------> Reading caliop date: %s' %caliop_sub_folder)

    for file in os.listdir(caliop_extracted_location + '/' + year + '/' + caliop_sub_folder):
        # if file.endswith('.npz') & file.starts('CAL_LID_L2_05kmAPro-Standard-V4-20.2011-06'):
        if file.endswith('.npz'):
            print('---------> Reading caliop file: %s' %file)

            dataset = np.load(caliop_extracted_location + '/' + year + '/' + caliop_sub_folder + '/' + file)

            aerosol_type = dataset['caliop_v4_aerosol_type']
            feature_type = dataset['feature_type']
            # location parameter
            utc_time = file[35:54]
            altitude = dataset['orbit_l2_altitude']
            latitude = dataset['orbit_l2_latitude']
            longitude = dataset['orbit_l2_longitude']
            # layer parameters
            tropopause_altitude = dataset['orbit_l2_tropopause_height']
            # optical parameters
            extinction = dataset['extinction']
            backscatter = dataset['backscatter']
            depolarisation = dataset['depolarisation']

            ash_mask = np.zeros((aerosol_type.shape))
            ash_mask[(feature_type == 4) & (aerosol_type == 2)] = 1

            for i in range(ash_mask.shape[1]):
                if np.sum(ash_mask[:, i]) > 1:

                    thickness_i, ash_height_i, extinction_i = calculate_ash_mask_thickness(ash_mask[:, i], altitude, extinction[:, i])
                    utc_time_all.append(utc_time)
                    latitude_i = latitude[i]
                    longitude_i = longitude[i]
                    altitude_i = np.copy(altitude)
                    tropopause_altitude_i = tropopause_altitude[i]


                    latitude_all.append(latitude_i)
                    longitude_all.append(longitude_i)
                    altitude_all.append(altitude_i)
                    thickness_all.append(thickness_i)
                    ash_height_all.append(ash_height_i)
                    troppause_altitude_all.append(tropopause_altitude_i)
                    extinction_all.append(extinction[:, i])
                    backscatter_all.append(backscatter[:, i])
                    depolarisation_all.append(depolarisation[:, i])
                    aerosol_type_all.append(aerosol_type[:, i])
                    feature_type_all.append(feature_type[:, i])


df = pd.DataFrame({
    'utc_time': utc_time_all,  # 'yyyy-mm-ddThh:mm:ssZ'
    'latitude': latitude_all,
    'longitude': longitude_all,
    'altitude': altitude_all,
    'ash_thickness': [','.join(map(str, t)) for t in thickness_all],
    'ash_height': [','.join(map(str, t)) for t in ash_height_all],
    'tropopause_altitude': troppause_altitude_all,
    'extinction': [','.join(map(str, t)) for t in extinction_all],
    'backscatter': [','.join(map(str, t)) for t in backscatter_all],
    'depolarisation': [','.join(map(str, t)) for t in depolarisation_all],
    'aerosol_type': [','.join(map(str, t)) for t in aerosol_type_all],
    'feature_type': [','.join(map(str, t)) for t in feature_type_all]
})

df.to_csv(save_location + '/' + year + '_ash_thickness.csv', index=False)



