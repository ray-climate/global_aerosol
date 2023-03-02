#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    aeolus_sahara_2020_June.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        20/02/2023 23:54

import sys
sys.path.append('../../')

from getColocationData.get_aeolus import *
from datetime import datetime, timedelta
from matplotlib.gridspec import GridSpec
import matplotlib.colors as colors
import matplotlib.pyplot as plt
from netCDF4 import Dataset
import numpy as np
import logging
import pathlib
import sys
import os


# Define the spatial bounds
lat_up = 37.
lat_down = 1.
# lon_left = -72.
# lon_right = 31.

BER_threshold = 0.05

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
AEOLUS_JASMIN_dir = '/gws/pw/j07/nceo_aerosolfire/rsong/project/global_aerosol/aeolus_archive/'

# take caliop altitude for projection
alt_caliop = np.load('./caliop_altitude.npy')

##############################################################
def read_aeolus_data(aeolus_ncFile, lat_down, lat_up, lon_left, lon_right):

    # open the netcdf file
    with Dataset(aeolus_ncFile, 'r') as nc_data:

        latitude = nc_data['observations']['latitude_of_DEM_intersection_obs'][:]
        longitude_of_DEM_intersection_obs = nc_data['observations']['longitude_of_DEM_intersection_obs'][:]
        longitude = [lon_i - 360. if lon_i > 180 else lon_i for lon_i in longitude_of_DEM_intersection_obs]

        sca_middle_bin_altitude_obs = nc_data['sca']['SCA_middle_bin_altitude_obs'][:]
        sca_middle_bin_backscatter = nc_data['sca']['SCA_middle_bin_backscatter'][:]
        sca_middle_bin_extinction = nc_data['sca']['SCA_middle_bin_extinction'][:]
        sca_middle_bin_qc = nc_data['sca']['SCA_middle_bin_processing_qc_flag'][:]
        sca_middle_bin_ber = nc_data['sca']['SCA_middle_bin_BER'][:]

    latitude = np.asarray(latitude)
    longitude = np.asarray(longitude)
    sca_middle_bin_backscatter = np.asarray(sca_middle_bin_backscatter)
    sca_middle_bin_ber = np.asarray(sca_middle_bin_ber)

    # Apply spatial mask
    spatial_mask = np.where((latitude > lat_down) & (latitude < lat_up) &
                            (longitude > lon_left) & (longitude < lon_right))[0]

    latitude = latitude[spatial_mask]
    longitude = longitude[spatial_mask]
    sca_middle_bin_altitude_obs = sca_middle_bin_altitude_obs[spatial_mask, :]
    sca_middle_bin_backscatter = sca_middle_bin_backscatter[spatial_mask, :]
    sca_middle_bin_ber = sca_middle_bin_ber[spatial_mask, :]

    if len(spatial_mask) > 0:
        # logger.info('Data found within the spatial window: %s', caliop_file_path)
        print('Data found within the spatial window: ', aeolus_ncFile)
        return latitude, longitude, sca_middle_bin_altitude_obs, sca_middle_bin_backscatter
    else:
        return None


# Extract relevant variables from the AEOLUS data
##############################################################
# Define start and end dates
for day in range(14, 27):

    start_date = '2020-06-%d' % day
    end_date = '2020-06-%d' % day

    fig = plt.figure(constrained_layout=True, figsize=(25, 10))
    gs = GridSpec(1, 8, figure=fig)

    for k in range(len(meridional_boundary) - 1):

        lon_left = meridional_boundary[k]
        lon_right = meridional_boundary[k + 1]

        latitude_all = []
        longitude_all = []
        altitude_all = []
        beta_all = []
        ber_all = []

        # Parse start and end dates
        start_date_datetime = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_datetime = datetime.strptime(end_date, '%Y-%m-%d')

        while start_date_datetime <= end_date_datetime:

            year_i = '{:04d}'.format(start_date_datetime.year)
            month_i = '{:02d}'.format(start_date_datetime.month)
            day_i = '{:02d}'.format(start_date_datetime.day)

            aeolus_fetch_dir = os.path.join(AEOLUS_JASMIN_dir, f'{year_i}-{month_i}')

            for aeolus_file_name in os.listdir(aeolus_fetch_dir):
                if aeolus_file_name.endswith('%s-%s-%s.nc'%(year_i,  month_i, day_i)):

                    aeolus_file_path = os.path.join(aeolus_fetch_dir, aeolus_file_name)

                    (latitude, longitude, sca_mb_altitude,
                     footprint_time_aeolus, sca_mb_backscatter, alpha_aeolus_mb,
                     qc_aeolus_mb, ber_aeolus_mb, lod_aeolus_mb) = \
                        extract_variables_from_aeolus(aeolus_file_path, logger)

                    spatial_mask = np.where((latitude > lat_down) & (latitude < lat_up) &
                                            (longitude > lon_left) & (longitude < lon_right))[0]

                    latitude_i = latitude[spatial_mask]
                    longitude_i = longitude[spatial_mask]
                    sca_mb_altitude = sca_mb_altitude[spatial_mask, :]
                    sca_mb_backscatter = sca_mb_backscatter[spatial_mask, :]
                    sca_mb_ber = ber_aeolus_mb[spatial_mask, :]

                    latitude_all.extend(latitude_i)
                    longitude_all.extend(longitude_i)

                    try:
                        beta_all = np.concatenate([beta_all, sca_mb_backscatter], axis=0)
                        ber_all = np.concatenate([ber_all, sca_mb_ber], axis=0)
                        altitude_all = np.concatenate([altitude_all, sca_mb_altitude], axis=0)
                    except:
                        beta_all = np.copy(sca_mb_backscatter)
                        ber_all = np.copy(sca_mb_ber)
                        altitude_all = np.copy(sca_mb_altitude)

            start_date_datetime += time_delta

        altitude_all[altitude_all == -1] = np.nan
        beta_all[beta_all == -1.e6] = 0
        # Convert altitude values from meters to kilometers
        altitude_all = altitude_all * 1e-3

        # convert aeolus data with the given scaling factor: convert to km-1.sr-1
        beta_all = beta_all * 1.e-6 * 1.e3
        print(ber_all)
        # Create empty array for resampled data, with same shape as alt_aeolus
        backscatter_resample = np.zeros((altitude_all.shape[0], np.size(alt_caliop)))
        # backscatter_resample[:] = np.nan

        # Iterate through rows and columns of alt_aeolus and data_aeolus
        for m in range(altitude_all.shape[0]):
            alt_aeolus_m = altitude_all[m, :]
            for n in range(np.size(alt_aeolus_m)):
                if alt_aeolus_m[n] > 0:
                    if (n + 1) < len(alt_aeolus_m):
                        # Resample data based on nearest altitude value less than current value in alt_caliop
                        backscatter_resample[m, (alt_caliop < alt_aeolus_m[n]) & (alt_caliop > alt_aeolus_m[n + 1])] = \
                        beta_all[m, n]

        ber_all_mask = np.zeros((ber_all.shape))
        ber_all_mask[ber_all < BER_threshold] = 1.
        ber_volume_sum = np.sum(ber_all_mask, axis=1)
        print(ber_volume_sum)
        beta_volume_sum = np.sum(backscatter_resample, axis=1)

        axk = fig.add_subplot(gs[0, k])

        figk = plt.plot(np.mean(backscatter_resample[beta_volume_sum > 0, :], axis=0), alt_caliop, 'r-*', lw=2,
                        label='no filter')
        plt.plot(np.mean(backscatter_resample[(beta_volume_sum > 0) & (ber_volume_sum < 1), :], axis=0),
                 alt_caliop, 'b-*', lw=2, label='cloud removed')

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
        # axk.legend(loc='upper right', fontsize=15)
        axk.set_xscale('log')
        axk.set_xlim([1.e-4, 2.e-2])
        axk.set_ylim([0., 8])
        axk.grid()

    fig.suptitle("%s-%s-%s" % (year_i, month_i, day_i), fontsize=17)
    fig.text(0.5, 0.02, 'Backscatter coefficient [km$^{-1}$sr$^{-1}$]', ha='center', va='center', fontsize=17)
    fig.text(0.02, 0.5, 'Heights [km]', ha='center', va='center', rotation='vertical', fontsize=17)
    fig.subplots_adjust(left=0.05, right=0.95, bottom=0.1, top=0.95, wspace=0.3, hspace=0.2)

    plt.savefig(output_dir + '/aeolus_dust_backscatter_%s-%s-%s.png' % (year_i, month_i, day_i))
