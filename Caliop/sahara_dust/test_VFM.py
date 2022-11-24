#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    test_VFM.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        31/08/2022 12:39

from Caliop.caliop import Caliop_hdf_reader
import scipy.integrate as integrate
import numpy as np
import csv
import os

# CALIOP level-2 data directory
data_folder = './updated_data/'
save_folder = './L2_aerosol_subtype_figures/'

for caliop_l2_filename in os.listdir((data_folder)):
    if (caliop_l2_filename.endswith('.hdf')) & ('05kmAPro' in caliop_l2_filename):
        print(caliop_l2_filename)
        request = Caliop_hdf_reader()

        (caliop_v4_aerosol_type, feature_type) = request._get_feature_classification(
            filename=data_folder + caliop_l2_filename,
            variable='Atmospheric_Volume_Description')

        orbit_l2_Profile_ID = request._get_profile_id(
            filename=data_folder + caliop_l2_filename)

        orbit_l2_altitude = request.get_altitudes(
            filename=data_folder + caliop_l2_filename)

        troposhperic_aerosol_type = np.copy(caliop_v4_aerosol_type)
        troposhperic_aerosol_type[feature_type == 4] = 0

        aerosol_type_text = "0 = not determined \n" \
                            "1 = clean marine\n" \
                            "2 = dust \n" \
                            "3 = polluted continental / smoke \n" \
                            "4 = clean continental \n" \
                            "5 = polluted dust \n" \
                            "6 = elevated smoke \n" \
                            "7 = dusty marine"

        request.plot_aerosol_subtype_classification(
            x=orbit_l2_Profile_ID,
            y=orbit_l2_altitude,
            z=troposhperic_aerosol_type,
            title='aerosol subtype classification',
            text = aerosol_type_text,
            save_str= save_folder + caliop_l2_filename[0:-4]+'_trop_aerosol_subtype.png')


