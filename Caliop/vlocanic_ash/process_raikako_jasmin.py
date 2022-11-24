#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    process_raikako_jasmin.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        26/09/2022 11:16

from Caliop.caliop import Caliop_hdf_reader
import scipy.integrate as integrate
import matplotlib.pyplot as plt
import numpy as np
import csv
import os

# CALIOP level-2 data directory
data_folder = './raikoke_data/'
save_txt_folder = './raikoke_txt/'

try:
    os.stat(save_txt_folder)
except:
    os.mkdir(save_txt_folder)

ash_lat = []
ash_lon = []
ash_index = []
# 1 for single layer ash
# 2 for double layer, top layer
# 3 for double layer, bottom layer
# 4 for double layer, combined
ash_thickness = []

for caliop_l2_filename in os.listdir((data_folder)):
    if (caliop_l2_filename.endswith('.hdf')) & ('05kmAPro' in caliop_l2_filename):

        request = Caliop_hdf_reader()

        (caliop_v4_aerosol_type, feature_type) = request._get_feature_classification(
            filename=data_folder + caliop_l2_filename,
            variable='Atmospheric_Volume_Description')

        total_attenuated_backscatter_532 = request._get_calipso_data(
            filename=data_folder + caliop_l2_filename,
            variable='Total_Backscatter_Coefficient_532')

        orbit_l2_Profile_ID = request._get_profile_id(
            filename=data_folder + caliop_l2_filename)

        orbit_l2_altitude = request.get_altitudes(
            filename=data_folder + caliop_l2_filename)

        orbit_l2_latitude = request._get_latitude(
            filename=data_folder + caliop_l2_filename)

        orbit_l2_longitude = request._get_longitude(
            filename=data_folder + caliop_l2_filename)

        ash_mask = np.zeros((caliop_v4_aerosol_type.shape))
        ash_mask[(feature_type == 4) & (caliop_v4_aerosol_type == 2)] = 1

        for k in range(ash_mask.shape[1]):
            mask_profile = ash_mask[:,k]
            index = np.where(mask_profile > 0)[0]

            if len(index)>1:
                print('---------> Ash altitude at (%.2f, %.2f):' %(orbit_l2_latitude[k], orbit_l2_longitude[k]))
                print('---------> %s' %orbit_l2_altitude[index])

                diff_list = index[1:] - index[0:-1]
                diff_list_index = np.where(diff_list>3)[0]

                if len(diff_list_index) > 0:

                    layer_1 = orbit_l2_altitude[index[0]:index[diff_list_index[0]]+1]
                    layer_2 = orbit_l2_altitude[index[diff_list_index[0]+1]:index[-1]+1]

                    if (len(layer_1) > 1) & (len(layer_2) > 1):

                        print('---------> There are two ash layers:')
                        print('---------> First layer:', orbit_l2_altitude[index[0]:index[diff_list_index[0]] + 1])
                        print('---------> Second layer:', orbit_l2_altitude[index[diff_list_index[0] + 1]:index[-1] + 1])

                        layer_1_thick = layer_1[0] - layer_1[-1] + (layer_1[0] - layer_1[1]) # boundary effect
                        layer_2_thick = layer_2[0] - layer_2[-1] + (layer_2[0] - layer_2[1]) # boundary effect

                        layer_combined = layer_1_thick + layer_2_thick

                        print('---------> Layer 1 thickness is %s' % layer_1_thick)
                        print('---------> Layer 2 thickness is %s' % layer_2_thick)

                        # save layer info.
                        ash_lat.append(orbit_l2_latitude[k])
                        ash_lon.append(orbit_l2_longitude[k])
                        ash_index.append(2)
                        ash_thickness.append(layer_1_thick)

                        ash_lat.append(orbit_l2_latitude[k])
                        ash_lon.append(orbit_l2_longitude[k])
                        ash_index.append(3)
                        ash_thickness.append(layer_2_thick)

                        ash_lat.append(orbit_l2_latitude[k])
                        ash_lon.append(orbit_l2_longitude[k])
                        ash_index.append(4)
                        ash_thickness.append(layer_combined)


                    elif (len(layer_1) > 1) & (len(layer_2) <= 1):
                        print('---------> This is a single ash layer, filtered from double layers:')
                        layer_thick = layer_1[0] - layer_1[-1] + (layer_1[0] - layer_1[1])  # boundary effect
                        print('---------> Layer thickness is %s' % layer_thick)

                        # save layer info.
                        ash_lat.append(orbit_l2_latitude[k])
                        ash_lon.append(orbit_l2_longitude[k])
                        ash_index.append(1)
                        ash_thickness.append(layer_thick)

                    elif (len(layer_1) <= 1) & (len(layer_2) > 1):
                        print('---------> This is a single ash layer, filtered from double layers:')
                        layer_thick = layer_2[0] - layer_2[-1] + (layer_2[0] - layer_2[1])  # boundary effect
                        print('---------> Layer thickness is %s' % layer_thick)

                        # save layer info.
                        ash_lat.append(orbit_l2_latitude[k])
                        ash_lon.append(orbit_l2_longitude[k])
                        ash_index.append(1)
                        ash_thickness.append(layer_thick)

                    else:
                        print('---------> Profile not counted for ash thickness.')
                else:
                    print('---------> This is a single ash layer:')
                    layer_thick = orbit_l2_altitude[index[0]] - orbit_l2_altitude[index[-1]]

                    print('---------> Layer thickness is %s' % layer_thick)

                    # save layer info.
                    ash_lat.append(orbit_l2_latitude[k])
                    ash_lon.append(orbit_l2_longitude[k])
                    ash_index.append(1)
                    ash_thickness.append(layer_thick)

            else:
                pass

        with open(save_txt_folder + '%s_ash.csv' % caliop_l2_filename[0:-4], "w") as output:
            writer = csv.writer(output, lineterminator='\n')
            writer.writerow(('Latitude', 'Longitude', 'Layer_index', 'Thickness'))
            for i in range(len(ash_lat)):
                writer.writerow((ash_lat[i], ash_lon[i], ash_index[i], ash_thickness[i]))




