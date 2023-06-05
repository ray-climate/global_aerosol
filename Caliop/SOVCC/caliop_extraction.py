#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    caliop_extraction.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        30/05/2023 12:51

import sys
sys.path.append('../../')

from Caliop.caliop import Caliop_hdf_reader
import numpy as np
import sys
import os

# set year from command line arugment
year = sys.argv[1]

# caliop location on CEDA
caliop_location = '/gws/nopw/j04/eo_shared_data_vol1/satellite/calipso/APro5km'
# location to save ash only data
save_location = './caliop_ash_data_extraction'

# create save_location folder if not exist
try:
    os.stat(save_location)
except:
    os.mkdir(save_location)

# loop through all the sub year folder in caliop_location
for caliop_sub_folder in os.listdir(caliop_location + '/' + year):

    try:
        os.stat(save_location + '/' + year)
    except:
        os.mkdir(save_location + '/' + year)

    for files in os.listdir(caliop_location + '/' + year + '/' + caliop_sub_folder):
        if files.endswith('.hdf'):
            print('---------> Reading caliop file: %s' %files)
            # read caliop hdf file
            caliop_file = caliop_location + '/' + year + '/' + caliop_sub_folder + '/' + files
            # extract ash layer only
            request = Caliop_hdf_reader()
            #
            (caliop_v4_aerosol_type, feature_type) = request._get_feature_classification(filename=caliop_file, variable='Atmospheric_Volume_Description')
            extinction = request._get_calipso_data(filename=caliop_file, variable='Extinction_Coefficient_532')
            orbit_l2_altitude = request.get_altitudes(filename=caliop_file)
            orbit_l2_latitude = request._get_latitude(filename=caliop_file)
            orbit_l2_longitude = request._get_longitude(filename=caliop_file)
            orbit_l2_tropopause_height = request._get_tropopause_height(filename=caliop_file)
            #
            save_sub_location = save_location + '/' + year + '/' + caliop_sub_folder + '/'
            try:
                os.stat(save_sub_location)
            except:
                os.mkdir(save_sub_location)

            # save all the variables as a numpy file
            save_file_name = save_sub_location + files[:-4]
            np.savez(save_file_name,
                     caliop_v4_aerosol_type=caliop_v4_aerosol_type,
                     feature_type=feature_type,
                     extinction=extinction,
                     orbit_l2_altitude=orbit_l2_altitude,
                     orbit_l2_latitude=orbit_l2_latitude,
                     orbit_l2_longitude=orbit_l2_longitude,
                     orbit_l2_tropopause_height=orbit_l2_tropopause_height)

            # for i in range(len(orbit_l2_latitude)):
            #     # print(len(orbit_l2_latitude))
            #     print(i, orbit_l2_latitude[i], orbit_l2_longitude[i])
            # quit()
        else:
            pass