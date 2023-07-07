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

print(caliop_latitude.shape)
print(caliop_alpha.shape)
print(caliop_feature_type.shape)

attenuation_mask = np.zeros((caliop_feature_type.shape))
attenuation_mask[caliop_feature_type == 7] = 1.
attenuation_mask_lat = np.sum(attenuation_mask, axis=1)
print(caliop_latitude[caliop_latitude > 1])
quit()




aod_file = './output_aod_file.npz'
script_name = os.path.splitext(os.path.basename(os.path.abspath(__file__)))[0]
save_path = f'./figures/{script_name}_output/'
pathlib.Path(save_path).mkdir(parents=True, exist_ok=True)

lat_caliop = np.load(aod_file, allow_pickle=True)['lat_caliop']
modis_lat_all = np.load(aod_file, allow_pickle=True)['modis_lat_all']
aod_caliop = np.load(aod_file, allow_pickle=True)['aod_caliop']
modis_aod_all = np.load(aod_file, allow_pickle=True)['modis_aod_all']

fontsize = 12
fig, ax = plt.subplots(figsize=(8, 6))
ax.plot(lat_caliop, aod_caliop, 'g.-',lw=3, markersize=5, label='CALIOP')
ax.plot(modis_lat_all, modis_aod_all, 'r.-',lw=3, markersize=5, label='MODIS')
ax.set_xlabel('Latitude', fontsize=fontsize)
ax.set_ylabel('AOD', fontsize=fontsize)
# ax.set_xlim(lat1_caliop, lat2_caliop)
ax.set_ylim(0, 5.)
# ax.set_title(f'layer between {layer[0]:.1f} km - {layer[1]:.1f} km', fontsize=fontsize, loc='left')
ax.tick_params(axis='both', labelsize=fontsize)
ax.legend(loc='best', fontsize=fontsize)
plt.savefig(save_path + f'figure_aod.png', dpi=300)