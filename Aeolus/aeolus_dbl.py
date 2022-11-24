#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    aeolus_dbl.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        14/09/2022 13:06

from numpy import hstack, vstack
import matplotlib.pyplot as plt
import numpy as np
import sys
import os
os.putenv('CODA_DEFINITION', '/Users/rs/Projects/global_aerosol/Aeolus/coda/')
sys.path.append('/Users/rs/Projects/global_aerosol/Aeolus/coda/install/lib/python3.9/site-packages')
import coda

def GetAeolusFromDBL(file_dir, dbl_filename, save_dir):

    print(dbl_filename)
    codaid = coda.open(file_dir + dbl_filename)

    # product = coda.fetch(codaid, 'sca_optical_properties', 0, 'sca_optical_properties_mid_bins', 0)
    # print(product)
    # quit()

    if coda.get_field_available(codaid, 'sca_optical_properties'):
        sca_backscatter = coda.fetch(codaid, 'sca_optical_properties', -1, 'sca_optical_properties_mid_bins', -1, 'backscatter')
        sca_backscatter = vstack(sca_backscatter).T[::-1, :]
        print('size of backscatter data is: ', sca_backscatter.shape)

    if coda.get_field_available(codaid, 'sca_optical_properties'):

        latitude_mid_bin = coda.fetch(codaid, 'sca_optical_properties', -1, 'geolocation_middle_bins', -1,
                                                  'latitude')
        latitude_mid_bin = vstack(latitude_mid_bin).T[::-1, :]

        longitude_mid_bin = coda.fetch(codaid, 'sca_optical_properties', -1, 'geolocation_middle_bins', -1,
                                                  'longitude')
        altitude_mid_bin = coda.fetch(codaid, 'sca_optical_properties', -1, 'geolocation_middle_bins', -1,
                                      'altitude')
        altitude_mid_bin = vstack(altitude_mid_bin).T[::-1, :]

        longitude_mid_bin = vstack(longitude_mid_bin).T[::-1, :]
        print("size of middle-bin geolocation is: ", longitude_mid_bin.shape)

        latitude_mid_bin[latitude_mid_bin < 0] = np.nan
        longitude_mid_bin[longitude_mid_bin < 0] = np.nan
        altitude_mid_bin[altitude_mid_bin < 0] = np.nan

    fig1, ax1 = plt.subplots(figsize=(30, 10))

    plt.pcolor(sca_backscatter, vmin=0, vmax=10., cmap='rainbow')
    plt.xlabel('Profile', fontsize=26)
    plt.ylabel('Bins', fontsize=26)

    for tick in ax1.xaxis.get_major_ticks():
        tick.label.set_fontsize(20)
    for tick in ax1.yaxis.get_major_ticks():
        tick.label.set_fontsize(20)

    plt.savefig(save_dir + '%s_backscatter.png'%dbl_filename[0:-4])
    plt.close()

    return altitude_mid_bin, latitude_mid_bin, longitude_mid_bin,

    # if coda.get_field_available(codaid, 'scene_classification'):
    #
    #     topclber = coda.fetch(codaid, 'scene_classification', -1, 'aladin_cloud_flag', 'topclber')
    #     DownClBER = coda.fetch(codaid, 'scene_classification', -1, 'aladin_cloud_flag', 'DownClBER')
    #     ClSR = coda.fetch(codaid, 'scene_classification', -1, 'aladin_cloud_flag', 'ClSR')
    #     ClRH = coda.fetch(codaid, 'scene_classification', -1, 'aladin_cloud_flag', 'ClRH')
    #     group_height_index = coda.fetch(codaid, 'scene_classification', -1, 'height_bin_index')
    #
    #     scene_classification = DownClBER + 2 * DownClBER + 4 * ClSR + 8 * ClRH
    #     cloud_array = np.zeros((sca_backscatter.shape[0] + 1, len(scene_classification)))
    #
    #     for i in range(cloud_array.shape[1]):
    #         cloud_array[group_height_index[i], i] = scene_classification[i]
    #
    #     print('size of scene classification flag is: ', cloud_array.shape)