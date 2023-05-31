#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    thickness_extraction.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        31/05/2023 10:28

import sys
sys.path.append('../../')

from Caliop.caliop import Caliop_hdf_reader
import numpy as np
import sys
import os

# set year from command line arugment
year = sys.argv[1]

# caliop location on CEDA
caliop_extracted_location = './caliop_ash_data_extraction'

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
                print(min_altitude, max_altitude)
                thickness = max_altitude - min_altitude
                thicknesses.append(thickness)

    return thicknesses

# loop through all the sub year folder in caliop_location
for caliop_sub_folder in os.listdir(caliop_extracted_location + '/' + year):

    print('---------> Reading caliop date: %s' %caliop_sub_folder)

    for file in os.listdir(caliop_extracted_location + '/' + year + '/' + caliop_sub_folder):
        if file.endswith('.npz'):
            print('---------> Reading caliop file: %s' %file)

            dataset = np.load(caliop_extracted_location + '/' + year + '/' + caliop_sub_folder + '/' + file)

            aerosol_type = dataset['caliop_v4_aerosol_type']
            feature_type = dataset['feature_type']
            altitude = dataset['orbit_l2_altitude']
            latitude = dataset['orbit_l2_latitude']
            longitude = dataset['orbit_l2_longitude']
            ash_mask = np.zeros((aerosol_type.shape))
            ash_mask[(feature_type == 4) & (aerosol_type == 2)] = 1

            for i in range(ash_mask.shape[1]):
                if np.sum(ash_mask[:, i]) > 1:
                    thickness_i = calculate_ash_mask_thickness(ash_mask[:, i], altitude)
                    print(thickness_i)


