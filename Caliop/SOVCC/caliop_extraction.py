#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    caliop_extraction.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        30/05/2023 12:51

import sys
import os

# set year from command line arugment
year = sys.argv[1]

# caliop location on CEDA
caliop_location = '/gws/nopw/j04/eo_shared_data_vol1/satellite/calipso/APro5km'
# location to save ash only data
save_location = './caliop_ash_data_extraction/'

# create save_location folder if not exist
try:
    os.stat(save_location)
except:
    os.mkdir(save_location)

# loop through all the sub year folder in caliop_location
for caliop_sub_folder in os.listdir(caliop_location + '/' + year):
    for files in os.listdir(caliop_location + '/' + year + '/' + caliop_sub_folder):
        if files.endswith('.hdf'):
            print('---------> Reading caliop file: %s' %files)
            # read caliop hdf file
            caliop_file = caliop_location + '/' + year + '/' + caliop_sub_folder + '/' + files
            # extract ash layer only
            print(caliop_file)
        else:
            pass