#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    dust_profile_visualisation.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        12/09/2022 13:16

from Caliop.caliop import Caliop_hdf_reader
import scipy.integrate as integrate
import matplotlib.pyplot as plt
import numpy as np
import csv
import os

# CALIOP level-2 data directory
data_folder = './updated_data/'
save_folder = './dust_profile_visualisation/'

dust_occurrence_matrix = np.zeros(399)
dusty_marine_occurrence_matrix = np.zeros(399)
smoke_occurrence_matrix = np.zeros(399)

dust_backscatter_matrix = np.zeros(399)
dust_backscatter_matrix[:] = np.nan
dusty_marine_backscatter_matrix = np.zeros(399)
dusty_marine_backscatter_matrix[:] = np.nan
smoke_backscatter_matrix = np.zeros(399)
smoke_backscatter_matrix[:] = np.nan

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

        troposhperic_aerosol_type = np.copy(caliop_v4_aerosol_type)
        troposhperic_aerosol_type[feature_type == 4] = 0

        dust_mask = np.zeros((troposhperic_aerosol_type.shape))
        dust_mask[troposhperic_aerosol_type == 2] = 1. # CALIOP aerosol type=2 equals to dust
        dust_mask = np.sum(dust_mask, axis = 1)
        dust_occurrence_matrix = dust_occurrence_matrix + dust_mask

        dusty_marine_mask = np.zeros((troposhperic_aerosol_type.shape))
        dusty_marine_mask[troposhperic_aerosol_type == 7] = 1.  # CALIOP aerosol type=7 equals to dusty marine
        dusty_marine_mask = np.sum(dusty_marine_mask, axis=1)
        dusty_marine_occurrence_matrix = dusty_marine_occurrence_matrix + dusty_marine_mask

        smoke_mask = np.zeros((troposhperic_aerosol_type.shape))
        smoke_mask[troposhperic_aerosol_type == 6] = 1.  # CALIOP aerosol type=6 equals to dusty marine
        smoke_mask = np.sum(smoke_mask, axis=1)
        smoke_occurrence_matrix = smoke_occurrence_matrix + smoke_mask


        dust_backscatter_mask = np.zeros((total_attenuated_backscatter_532.shape))
        dust_backscatter_mask[:] = np.nan
        dust_backscatter_mask[(troposhperic_aerosol_type == 2) & (total_attenuated_backscatter_532 > 0)] = \
            total_attenuated_backscatter_532[(troposhperic_aerosol_type == 2) & (total_attenuated_backscatter_532 > 0)]
        dust_backscatter_mask = np.nanmean(dust_backscatter_mask, axis=1)
        dust_backscatter_mask = np.vstack((dust_backscatter_matrix, dust_backscatter_mask))
        dust_backscatter_mask = np.nanmean(dust_backscatter_mask, axis=0)

        dusty_marine_backscatter_mask = np.zeros((total_attenuated_backscatter_532.shape))
        dusty_marine_backscatter_mask[:] = np.nan
        dusty_marine_backscatter_mask[(troposhperic_aerosol_type == 7) & (total_attenuated_backscatter_532 > 0)] = \
            total_attenuated_backscatter_532[(troposhperic_aerosol_type == 7) & (total_attenuated_backscatter_532 > 0)]
        dusty_marine_backscatter_mask = np.nanmean(dusty_marine_backscatter_mask, axis=1)
        dusty_marine_backscatter_mask = np.vstack((dusty_marine_backscatter_matrix, dusty_marine_backscatter_mask))
        dusty_marine_backscatter_mask = np.nanmean(dusty_marine_backscatter_mask, axis=0)

        smoke_backscatter_mask = np.zeros((total_attenuated_backscatter_532.shape))
        smoke_backscatter_mask[:] = np.nan
        smoke_backscatter_mask[(troposhperic_aerosol_type == 6) & (total_attenuated_backscatter_532 > 0)] = \
            total_attenuated_backscatter_532[(troposhperic_aerosol_type == 6) & (total_attenuated_backscatter_532 > 0)]
        smoke_backscatter_mask = np.nanmean(smoke_backscatter_mask, axis=1)
        smoke_backscatter_mask = np.vstack((smoke_backscatter_matrix, smoke_backscatter_mask))
        smoke_backscatter_mask = np.nanmean(smoke_backscatter_mask, axis=0)

dust_backscatter_mask = dust_backscatter_mask * 1.e3
dusty_marine_backscatter_mask = dusty_marine_backscatter_mask * 1.e3
smoke_backscatter_mask = smoke_backscatter_mask * 1.e3

fig, ax = plt.subplots(figsize=(5, 8))
plt.plot(dust_occurrence_matrix, orbit_l2_altitude, lw=3, color='orange', label='dust')
plt.plot(dusty_marine_occurrence_matrix, orbit_l2_altitude, lw=3, color='cyan', label='dusty marine')
plt.plot(smoke_occurrence_matrix, orbit_l2_altitude, lw=3, color='black', label='smoke')
plt.plot(dust_occurrence_matrix +
         dusty_marine_occurrence_matrix +
         smoke_occurrence_matrix,
         orbit_l2_altitude, lw=3, color='red', label='total')
plt.title('CALIOP - Number of dust retrievals', fontsize=15)

for tick in ax.xaxis.get_major_ticks():
    tick.label.set_fontsize(12)
for tick in ax.yaxis.get_major_ticks():
    tick.label.set_fontsize(12)

plt.xlabel('Number of retrievals', fontsize=12)
plt.ylabel('Height [km]', fontsize=12)
plt.xlim([0., 15000.])
plt.ylim([0., 20.])
plt.legend(fontsize=15)
plt.tight_layout()
plt.savefig(save_folder + 'CALIOP_dust_occurrence.png')
plt.close()

fig, ax = plt.subplots(figsize=(5, 8))
plt.plot(dust_backscatter_mask, orbit_l2_altitude, lw=3, color='orange', label='dust')
plt.plot(dusty_marine_backscatter_mask, orbit_l2_altitude, lw=3, color='cyan', label='dusty marine')
plt.plot(smoke_backscatter_mask, orbit_l2_altitude, lw=3, color='black', label='smoke')
plt.title('CALIOP - Averaged Backscatter', fontsize=15)

for tick in ax.xaxis.get_major_ticks():
    tick.label.set_fontsize(12)
for tick in ax.yaxis.get_major_ticks():
    tick.label.set_fontsize(12)

plt.xlabel('Part. backsc. coeff. [Mm$^{-1}$sr$^{-1}$]', fontsize=12)
plt.ylabel('Height [km]', fontsize=12)
plt.xlim([0., 70])
plt.ylim([0., 20.])
plt.legend(fontsize=15)
plt.tight_layout()
plt.savefig(save_folder + 'CALIOP_avg_backscatter.png')

