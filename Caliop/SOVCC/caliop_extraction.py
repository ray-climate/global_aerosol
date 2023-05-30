#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    caliop_extraction.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        30/05/2023 12:51

import os

# caliop location on CEDA
caliop_location = '/gws/nopw/j04/eo_shared_data_vol1/satellite/calipso/APro5km'
# location to save ash only data
save_location = './caliop_ash_data_extraction/'

# create save_location folder if not exist
try:
    os.stat(save_location)
except:
    os.mkdir(save_location)

# loop through all the sub folder in caliop_location
for caliop_sub_folder in os.listdir(caliop_location):
    for caliop_sub_sub_folder in os.listdir(caliop_location + '/' + caliop_sub_folder):
        for caliop_file in os.listdir(caliop_location + '/' + caliop_sub_folder + '/' + caliop_sub_sub_folder):
            if caliop_file.endswith('.hdf'):
                print('---------> Reading file: %s' % caliop_file)
                # extract ash only data
                # os.system('python caliop_ash_extraction.py %s %s %s' % (caliop_location + '/' + caliop_sub_folder + '/' + caliop_sub_sub_folder + '/' + caliop_file, save_location, caliop_file))
            else:
                pass



