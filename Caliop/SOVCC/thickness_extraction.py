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
            ash_mask = np.zeros((aerosol_type.shape))
            ash_mask[(feature_type == 4) & (aerosol_type == 2)] = 1
            print(latitude.shape)
            # print(ash_mask[ash_mask > 0])
            print(ash_mask[ash_mask > 0].shape)