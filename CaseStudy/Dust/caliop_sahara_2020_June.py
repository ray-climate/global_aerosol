#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    caliop_sahara_2020_June.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        16/02/2023 18:26

import sys
sys.path.append('../../')

from Caliop.caliop import Caliop_hdf_reader
from datetime import datetime, timedelta
from matplotlib.gridspec import GridSpec
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy as np
import logging
import pathlib
import sys
import os

##############################################################
# Define start and end dates
start_date = '2020-06-20'
end_date = '2020-06-20'

# Define the spatial bounds
lat_up = 37.
lat_down = 1.
# lon_left = -72.
# lon_right = 31.

# Set up time delta
time_delta = timedelta(days = 1)
##############################################################
meridional_boundary = [-90., -75., -60., -45., -30., -15., 0., 15., 30.]
##############################################################

# Define output directory
script_name = os.path.splitext(os.path.abspath(__file__))[0]
output_dir = f'{script_name}_output'
pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True)

# Create output directories if they don't exist
##############################################################

# Add the .log extension to the base name

log_filename = f'{script_name}.log'
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                    filemode='w',
                    filename=os.path.join(output_dir, log_filename),
                    level=logging.INFO)
logger = logging.getLogger()

##############################################################
# Define data directory
CALIOP_JASMIN_dir = '/gws/nopw/j04/eo_shared_data_vol1/satellite/calipso/APro5km/'

##############################################################

def read_caliop_data(caliop_file_path, lat_down, lat_up, lon_left, lon_right):

    caliop_request = Caliop_hdf_reader()

    # Read data from Caliop file
    caliop_utc = np.asarray(caliop_request._get_profile_UTC(caliop_file_path))
    caliop_latitude = np.asarray(caliop_request._get_latitude(caliop_file_path))
    caliop_longitude = np.asarray(caliop_request._get_longitude(caliop_file_path))
    caliop_altitude = np.asarray(caliop_request.get_altitudes(caliop_file_path))
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
               caliop_longitude[spatial_mask], caliop_altitude, caliop_beta[:, spatial_mask], \
               caliop_aerosol_type[:, spatial_mask], caliop_Depolarization_Ratio[:, spatial_mask]
    else:
        return None

# Parse start and end dates
start_date_datetime = datetime.strptime(start_date, '%Y-%m-%d')
end_date_datetime = datetime.strptime(end_date, '%Y-%m-%d')

fig = plt.figure(constrained_layout=True, figsize=(25, 10))
gs = GridSpec(1, 8, figure=fig)

for k in range(len(meridional_boundary) - 1):

    lon_left = meridional_boundary[k]
    lon_right = meridional_boundary[k + 1]

    datatime_all = []
    latitude_all = []
    longitude_all = []
    caliop_altitude = []
    beta_all = []
    aerosol_type_all = []

    while start_date_datetime <= end_date_datetime:

        year_i = '{:04d}'.format(start_date_datetime.year)
        month_i = '{:02d}'.format(start_date_datetime.month)
        day_i = '{:02d}'.format(start_date_datetime.day)

        caliop_fetch_dir = os.path.join(CALIOP_JASMIN_dir, year_i, f'{year_i}_{month_i}_{day_i}')

    #     for caliop_file_name in os.listdir(caliop_fetch_dir):
    #         if caliop_file_name.endswith('hdf'):
    #             caliop_file_path = os.path.join(caliop_fetch_dir, caliop_file_name)
    #
    #             caliop_data = read_caliop_data(caliop_file_path, lat_down, lat_up, lon_left, lon_right)
    #
    #             if caliop_data:
    #                 caliop_utc, caliop_latitude, caliop_longitude, caliop_altitude, caliop_beta, \
    #                 caliop_aerosol_type, caliop_Depolarization_Ratio = caliop_data
    #                 datatime_all.extend(caliop_utc)
    #                 latitude_all.extend(caliop_latitude)
    #                 longitude_all.extend(caliop_longitude)
    #                 try:
    #                     beta_all = np.concatenate([beta_all, caliop_beta], axis=1)
    #                     aerosol_type_all = np.concatenate([aerosol_type_all, caliop_aerosol_type], axis=1)
    #                 except:
    #                     beta_all = np.copy(caliop_beta)
    #                     aerosol_type_all = np.copy(caliop_aerosol_type)
    #
        start_date_datetime += time_delta
    #
    # beta_all = np.asarray(beta_all)
    # aerosol_type_all = np.asarray(aerosol_type_all)
    # sort_index = np.argsort(datatime_all)
    #
    # datatime_all_sort = sorted(datatime_all)
    # beta_all_sort = beta_all[:, sort_index]
    # beta_all_sort[beta_all_sort<0] = 0
    # aerosol_type_all_sort = aerosol_type_all[:, sort_index]

    a = np.linspace(1,100,100)
    b = np.linspace(1,100,100)
    axk = fig.add_subplot(gs[0, k])
    # figk = plt.plot(np.mean(beta_all_sort, axis=1), caliop_altitude, 'r-*', lw=2)
    figk = plt.plot(a, b, 'r-*', lw=2)

    if meridional_boundary[k] < 0:
        if meridional_boundary[k+1] < 0:
            axk.set_xlabel('[%s$^{\circ}$ W - %s$^{\circ}$ W]' % (abs(meridional_boundary[k]), abs(meridional_boundary[k+1])), fontsize=15)
        else:
            axk.set_xlabel('[%s$^{\circ}$ W - %s$^{\circ}$ E]' % (abs(meridional_boundary[k]), abs(meridional_boundary[k+1])), fontsize=15)
    else:
        if meridional_boundary[k+1] < 0:
            axk.set_xlabel('[%s$^{\circ}$ E - %s$^{\circ}$ W]' % (abs(meridional_boundary[k]), abs(meridional_boundary[k+1])), fontsize=15)
        else:
            axk.set_xlabel('[%s$^{\circ}$ E - %s$^{\circ}$ E]' % (abs(meridional_boundary[k]), abs(meridional_boundary[k+1])), fontsize=15)

    # axk.set_ylabel('Averaged photon counts', fontsize=15)
    for tick in axk.xaxis.get_major_ticks():
        tick.label.set_fontsize(15)
    for tick in axk.yaxis.get_major_ticks():
        tick.label.set_fontsize(15)
    axk.set_xscale('log')
    axk.set_xlim([1.e-4, 1.e-2])
    axk.set_ylim([0., 15])
    axk.grid()

fig.suptitle("%s-%s-%s" %(year_i, month_i, day_i), fontsize = 17)
fig.text(0.5, 0.02, 'Backscatter coefficient [km$^{-1}$sr$^{-1}$]', ha='center', va='center', fontsize=17)
fig.text(0.02, 0.5, 'Heights [km]', ha='center', va='center', rotation='vertical', fontsize=17)
fig.subplots_adjust(left=0.05, right=0.95, bottom=0.1, top=0.95, wspace=0.3, hspace=0.2)

plt.savefig('./test_1d-8.png')

# aerosol_type_all_sort_mask = np.zeros((aerosol_type_all_sort.shape))
# aerosol_type_all_sort_mask[(aerosol_type_all_sort == 2) | (aerosol_type_all_sort == 5) |(aerosol_type_all_sort == 6) ] = 1
# aerosol_type_all_sort_mask = np.sum(aerosol_type_all_sort_mask, axis = 0)
# aerosol_type_all_sort_mask_index = np.where(aerosol_type_all_sort_mask > 0)[0]
# datatime_all_sort = np.asarray(datatime_all_sort)
# datatime_filtered = datatime_all_sort[aerosol_type_all_sort_mask_index]
# beta_filtered = beta_all_sort[:, aerosol_type_all_sort_mask_index]
# aerosol_type_filtered = aerosol_type_all_sort[:, aerosol_type_all_sort_mask_index]


##### 2D mesh plot ##########################################################
# x_space = np.linspace(1, len(datatime_all_sort), len(datatime_all_sort))
# X, Y = np.meshgrid(x_space, caliop_altitude)
# fig, ax = plt.subplots(figsize=(12, 10))
# plt.pcolormesh(X, Y, beta_all_sort, norm=colors.LogNorm(vmin = 0.0001, vmax = 0.03), cmap='rainbow')
# plt.xlabel('Datetime', fontsize=20)
# plt.ylabel('Height [km]', fontsize=20)
# plt.ylim([0., 16])
# ax.yaxis.set_ticks(range(0, 16, 2))
#
# # Generate tick indices
# # tick_indices = np.linspace(0, len(datatime_all_sort) - 1, 8, dtype=int)
# # Set x-tick labels
# # plt.xticks(np.asarray(datatime_all_sort)[tick_indices], rotation=45, fontsize=20)
#
# cbar = plt.colorbar(extend='both', shrink=0.7, fraction=0.05)
# cbar.set_label('[km$^{0-1}$sr$^{-1}$]', fontsize=20)
# cbar.ax.tick_params(labelsize=20)
# for tick in ax.xaxis.get_major_ticks():
#     tick.label.set_fontsize(20)
# for tick in ax.yaxis.get_major_ticks():
#     tick.label.set_fontsize(20)
# plt.savefig('./test_timeseries.png')
##### 2D mesh plot ##########################################################

##### 1D backscatter plot ###################################################
# fig, ax = plt.subplots(figsize=(8, 15))
# plt.plot(np.mean(beta_all_sort, axis=1), caliop_altitude, 'r-*', lw=2)
# plt.xlabel('Backscatter coefficient', fontsize=15)
# plt.ylabel('Averaged photon counts', fontsize=15)
# for tick in ax.xaxis.get_major_ticks():
#     tick.label.set_fontsize(15)
# for tick in ax.yaxis.get_major_ticks():
#     tick.label.set_fontsize(15)
# ax.set_xscale('log')
# plt.xlim([1.e-4, 1.e-2])
# plt.ylim([0., 15])
# plt.grid()
# plt.savefig('./test_1d.png')
# plt.close()
##### 1D backscatter plot ###################################################
