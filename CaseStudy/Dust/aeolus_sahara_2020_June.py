#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    aeolus_sahara_2020_June.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        20/02/2023 23:54

import sys
sys.path.append('../../')

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
    # Apply spatial mask
    spatial_mask = np.where((latitude > lat_down) & (latitude < lat_up) &
                            (longitude > lon_left) & (longitude < lon_right))[0]

    latitude = latitude[spatial_mask]
    longitude = longitude[spatial_mask]
    sca_middle_bin_altitude_obs = sca_middle_bin_altitude_obs[spatial_mask, :]
    sca_middle_bin_backscatter = sca_middle_bin_backscatter[spatial_mask, :]

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

        datatime_all = []
        latitude_all = []
        longitude_all = []
        caliop_altitude = []
        beta_all = []
        aerosol_type_all = []

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

                    print(aeolus_file_path)
                    (latitude_i, longitude_i, sca_mb_altitude, sca_mb_backscatter) = read_aeolus_data(aeolus_file_path,
                                                                                                      lat_down, lat_up,
                                                                                                      lon_left,
                                                                                                      lon_right)
                    print(sca_mb_backscatter)
                    quit()
            start_date_datetime += time_delta
