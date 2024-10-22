#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    aeolus_caliop_sahara2020_birdview.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        15/03/2023 13:45

import sys
sys.path.append('../../')

import matplotlib.pyplot as plt
from Caliop.caliop import Caliop_hdf_reader
from getColocationData.get_aeolus import *
from datetime import datetime, timedelta
from matplotlib.gridspec import GridSpec
import matplotlib.colors as colors
from SEVIRI.get_SEVIRI_CLM import *
from netCDF4 import Dataset
from osgeo import gdal
import numpy as np
import logging
import pathlib
import sys
import os

input_sat = str(sys.argv[1]) # input satellite, either 'aeolus' or 'caliop'
input_mode = str(sys.argv[2]) # input mode, either 'ascending' or 'descending'

# Define the spatial bounds
lat_up = 40. # degree
lat_down = 0. # degree
# lon_left = -72.
# lon_right = 31.
lat_jump_threshold = 3.0 # degree, lat_jump_threshold is the threshold to separate observations from different orbits

# Define the time range
datetime_start = "2020-06-17"
datetime_end = "2020-06-24"

# Convert strings to datetime objects
start_date = datetime.strptime(datetime_start, "%Y-%m-%d")
end_date = datetime.strptime(datetime_end, "%Y-%m-%d")

# Set up time delta
time_delta = timedelta(days = 1)
##############################################################
meridional_boundary = [-60., 30.]
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
CLMSEVIRI_dir = '/gws/pw/j07/nceo_aerosolfire/rsong/project/global_aerosol/SEVIRI_data_collection/SEVIRI_CLM/'
HRSEVIRI_dir = '/gws/pw/j07/nceo_aerosolfire/rsong/project/global_aerosol/SEVIRI_data_collection/SEVIRI_HRSEVIRI/'
CMASEVIRI_dir = '/gws/pw/j07/nceo_aerosolfire/rsong/project/global_aerosol/SEVIRI_data_collection/CMA-SEVIRI/'
IanSEVIRI_ref = '/gws/pw/j07/nceo_aerosolfire/rsong/project/global_aerosol/SEVIRI_data_collection/SEVIRI_Ian/BTD_ref/final_average.npy'

CALIOP_JASMIN_dir = '/gws/nopw/j04/eo_shared_data_vol1/satellite/calipso/APro5km/'

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

for i in range((end_date - start_date).days + 1):

    date_i = start_date + timedelta(days=i)
    # Convert date back to string format
    date_i_str = date_i.strftime("%Y-%m-%d")

    lon_left = meridional_boundary[0]
    lon_right = meridional_boundary[1]

    aeolus_time_all = []
    aeolus_latitude_all = []
    aeolus_longitude_all = []
    aeolus_altitude_all = []
    aeolus_beta_all = []
    aeolus_ber_all = []

    caliop_time_all = []
    caliop_latitude_all = []
    caliop_longitude_all = []
    caliop_altitude = []
    caliop_beta_all = []
    caliop_aerosol_type_all = []

    # Parse start and end dates
    start_date_datetime = datetime.strptime(date_i_str, '%Y-%m-%d')
    end_date_datetime = datetime.strptime(date_i_str, '%Y-%m-%d')

    # collect all Aeolus data from 1 day
    while start_date_datetime <= end_date_datetime:

        year_i = '{:04d}'.format(start_date_datetime.year)
        month_i = '{:02d}'.format(start_date_datetime.month)
        day_i = '{:02d}'.format(start_date_datetime.day)

        aeolus_fetch_dir = os.path.join(AEOLUS_JASMIN_dir, f'{year_i}-{month_i}')
        caliop_fetch_dir = os.path.join(CALIOP_JASMIN_dir, year_i, f'{year_i}_{month_i}_{day_i}')

        if input_sat == 'Aeolus':
            # aeolus data fetch
            for aeolus_file_name in os.listdir(aeolus_fetch_dir):
                if aeolus_file_name.endswith('%s-%s-%s.nc'%(year_i,  month_i, day_i)):

                    aeolus_file_path = os.path.join(aeolus_fetch_dir, aeolus_file_name)

                    (latitude, longitude, sca_mb_altitude,
                     footprint_time_aeolus, sca_mb_backscatter, alpha_aeolus_mb,
                     qc_aeolus_mb, ber_aeolus_mb, lod_aeolus_mb) = \
                        extract_variables_from_aeolus(aeolus_file_path, logger)

                    spatial_mask = np.where((latitude > lat_down) & (latitude < lat_up) &
                                            (longitude > lon_left) & (longitude < lon_right))[0]

                    time_i = footprint_time_aeolus[spatial_mask]
                    latitude_i = latitude[spatial_mask]
                    longitude_i = longitude[spatial_mask]
                    sca_mb_altitude = sca_mb_altitude[spatial_mask, :]
                    sca_mb_backscatter = sca_mb_backscatter[spatial_mask, :]
                    sca_mb_ber = ber_aeolus_mb[spatial_mask, :]

                    aeolus_latitude_all.extend(latitude_i)
                    aeolus_longitude_all.extend(longitude_i)
                    aeolus_time_all.extend(time_i)

                    # plot_aeolus_basemap(latitude_i, longitude_i, lat_SEVIRI, lon_SEVIRI, CLM_valid, './test_fig.png')

                    try:
                        aeolus_beta_all = np.concatenate([aeolus_beta_all, sca_mb_backscatter], axis=0)
                        aeolus_ber_all = np.concatenate([aeolus_ber_all, sca_mb_ber], axis=0)
                        aeolus_altitude_all = np.concatenate([aeolus_altitude_all, sca_mb_altitude], axis=0)
                    except:
                        aeolus_beta_all = np.copy(sca_mb_backscatter)
                        aeolus_ber_all = np.copy(sca_mb_ber)
                        aeolus_altitude_all = np.copy(sca_mb_altitude)

        if input_sat == 'Caliop':

            # caliop data fetch
            for caliop_file_name in os.listdir(caliop_fetch_dir):
                if caliop_file_name.endswith('hdf'):
                    caliop_file_path = os.path.join(caliop_fetch_dir, caliop_file_name)
                    caliop_data = read_caliop_data(caliop_file_path, lat_down, lat_up, lon_left, lon_right)

                    if caliop_data:
                        caliop_utc, caliop_latitude, caliop_longitude, caliop_altitude, caliop_beta, \
                        caliop_aerosol_type, caliop_Depolarization_Ratio = caliop_data

                        spatial_mask = np.where((caliop_latitude > lat_down) & (caliop_latitude < lat_up) &
                                                (caliop_longitude > lon_left) & (caliop_longitude < lon_right))[0]

                        caliop_time_all.extend(caliop_utc[spatial_mask])
                        caliop_latitude_all.extend(caliop_latitude[spatial_mask])
                        caliop_longitude_all.extend(caliop_longitude[spatial_mask])

                        try:
                            caliop_beta_all = np.concatenate([caliop_beta_all, caliop_beta[:, spatial_mask]], axis=1)
                            caliop_aerosol_type_all = np.concatenate([caliop_aerosol_type_all, caliop_aerosol_type[:, spatial_mask]], axis=1)
                        except:
                            caliop_beta_all = np.copy(caliop_beta[:, spatial_mask])
                            caliop_aerosol_type_all = np.copy(caliop_aerosol_type[:, spatial_mask])

        start_date_datetime += time_delta

    if input_sat == 'Aeolus':
        ############# aeolus tidy up ####################################################
        # Convert aeolus altitude values from meters to kilometers
        aeolus_altitude_all[aeolus_altitude_all == -1] = np.nan
        aeolus_altitude_all = aeolus_altitude_all * 1e-3

        # convert aeolus data with the given scaling factor: convert to km-1.sr-1
        aeolus_beta_all[aeolus_beta_all == -1.e6] = 0
        aeolus_beta_all = aeolus_beta_all * 1.e-6 * 1.e3

        # Create empty array for resampled data, with same shape as alt_aeolus
        backscatter_resample = np.zeros((aeolus_altitude_all.shape[0], np.size(alt_caliop)))
        # backscatter_resample[:] = np.nan

        # Iterate through rows and columns of alt_aeolus and data_aeolus
        for m in range(aeolus_altitude_all.shape[0]):
            alt_aeolus_m = aeolus_altitude_all[m, :]
            for n in range(np.size(alt_aeolus_m)):
                if alt_aeolus_m[n] > 0:
                    if (n + 1) < len(alt_aeolus_m):
                        # Resample data based on nearest altitude value less than current value in alt_caliop
                        backscatter_resample[m, (alt_caliop < alt_aeolus_m[n]) & (alt_caliop > alt_aeolus_m[n + 1])] = \
                        aeolus_beta_all[m, n]

        ############# aeolus tidy up ####################################################

        ############# separate aeolus data into different orbits ############################
        lat_jump_threshold = 2.0
        lat_sublists = [[0]]  # initialize with the index of the first value

        j = 1
        while j < len(aeolus_latitude_all):
            if abs(aeolus_latitude_all[j] - aeolus_latitude_all[lat_sublists[-1][-1]]) >= lat_jump_threshold:
                lat_sublists.append([j])
            else:
                lat_sublists[-1].append(j)
            j += 1

        aeolus_lat_asc_des = []
        aeolus_lon_asc_des = []
        aeolus_time_asc_des = []

        if input_mode == 'ascending':
            for m in range(len(lat_sublists)):
                if aeolus_latitude_all[lat_sublists[m][1]] - aeolus_latitude_all[lat_sublists[m][0]] > 0:
                    aeolus_lat_asc_des.append(aeolus_latitude_all[lat_sublists[m][0]:lat_sublists[m][-1]])
                    aeolus_lon_asc_des.append(aeolus_longitude_all[lat_sublists[m][0]:lat_sublists[m][-1]])
                    aeolus_time_asc_des.append(aeolus_time_all[lat_sublists[m][0]:lat_sublists[m][-1]])
        else:
            for m in range(len(lat_sublists)):
                if aeolus_latitude_all[lat_sublists[m][1]] - aeolus_latitude_all[lat_sublists[m][0]] < 0:
                    aeolus_lat_asc_des.append(aeolus_latitude_all[lat_sublists[m][0]:lat_sublists[m][-1]])
                    aeolus_lon_asc_des.append(aeolus_longitude_all[lat_sublists[m][0]:lat_sublists[m][-1]])
                    aeolus_time_asc_des.append(aeolus_time_all[lat_sublists[m][0]:lat_sublists[m][-1]])

        central_time = aeolus_time_asc_des[int(len(aeolus_time_asc_des) / 2)][
            int(len(aeolus_time_asc_des[0]) / 2)]
        CLMSEVIRI_time_str = get_SEVIRI_CLM_time(central_time)
        HRSEVIRI_time_str = get_HRSEVIRI_time(central_time)
        ############# separate aeolus data into different orbits ############################

    if input_sat == 'Caliop':
        ############# caliop tidy up ####################################################

        sort_index = np.argsort(caliop_time_all)

        caliop_time_all = sorted(caliop_time_all)
        caliop_beta_all = np.asarray(caliop_beta_all)[:,sort_index]
        caliop_latitude_all = np.asarray(caliop_latitude_all)[sort_index]
        caliop_longitude_all = np.asarray(caliop_longitude_all)[sort_index]

        ############# caliop tidy up ####################################################

        ############# separate caliop data into different orbits ############################
        lat_sublists = [[0]]  # initialize with the index of the first value

        j = 1
        while j < len(caliop_latitude_all):
            if (abs(caliop_latitude_all[j] - caliop_latitude_all[lat_sublists[-1][-1]]) >= lat_jump_threshold):
                lat_sublists.append([j])
            elif (caliop_time_all[j] - caliop_time_all[lat_sublists[-1][-1]]) > timedelta(minutes=10):
                lat_sublists.append([j])
            else:
                lat_sublists[-1].append(j)
            j += 1

        caliop_lat_asc_des = []
        caliop_lon_asc_des = []
        caliop_time_asc_des = []

        if input_mode == 'ascending':
            for m in range(len(lat_sublists)):
                try:
                    if caliop_latitude_all[lat_sublists[m][10]] - caliop_latitude_all[lat_sublists[m][0]] > 0:
                        caliop_lat_asc_des.append(caliop_latitude_all[lat_sublists[m][0]:lat_sublists[m][-1]])
                        caliop_lon_asc_des.append(caliop_longitude_all[lat_sublists[m][0]:lat_sublists[m][-1]])
                        caliop_time_asc_des.append(caliop_time_all[lat_sublists[m][0]:lat_sublists[m][-1]])
                except:
                    print('Only one data point in this orbit, ignore it')
        else:
            for m in range(len(lat_sublists)):
                try:
                    if caliop_latitude_all[lat_sublists[m][10]] - caliop_latitude_all[lat_sublists[m][0]] < 0:
                        caliop_lat_asc_des.append(caliop_latitude_all[lat_sublists[m][0]:lat_sublists[m][-1]])
                        caliop_lon_asc_des.append(caliop_longitude_all[lat_sublists[m][0]:lat_sublists[m][-1]])
                        caliop_time_asc_des.append(caliop_time_all[lat_sublists[m][0]:lat_sublists[m][-1]])
                except:
                    print('Only one data point in this orbit, ignore it')

        central_time = caliop_time_asc_des[int(len(caliop_time_asc_des) / 2)][int(len(caliop_time_asc_des[int(len(caliop_time_asc_des) / 2)]) / 2)]
        CLMSEVIRI_time_str = get_SEVIRI_CLM_time(central_time)
        HRSEVIRI_time_str = get_HRSEVIRI_time(central_time)

        ############# separate caliop data into different orbits ############################

    for root, dirs, files in os.walk(HRSEVIRI_dir):
        for file in files:
            if HRSEVIRI_time_str in file:
                HRSEVIRI_file = os.path.join(root, file)

                year_SEVIRI_background = HRSEVIRI_time_str[:4]
                month_SEVIRI_background = HRSEVIRI_time_str[4:6]
                day_SEVIRI_background = HRSEVIRI_time_str[6:8]
                converted_SEVIRI_background_datetime = f"{year_SEVIRI_background}-{month_SEVIRI_background}-{day_SEVIRI_background}"

                # get_SEVIRI_HR_cartopy(HRSEVIRI_file,
                #                       extent=[meridional_boundary[0], lat_down, meridional_boundary[1], lat_up],
                #                       title = 'SEVIRI Dust RGB %s'%converted_SEVIRI_background_datetime,
                #                       aeolus_lat=aeolus_lat_ascending,
                #                       aeolus_lon=aeolus_lon_ascending,
                #                       aeolus_time=aeolus_time_ascending,
                #                       save_str=output_dir + '/SEVIRI_dust_RGB_%s.png' % converted_SEVIRI_background_datetime)

                if input_sat == 'Aeolus':
                    get_SEVIRI_Ian_cartopy(SEVIRI_HR_file_path = HRSEVIRI_file,
                                       BTD_ref = IanSEVIRI_ref,
                                       extent=[meridional_boundary[0], lat_down, meridional_boundary[1], lat_up],
                                       title='SEVIRI Dust Mask %s' % converted_SEVIRI_background_datetime,
                                       aeolus_lat=aeolus_lat_asc_des,
                                       aeolus_lon=aeolus_lon_asc_des,
                                       aeolus_time=aeolus_time_asc_des,
                                       save_str=output_dir + '/SEVIRI_dust_%s_%s_%s.png' % (input_sat, input_mode, converted_SEVIRI_background_datetime))

                    get_SEVIRI_HR_cartopy(HRSEVIRI_file,
                                          extent=[meridional_boundary[0], lat_down, meridional_boundary[1], lat_up],
                                          title = 'SEVIRI Dust RGB %s'%converted_SEVIRI_background_datetime,
                                          aeolus_lat=aeolus_lat_asc_des,
                                          aeolus_lon=aeolus_lon_asc_des,
                                          aeolus_time=aeolus_time_asc_des,
                                          save_str=output_dir + '/SEVIRI_dust_RGB_%s_%s_%s.png' % (input_sat, input_mode, converted_SEVIRI_background_datetime))
                else:
                    get_SEVIRI_Ian_cartopy(SEVIRI_HR_file_path = HRSEVIRI_file,
                                           BTD_ref = IanSEVIRI_ref,
                                           extent=[meridional_boundary[0], lat_down, meridional_boundary[1], lat_up],
                                           title='SEVIRI Dust Mask %s' % converted_SEVIRI_background_datetime,
                                           caliop_lat=caliop_lat_asc_des,
                                           caliop_lon=caliop_lon_asc_des,
                                           caliop_time=caliop_time_asc_des,
                                           save_str=output_dir + '/SEVIRI_dust_%s_%s_%s.png' % (input_sat, input_mode, converted_SEVIRI_background_datetime))

                    get_SEVIRI_HR_cartopy(HRSEVIRI_file,
                                          extent=[meridional_boundary[0], lat_down, meridional_boundary[1], lat_up],
                                          title = 'SEVIRI Dust RGB %s'%converted_SEVIRI_background_datetime,
                                          caliop_lat=caliop_lat_asc_des,
                                          caliop_lon=caliop_lon_asc_des,
                                          caliop_time=caliop_time_asc_des,
                                          save_str=output_dir + '/SEVIRI_dust_RGB_%s_%s_%s.png' % (input_sat, input_mode, converted_SEVIRI_background_datetime))

            else:
                logger.warning('No HRSEVIRI file found for the given time: %s' % central_time)

