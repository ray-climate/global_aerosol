#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    colocation_data_fetch.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        18/10/2022 12:13


"""
# v1 set up on 18th October 2022 is to fetch Aeolus data, as Aeolus data is in a coarser resolution than CALIOP.
"""

from datetime import datetime, timedelta
from netCDF4 import Dataset
from Aeolus.aeolus import *
import pandas as pd
import numpy as np
import logging
import os

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# set default logging level as INFO level
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                    filemode='w',
                    filename= './output.log',
                    level=logging.INFO)

output_dir = './subdatasets'
temporal_threshold = 3. # temporal space between co-located AEOLUS and CALIOP data.

colocation_filename = []
lat_ALADIN_colocation = []
lon_ALADIN_colocation = []
lat_CALIOP_colocation = []
lon_CALIOP_colocation = []
time_ALADIN_colocation = []
time_CALIOP_colocation = []

for file in os.listdir('./colocated_AEOLUS_CALIPSO/'):

    if file.endswith('.nc'):

        database_file = './colocated_AEOLUS_CALIPSO/%s'%file
        database = Dataset(database_file, 'r')

        lat_ALADIN = database.variables['lat_ALADIN'][:]
        lon_ALADIN = database.variables['lon_ALADIN'][:]
        time_ALADIN = database.variables['time_ALADIN'][:]

        lat_CALIOP = database.variables['lat_CALIOP'][:]
        lon_CALIOP = database.variables['lon_CALIOP'][:]
        time_CALIOP = database.variables['time_CALIOP'][:]

        dup_filename = [file for x in range(len(lat_ALADIN))]
        dup_filename = np.asarray(dup_filename)

        time_diff = np.abs(time_ALADIN - time_CALIOP)

        lat_ALADIN_colocation = np.hstack((lat_ALADIN_colocation, lat_ALADIN[time_diff < temporal_threshold]))
        lon_ALADIN_colocation = np.hstack((lon_ALADIN_colocation, lon_ALADIN[time_diff < temporal_threshold]))

        lat_CALIOP_colocation = np.hstack((lat_CALIOP_colocation, lat_CALIOP[time_diff < temporal_threshold]))
        lon_CALIOP_colocation = np.hstack((lon_CALIOP_colocation, lon_CALIOP[time_diff < temporal_threshold]))

        time_ALADIN_colocation = np.hstack((time_ALADIN_colocation, time_ALADIN[time_diff < temporal_threshold]))
        time_CALIOP_colocation = np.hstack((time_CALIOP_colocation, time_CALIOP[time_diff < temporal_threshold]))

        colocation_filename = np.hstack((colocation_filename, dup_filename[time_diff < temporal_threshold]))

for i in range(len(lat_ALADIN_colocation)):

        logging.info('--------------------------------------------------------------------------------')
        logging.info('----------> Start fetching co-location data ......')
        logging.info('----------> AEOLUS data location: (%.2f, %.2f)' % (lat_ALADIN_colocation[i], lon_ALADIN_colocation[i]))

        colocation_year = colocation_filename[i][0:4]
        colocation_month = colocation_filename[i][5:7]
        colocation_day = colocation_filename[i][8:10]

        ALADIN_hour = str(int(time_ALADIN_colocation[i]))
        ALADIN_minute = str(int((time_ALADIN_colocation[i] - int(time_ALADIN_colocation[i])) * 60.))
        ALADIN_second = str(int(time_ALADIN_colocation[i] * 3600. - int(time_ALADIN_colocation[i]) * 3600. -
                                int((time_ALADIN_colocation[i] - int(time_ALADIN_colocation[i])) * 60.) * 60))

        if len(ALADIN_hour) == 1:
            ALADIN_hour = '0' + ALADIN_hour
        if len(ALADIN_minute) == 1:
            ALADIN_minute = '0' + ALADIN_minute
        if len(ALADIN_second) == 1:
            ALADIN_second = '0' + ALADIN_second

        logging.info('----------> AEOLUS data date: %s-%s-%s %s:%s'
                     %(colocation_year, colocation_month, colocation_day, ALADIN_hour, ALADIN_minute))

        datetime_UTC_ALADIN_i = datetime.strptime(colocation_filename[i][:-3] + ' 00:00:00', '%Y_%m_%d %H:%M:%S') + timedelta(hours=time_ALADIN_colocation[i])
        datetime_UTC_ALADIN_i_minus = datetime_UTC_ALADIN_i - timedelta(minutes=2)
        datetime_UTC_ALADIN_i_plus = datetime_UTC_ALADIN_i + timedelta(minutes=1)

        DATA_PRODUCT = "ALD_U_N_2A"

        VirES_request = GetAeolusFromVirES(measurement_start=datetime_UTC_ALADIN_i_minus,
                                           measurement_stop=datetime_UTC_ALADIN_i_plus,
                                           DATA_PRODUCT=DATA_PRODUCT)

        ds_sca = VirES_request._get_ds_sca()
        SCA_time_obs_datetime = ds_sca['SCA_time_obs_datetime']
        latitude_of_DEM_intersection_obs = ds_sca['latitude_of_DEM_intersection_obs']
        longitude_of_DEM_intersection_obs = ds_sca['longitude_of_DEM_intersection_obs']
        SCA_middle_bin_backscatter = ds_sca['SCA_middle_bin_backscatter']
        SCA_middle_bin_altitude = ds_sca['SCA_middle_bin_altitude_obs']
        longitude_of_DEM_intersection_obs[longitude_of_DEM_intersection_obs > 180.] = longitude_of_DEM_intersection_obs[longitude_of_DEM_intersection_obs > 180.] - 360.

        time_list_aladin = [abs((pd.to_datetime(k) - datetime_UTC_ALADIN_i).total_seconds()) for k in SCA_time_obs_datetime.values]
        SCA_middle_bin_backscatter_obs = SCA_middle_bin_backscatter[np.argmin(time_list_aladin), :]
        SCA_middle_bin_backscatter_obs[SCA_middle_bin_backscatter_obs == -1.e6] = np.nan

        SCA_middle_bin_altitude_obs = SCA_middle_bin_altitude[np.argmin(time_list_aladin), :]

        netcdf_file = output_dir + '/%s%s%s%s%s%s.nc'%(colocation_year, colocation_month, colocation_day, ALADIN_hour, ALADIN_minute, ALADIN_second)
        ncfile = Dataset(netcdf_file, mode='w', format='NETCDF4')

        backscatter_dim = ncfile.createDimension('backscatter', SCA_middle_bin_backscatter.shape[1])
        altitude_dim = ncfile.createDimension('altitude', SCA_middle_bin_altitude.shape[1])

        nc_ALADIN_latitude = ncfile.createVariable('ALADIN_latitude', 'f4')
        nc_ALADIN_latitude[:] = latitude_of_DEM_intersection_obs[np.argmin(time_list_aladin)]

        nc_ALADIN_longitude = ncfile.createVariable('ALADIN_longitude', 'f4')
        nc_ALADIN_longitude[:] = longitude_of_DEM_intersection_obs[np.argmin(time_list_aladin)]

        nc_ALADIN_backscatter = ncfile.createVariable('ALADIN_backscatter_midBin', 'f4', ('backscatter',))
        nc_ALADIN_backscatter[:] = SCA_middle_bin_backscatter_obs

        nc_ALADIN_altitude = ncfile.createVariable('ALADIN_altitude', 'f4', ('altitude',))
        nc_ALADIN_altitude[:] = SCA_middle_bin_altitude_obs


        #
        # logging.info(
        #     '----------> CALIOP data location: (%.2f, %.2f)' % (lat_CALIOP_colocation[i], lon_CALIOP_colocation[i]))
        #
        # logging.info('----------> CALIOP data location: (%.2f, %.2f)' % (lat_CALIOP_colocation[i], lon_CALIOP_colocation[i]))
        # logging.info('--------------------------------------------------------------------------------\n\n\n')
