#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    plot_aod_June19.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        07/07/2023 14:33

import sys
sys.path.append('../../')
from Caliop.caliop import Caliop_hdf_reader
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import pathlib
import sys
import csv
import os

lat_up = 40. # degree
lat_down = 0. # degree
meridional_boundary = [-60., 30.] # degree
lon_left = meridional_boundary[0]
lon_right = meridional_boundary[1]

caliop_file = '/gws/nopw/j04/eo_shared_data_vol1/satellite/calipso/APro5km/2020/2020_06_18/CAL_LID_L2_05kmAPro-Standard-V4-20.2020-06-18T15-45-38ZD.hdf'

def read_caliop_data(caliop_file_path, lat_down, lat_up, lon_left, lon_right):

    caliop_request = Caliop_hdf_reader()

    # Read data from Caliop file
    # caliop_request.get_variable_names(caliop_file_path)
    caliop_utc = np.asarray(caliop_request._get_profile_UTC(caliop_file_path))
    caliop_latitude = np.asarray(caliop_request._get_latitude(caliop_file_path))
    caliop_longitude = np.asarray(caliop_request._get_longitude(caliop_file_path))
    caliop_altitude = np.asarray(caliop_request.get_altitudes(caliop_file_path))
    caliop_AOD_532_trop = np.asarray(caliop_request._get_aod(caliop_file_path, 'Column_Optical_Depth_Tropospheric_Aerosols_532'))
    caliop_AOD_532_stra = np.asarray(caliop_request._get_aod(caliop_file_path, 'Column_Optical_Depth_Stratospheric_Aerosols_532'))
    caliop_AOD_532_total = caliop_AOD_532_trop + caliop_AOD_532_stra

    caliop_beta = np.asarray(
        caliop_request._get_calipso_data(filename=caliop_file_path, variable='Total_Backscatter_Coefficient_532'))
    caliop_alpha = np.asarray(
        caliop_request._get_calipso_data(filename=caliop_file_path, variable='Extinction_Coefficient_532'))
    (caliop_aerosol_type, caliop_feature_type) = caliop_request._get_feature_classification(filename=caliop_file_path,
                                                                                            variable='Atmospheric_Volume_Description')

    caliop_aerosol_type_mask = np.copy(caliop_aerosol_type)
    caliop_aerosol_type_mask[caliop_feature_type != 3] = -1.
    caliop_Depolarization_Ratio = np.asarray(caliop_request._get_calipso_data(filename=caliop_file_path,
                                                                              variable='Particulate_Depolarization_Ratio_Profile_532'))

    # Apply spatial mask
    spatial_mask = np.where((caliop_latitude > lat_down) & (caliop_latitude < lat_up) &
                            (caliop_longitude > lon_left) & (caliop_longitude < lon_right))[0]

    if len(spatial_mask) > 0:

        # logger.info('Data found within the spatial window: %s', caliop_file_path)
        print('Data found within the spatial window: ', caliop_file_path)

        return caliop_utc[spatial_mask], caliop_latitude[spatial_mask], \
               caliop_longitude[spatial_mask], caliop_altitude, caliop_beta[:, spatial_mask], caliop_alpha[:, spatial_mask], \
               caliop_aerosol_type[:, spatial_mask], caliop_feature_type[:, spatial_mask], caliop_Depolarization_Ratio[:, spatial_mask], caliop_AOD_532_total[spatial_mask]
    else:
        return None

caliop_data = read_caliop_data(caliop_file, lat_down, lat_up, lon_left, lon_right)
caliop_utc, caliop_latitude, caliop_longitude, caliop_altitude, caliop_beta, caliop_alpha, caliop_aerosol_type, caliop_feature_type, caliop_Depolarization_Ratio, caliop_AOD_532_total = caliop_data

spatial_mask = np.where((caliop_latitude > lat_down) & (caliop_latitude < lat_up) & (caliop_longitude > lon_left) & (caliop_longitude < lon_right))[0]

attenuation_mask = np.zeros((caliop_feature_type.shape))
aersol_mask = np.zeros((caliop_feature_type.shape))
attenuation_mask[caliop_feature_type == 7] = 1.
aersol_mask[caliop_feature_type == 3] = 1.
attenuation_mask_lat = np.sum(attenuation_mask, axis=0)

aod_file = './output_aod_file_v2.npz'
script_name = os.path.splitext(os.path.basename(os.path.abspath(__file__)))[0]
save_path = f'./figures/{script_name}_output/'
pathlib.Path(save_path).mkdir(parents=True, exist_ok=True)

lat_caliop = np.load(aod_file, allow_pickle=True)['lat_caliop']
modis_lat_all = np.load(aod_file, allow_pickle=True)['modis_lat_all']
aod_caliop = np.load(aod_file, allow_pickle=True)['aod_caliop']
modis_aod_all = np.load(aod_file, allow_pickle=True)['modis_aod_all']

caliop_aod_trap = np.zeros((caliop_alpha.shape[1]))
plume_thickness = np.zeros((caliop_alpha.shape[1]))

for i in range(caliop_alpha.shape[1]):
    alpha_i = caliop_alpha[:, i]
    mask_i = aersol_mask[:, i]
    alpha_i[alpha_i < 0] = np.nan
    alpha_i[np.isnan(alpha_i)] = 0

    alpha_i[(caliop_altitude > 7.)] = 0.
    mask_i[(caliop_altitude > 7.)] = 0.

    caliop_aod_trap[i] = np.trapz(alpha_i[::-1], caliop_altitude[::-1])
    plume_thickness[i] = np.trapz(mask_i[::-1], caliop_altitude[::-1])

fontsize = 12
fig, ax = plt.subplots(figsize=(11, 5))
# ax.plot(lat_caliop, aod_caliop, 'g.-',lw=3, markersize=5, label='CALIOP')
ax.plot(modis_lat_all, modis_aod_all, 'k.-',lw=3, markersize=10, label='MODIS Aqua')
# Create the masks
mask_greater = attenuation_mask_lat >= 1
mask_less_equal = attenuation_mask_lat < 1

# Then plot the line in a single color and style
# ax.plot(caliop_latitude, caliop_AOD_532_total, 'g-', lw=3, label='CALIOP')
# Overlay the different marker styles for the sections of the line that meet your conditions
# ax.plot(caliop_latitude[mask_greater], caliop_AOD_532_total[mask_greater], 'bo', markersize=5)  # Use 'go' for green circles
ax.plot(caliop_latitude[mask_less_equal], caliop_AOD_532_total[mask_less_equal], 'g-*', lw=3, markersize=10, label='CALIOP')  # Use 'g*' for green stars
ax.plot(caliop_latitude[mask_less_equal], caliop_aod_trap[mask_less_equal], 'r-*', lw=3, markersize=10, label='CALIOP trap')  # Use 'g*' for green stars

ax.set_xlabel('Latitude [$^{\circ}$]', fontsize=fontsize)
ax.set_ylabel('AOD', fontsize=fontsize)
ax.set_xlim(12., 20.)
ax.set_ylim(0, 5.)
ax.grid()
# ax.set_title(f'layer between {layer[0]:.1f} km - {layer[1]:.1f} km', fontsize=fontsize, loc='left')
ax.tick_params(axis='both', labelsize=fontsize)
ax.legend(loc='best', fontsize=fontsize)
plt.savefig(save_path + f'figure_aod.png', dpi=300)


fig, ax = plt.subplots(figsize=(11, 5))
# ax.plot(lat_caliop, aod_caliop, 'g.-',lw=3, markersize=5, label='CALIOP')
ax.plot(modis_lat_all, modis_aod_all, 'k.-',lw=3, markersize=10, label='MODIS Aqua')
# Create the masks
mask_greater = attenuation_mask_lat >= 1
mask_less_equal = attenuation_mask_lat < 1

# Then plot the line in a single color and style
# ax.plot(caliop_latitude, caliop_AOD_532_total, 'g-', lw=3, label='CALIOP')
# Overlay the different marker styles for the sections of the line that meet your conditions
# ax.plot(caliop_latitude[mask_greater], caliop_AOD_532_total[mask_greater], 'bo', markersize=5)  # Use 'go' for green circles
ax.plot(caliop_latitude[mask_less_equal], caliop_AOD_532_total[mask_less_equal], 'g-*', lw=3, markersize=10, label='CALIOP')  # Use 'g*' for green stars
ax.plot(caliop_latitude[mask_less_equal], caliop_AOD_532_total[mask_less_equal] * 63.5 / 43.5, 'r-*', lw=3, markersize=10, label='CALIOP corrected')
ax.set_xlabel('Latitude [$^{\circ}$]', fontsize=fontsize)
ax.set_ylabel('AOD', fontsize=fontsize)
ax.set_xlim(12., 20.)
ax.set_ylim(0, 5.)

ax.grid()
# ax.set_title(f'layer between {layer[0]:.1f} km - {layer[1]:.1f} km', fontsize=fontsize, loc='left')
ax.tick_params(axis='both', labelsize=fontsize)
ax.legend(loc='best', fontsize=fontsize)
plt.savefig(save_path + f'figure_aod_corrected.png', dpi=300)

plume_top = np.zeros((caliop_latitude.shape[0]))
plume_bottom = np.zeros((caliop_latitude.shape[0]))
plum_diff = np.zeros((caliop_latitude.shape[0]))

for i in range(caliop_latitude.shape[0]):
    aerosol_layer_height = caliop_altitude * aersol_mask[:, i]
    aerosol_layer_height[aerosol_layer_height < 0.1] = np.nan

    plume_top[i] = np.nanmax(aerosol_layer_height)
    plume_bottom[i] = np.nanmin(aerosol_layer_height)
    plum_diff[i] = plume_top[i] - plume_bottom[i]


fig, ax = plt.subplots(figsize=(11, 5))

ax.plot(caliop_latitude[mask_less_equal], plume_top[mask_less_equal], 'r-*', lw=3, markersize=10, label='dust top')
ax.plot(caliop_latitude[mask_less_equal], plume_bottom[mask_less_equal], 'b-*', lw=3, markersize=10, label='dust bottom')
# ax.plot(caliop_latitude, top_plume_height_bottom, 'k-.', lw=3, markersize=10, label='dust bottom nonfilter')
ax.plot(caliop_latitude[mask_less_equal], plume_thickness[mask_less_equal], 'g-*', lw=3, markersize=10, label='dust thickness')
ax.plot(caliop_latitude[mask_less_equal], plum_diff[mask_less_equal], 'k-*', lw=3, markersize=10, label='dust thickness nonfilter')

ax.set_xlabel('Latitude [$^{\circ}$]', fontsize=fontsize)
ax.set_ylabel('Altitude [km]', fontsize=fontsize)
ax.set_xlim(12., 20.)
ax.set_ylim(0, 7.)
# ax.grid()
ax.tick_params(axis='both', labelsize=fontsize)
ax.legend(loc='best', fontsize=fontsize)
plt.savefig(save_path + f'dust_plume_height.png', dpi=300)