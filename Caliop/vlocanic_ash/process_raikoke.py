#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    process_raikoke.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        21/09/2022 22:13

from Caliop.caliop import Caliop_hdf_reader
import scipy.integrate as integrate
import matplotlib.pyplot as plt
import numpy as np
import csv
import os

# CALIOP level-2 data directory
data_folder = './raikoke_data/'
save_folder = './raikoke_figure/'

ash_occurrence_matrix = np.zeros(399)
ash_mask_all = np.zeros((399,1))
ash_backscatter_matrix = np.zeros((399,1))
ash_backscatter_matrix[:] = np.nan
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

        ash_mask = np.zeros((caliop_v4_aerosol_type.shape))
        ash_mask[(feature_type == 4) & (caliop_v4_aerosol_type == 2)] = 1

        request.plot_2d_map(x=orbit_l2_latitude, y=orbit_l2_altitude, z=total_attenuated_backscatter_532,
                            title='Total Backscatter Coefficient 532',
                            save_str=save_folder + 'Total_Attenuated_Backscatter_532_%s.png' % caliop_l2_filename[0:-4])

        total_attenuated_backscatter_532_ash = np.copy(total_attenuated_backscatter_532)
        total_attenuated_backscatter_532_ash[ash_mask<1] = np.nan

        request.plot_2d_map(x=orbit_l2_latitude, y=orbit_l2_altitude, z=total_attenuated_backscatter_532_ash,
                            title='Total Backscatter Coefficient 532',
                            save_str=save_folder + 'Total_Attenuated_Backscatter_532_%s_ash.png' % caliop_l2_filename[0:-4])

        ash_mask_all = np.hstack((ash_mask_all, ash_mask))
        ash_backscatter_matrix = np.hstack((ash_backscatter_matrix, total_attenuated_backscatter_532_ash))

        for k in range(ash_mask.shape[1]):
            mask_profile = ash_mask[:,k]
            index = np.where(mask_profile > 0)[0]

            if len(index)>1:
                print('ash altitude is: %s'% orbit_l2_altitude[index])

                diff_list = index[1:] - index[0:-1]
                diff_list_index = np.where(diff_list>3)[0]
                if len(diff_list_index) > 0:
                    print('------ there are two ash layers:')
                    print('------ ', orbit_l2_altitude[index[0]:index[diff_list_index[0]]+1])
                    print('------ ', orbit_l2_altitude[index[diff_list_index[0]+1]:index[-1]+1])
                    layer_1 = orbit_l2_altitude[index[0]:index[diff_list_index[0]]+1]
                    layer_2 = orbit_l2_altitude[index[diff_list_index[0]+1]:index[-1]+1]
                    layer_1_thick = layer_1[0] - layer_1[-1]
                    layer_2_thick = layer_2[0] - layer_2[-1]
                    ash_thickness.append(layer_1_thick)
                    ash_thickness.append(layer_2_thick)
                    print('layer 1 thickness is %s' % layer_1_thick)
                    print('layer 2 thickness is %s' % layer_2_thick)
                else:
                    layer_thick = orbit_l2_altitude[index[0]] - orbit_l2_altitude[index[-1]]
                    ash_thickness.append(layer_thick)
                    print('layer thickness is %s' % layer_thick)
            else:
                pass

fig, ax = plt.subplots(figsize=(8, 5))
plt.plot(ash_thickness, lw=3, color='red', label='ash')
plt.title('CALIOP - Ash Thickness', fontsize=15)
for tick in ax.xaxis.get_major_ticks():
    tick.label.set_fontsize(12)
for tick in ax.yaxis.get_major_ticks():
    tick.label.set_fontsize(12)
# plt.xlabel('Stratospheric volcanic ash thickness [km]', fontsize=15)
# plt.ylabel('PDF', fontsize=15)
plt.legend(fontsize=15)
plt.tight_layout()
plt.savefig(save_folder + 'CALIOP_ash_thickness_linear.png')
plt.close()

fig, ax = plt.subplots(figsize=(6.5, 5))
plt.hist(ash_thickness, bins=30, color='#0504aa', alpha=0.7)
plt.title('CALIOP - Ash Thickness (Example of Raikoke Eruption)', fontsize=15)
for tick in ax.xaxis.get_major_ticks():
    tick.label.set_fontsize(12)
for tick in ax.yaxis.get_major_ticks():
    tick.label.set_fontsize(12)
plt.xlabel('Stratospheric volcanic ash thickness [km]', fontsize=15)
plt.ylabel('Number of Retrievals', fontsize=15)
# plt.legend(fontsize=15)
plt.tight_layout()
plt.savefig(save_folder + 'CALIOP_ash_thickness.png')
plt.close()


ash_occurrence_matrix = np.sum(ash_mask_all, axis = 1)
ash_backscatter_mean = np.nanmean(ash_backscatter_matrix, axis=1)
ash_backscatter_mean = ash_backscatter_mean * 1.e3

fig, ax = plt.subplots(figsize=(5, 8))
plt.plot(ash_occurrence_matrix, orbit_l2_altitude, lw=3, color='red', label='ash')
plt.title('CALIOP - Number of valid retrievals', fontsize=15)

for tick in ax.xaxis.get_major_ticks():
    tick.label.set_fontsize(12)
for tick in ax.yaxis.get_major_ticks():
    tick.label.set_fontsize(12)

plt.xlabel('Number of retrievals', fontsize=12)
plt.ylabel('Height [km]', fontsize=12)
plt.xlim([0., 150.])
plt.ylim([0., 20.])
plt.legend(fontsize=15)
plt.tight_layout()
plt.savefig(save_folder + 'CALIOP_dust_occurrence.png')
plt.close()
#
fig, ax = plt.subplots(figsize=(5, 8))
plt.plot(ash_backscatter_mean, orbit_l2_altitude, lw=3, color='red', label='ash')
# plt.plot(dusty_marine_backscatter_mask, orbit_l2_altitude, lw=3, color='cyan', label='dusty marine')
# plt.plot(smoke_backscatter_mask, orbit_l2_altitude, lw=3, color='black', label='smoke')
plt.title('CALIOP - Averaged Backscatter', fontsize=15)

for tick in ax.xaxis.get_major_ticks():
    tick.label.set_fontsize(12)
for tick in ax.yaxis.get_major_ticks():
    tick.label.set_fontsize(12)

plt.xlabel('Part. backsc. coeff. [Mm$^{-1}$sr$^{-1}$]', fontsize=12)
plt.ylabel('Height [km]', fontsize=12)
plt.xlim([0., 20])
plt.ylim([0., 20.])
plt.legend(fontsize=15)
plt.tight_layout()
plt.savefig(save_folder + 'CALIOP_avg_backscatter.png')


