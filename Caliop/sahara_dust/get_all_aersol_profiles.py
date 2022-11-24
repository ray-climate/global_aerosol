#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    get_all_aersol_profiles.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        30/08/2022 15:44

from Caliop.caliop import Caliop_hdf_reader
import scipy.integrate as integrate
import numpy as np
import csv
import os

# CALIOP level-2 data directory
data_folder = './L2_aerosol/'
save_folder = './L2_aerosol_figures/'

clean_stratosphere_alt_min = 10
clean_stratosphere_threshold = 1
aod_threshold = 0.05

# lat/lon boundary of the Sahara dust event
lat_min = 1.
lat_max = 45.
lon_min = -57.
lon_max = 15.

backscatter_profiles = []

index = 0

for caliop_l2_filename in os.listdir((data_folder)):
    if caliop_l2_filename.endswith('.hdf'):

        print('Start interpreting %s..................'%caliop_l2_filename)

        request = Caliop_hdf_reader()

        orbit_total_attenuated_backscatter_532 = request._get_calipso_data\
            (filename=data_folder + caliop_l2_filename,
             variable='Total_Backscatter_Coefficient_532')

        orbit_extinction_coefficient_532 = request._get_calipso_data\
            (filename=data_folder + caliop_l2_filename,
             variable='Extinction_Coefficient_532')

        orbit_l2_altitude = request.get_altitudes\
            (filename=data_folder + caliop_l2_filename)
        orbit_l2_latitude = request._get_latitude\
            (filename=data_folder + caliop_l2_filename)
        orbit_l2_longitude = request._get_longitude\
            (filename=data_folder + caliop_l2_filename)

        # test_array = orbit_extinction_coefficient_532.data

#
#         Total_Attenuated_Backscatter_532_filtered = np.copy(Total_Attenuated_Backscatter_532)
#
#         Extinction_Coefficient_532[Extinction_Coefficient_532 < 0.] = 0.
#         Extinction_Coefficient_532_filtered = np.copy(Extinction_Coefficient_532)
#
#         orbit_aod = - np.trapz(Extinction_Coefficient_532_filtered, x=L2_altitude, axis=0)
#
#         Total_Attenuated_Backscatter_532_filtered = Total_Attenuated_Backscatter_532_filtered[:,
#                                                     (orbit_aod > aod_threshold) & (np.mean(
#                                                         Extinction_Coefficient_532[
#                                                             L2_altitude > clean_stratosphere_alt_min],
#                                                         axis=0) < clean_stratosphere_threshold)]
#
#         Total_Attenuated_Backscatter_532_filtered = Total_Attenuated_Backscatter_532_filtered * 1.e3
#         Total_Attenuated_Backscatter_532_filtered[Total_Attenuated_Backscatter_532_filtered<0] = np.nan
#
#         Extinction_Coefficient_532_filtered = Extinction_Coefficient_532_filtered * 1.e3
#
#         Extinction_Coefficient_532_filtered = Extinction_Coefficient_532_filtered[:,
#                                                     (orbit_aod > aod_threshold) & (np.mean(
#                                                         Extinction_Coefficient_532[
#                                                             L2_altitude > clean_stratosphere_alt_min],
#                                                         axis=0) < clean_stratosphere_threshold)]
#
#         if index > 0:
#             backscatter_profiles = np.hstack((backscatter_profiles, Total_Attenuated_Backscatter_532_filtered))
#         else:
#             backscatter_profiles = np.copy(Total_Attenuated_Backscatter_532_filtered)
#
#         index = index + 1
#
# import matplotlib.pyplot as plt
# fig, ax = plt.subplots(figsize=(5, 8))
# # for i in range(backscatter_profiles.shape[1]):
# #     plt.plot(backscatter_profiles[:, i], L2_altitude)
# plt.plot(np.nanmean(backscatter_profiles, axis=1), L2_altitude)
#
# for tick in ax.xaxis.get_major_ticks():
#     tick.label.set_fontsize(12)
# for tick in ax.yaxis.get_major_ticks():
#     tick.label.set_fontsize(12)
#
# plt.xlabel('Part. backsc. coeff. [Mm$^{-1}$sr$^{-1}$]', fontsize=15)
# plt.ylabel('Height [km]', fontsize=15)
# plt.xlim([0., 100])
# plt.ylim([0., 15.])
# #
# # from pydlc import dense_lines
# #
# # fig, axs = plt.subplots(1, 2, figsize=(8, 3), sharey=True, sharex=True)
# # axs[0].plot(L2_altitude, np.array(backscatter_profiles[:,500:1000]), lw=1)  # this is slow and cluttered
# # axs[0].set_title('Line Chart')
# # axs[0].set_ylim([0., 50.])
# #
# # backscatter_profiles_list = backscatter_profiles.T.tolist()
# # im = dense_lines(backscatter_profiles_list[500:1000], x=L2_altitude, ax=axs[1], cmap='magma')  # this is fast and clean
# # axs[1].set_title('Density Lines Chart')
# # axs[1].set_ylim([0., 50.])
# # fig.colorbar(im)
# # fig.tight_layout()
#
# import matplotlib.pyplot as plt
# fig, ax = plt.subplots(figsize=(5, 8))
# # for i in range(backscatter_profiles.shape[1]):
# #     plt.plot(backscatter_profiles[:, i], L2_altitude)
# plt.plot(np.nanmean(Extinction_Coefficient_532_filtered, axis=1), L2_altitude)
#
# for tick in ax.xaxis.get_major_ticks():
#     tick.label.set_fontsize(12)
# for tick in ax.yaxis.get_major_ticks():
#     tick.label.set_fontsize(12)
#
# plt.xlabel('Extinction', fontsize=15)
# plt.ylabel('Height [km]', fontsize=15)
# plt.xlim([0., 100])
# plt.ylim([0., 15.])
#
#
# plt.show()
