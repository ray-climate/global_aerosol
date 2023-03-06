#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    aeolus_sahara_2020_June_nightime.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        06/03/2023 15:35

import sys
sys.path.append('../../')

from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
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


# Define the spatial bounds
lat_up = 40.
lat_down = 0.
# lon_left = -72.
# lon_right = 31.
lat_jump_threshold = 3.0

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
SEVIRI_dir = '/gws/pw/j07/nceo_aerosolfire/rsong/project/global_aerosol/SEVIRI_CLM/'

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

def plot_aeolus_basemap(lat_aeolus, lon_aeolus, lat_SEVIRI, lon_SEVIRI, CLM_SEVIRI, save_fig):


    bbox = [-60., 0., 30., 40.]  # map boundaries
    fig, ax = plt.subplots(figsize=(9, 4), dpi=200)
    # ax.set_axis_off()
    # set basemap boundaries, cylindrical projection, 'i' = intermediate resolution
    m = Basemap(llcrnrlon=bbox[0], llcrnrlat=bbox[1], urcrnrlon=bbox[2],
                urcrnrlat=bbox[3], resolution='i', projection='cyl')

    x_aeolus, y_aeolus = m(lon_aeolus, lat_aeolus)

    # m.fillcontinents(color='#d9b38c',lake_color='#bdd5d5') # continent colors
    # m.drawmapboundary(fill_color='#bdd5d5') # ocean color
    m.drawcoastlines()
    m.drawcountries()
    states = m.drawstates()  # draw state boundaries

    # m.pcolormesh(lon, lat, np.ma.masked_array(CLM_valid, mask), cmap='gray', latlon=True)

    # draw parallels and meridians by every 5 degrees
    parallels = np.arange(bbox[1], bbox[3], 10.)
    m.drawparallels(parallels, labels=[1, 0, 0, 0], fontsize=10)
    meridians = np.arange(bbox[0], bbox[2], 10.)
    m.drawmeridians(meridians, labels=[0, 0, 0, 1], fontsize=10)

    m.pcolormesh(lon_SEVIRI, lat_SEVIRI, CLM_SEVIRI, cmap='gray', alpha = 0.7, latlon=True)

    m.scatter(x_aeolus, y_aeolus, marker='o', color='blue', s=10, label='AEOLUS')
    plt.legend(fontsize=10)
    plt.savefig(save_fig, dpi=200)

def get_SEVIRI_CLM(file_path):
    """Read the SEVIRI CLM data from the downloaded file"""
    dataset = gdal.Open(file_path, gdal.GA_ReadOnly)
    # Read the first band of the dataset
    band = dataset.GetRasterBand(1)
    # Read the data from the band as a NumPy array
    data = band.ReadAsArray()
    return data

# implement SEVIRI data for CLM testing
lon_SEVIRI = np.load('/gws/pw/j07/nceo_aerosolfire/rsong/project/global_aerosol/SEVIRI/SEVIRI_lon.npy')
lat_SEVIRI = np.load('/gws/pw/j07/nceo_aerosolfire/rsong/project/global_aerosol/SEVIRI/SEVIRI_lat.npy')
CLM_SEVIRI = np.load('/gws/pw/j07/nceo_aerosolfire/rsong/project/global_aerosol/SEVIRI/SEVIRI_CLM.npy')

lon_SEVIRI[(np.isinf(lon_SEVIRI)) | (np.isinf(lat_SEVIRI)) | (np.isinf(CLM_SEVIRI))] = 0
lat_SEVIRI[(np.isinf(lon_SEVIRI)) | (np.isinf(lat_SEVIRI)) | (np.isinf(CLM_SEVIRI))] = 0
# CLM_SEVIRI[(np.isinf(lon_SEVIRI)) | (np.isinf(lat_SEVIRI)) | (np.isinf(CLM_SEVIRI))] = 0

# Extract relevant variables from the AEOLUS data
##############################################################
# Define start and end dates
for day in range(14, 27):

    start_date = '2020-06-%d' % day
    end_date = '2020-06-%d' % day

    lon_left = meridional_boundary[0]
    lon_right = meridional_boundary[1]

    aeolus_time_all = []
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

                time_i = footprint_time_aeolus[spatial_mask]
                latitude_i = latitude[spatial_mask]
                longitude_i = longitude[spatial_mask]
                sca_mb_altitude = sca_mb_altitude[spatial_mask, :]
                sca_mb_backscatter = sca_mb_backscatter[spatial_mask, :]
                sca_mb_ber = ber_aeolus_mb[spatial_mask, :]

                latitude_all.extend(latitude_i)
                longitude_all.extend(longitude_i)
                aeolus_time_all.extend(time_i)

                # plot_aeolus_basemap(latitude_i, longitude_i, lat_SEVIRI, lon_SEVIRI, CLM_valid, './test_fig.png')

                try:
                    beta_all = np.concatenate([beta_all, sca_mb_backscatter], axis=0)
                    ber_all = np.concatenate([ber_all, sca_mb_ber], axis=0)
                    altitude_all = np.concatenate([altitude_all, sca_mb_altitude], axis=0)
                except:
                    beta_all = np.copy(sca_mb_backscatter)
                    ber_all = np.copy(sca_mb_ber)
                    altitude_all = np.copy(sca_mb_altitude)
        start_date_datetime += time_delta

    # Convert altitude values from meters to kilometers
    altitude_all[altitude_all == -1] = np.nan
    altitude_all = altitude_all * 1e-3

    # convert aeolus data with the given scaling factor: convert to km-1.sr-1
    beta_all[beta_all == -1.e6] = 0
    beta_all = beta_all * 1.e-6 * 1.e3

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

    lat_jump_threshold = 2.0
    lat_sublists = [[0]]  # initialize with the index of the first value

    j = 1
    while j < len(latitude_all):
        if abs(latitude_all[j] - latitude_all[lat_sublists[-1][-1]]) >= lat_jump_threshold:
            lat_sublists.append([j])
        else:
            lat_sublists[-1].append(j)
        j += 1

    lat_ascending = []
    lon_ascending = []
    time_ascending = []
    for m in range(len(lat_sublists)):
        if latitude_all[lat_sublists[m][1]]- latitude_all[lat_sublists[m][0]] > 0:
            lat_ascending.extend(latitude_all[lat_sublists[m][0]:lat_sublists[m][-1]])
            lon_ascending.extend(longitude_all[lat_sublists[m][0]:lat_sublists[m][-1]])
            time_ascending.extend(aeolus_time_all[lat_sublists[m][0]:lat_sublists[m][-1]])

    central_time = time_ascending[int(len(time_ascending)/2)]
    SEVIRI_time_str = get_SEVIRI_CLM(central_time)

    for root, dirs, files in os.walk(SEVIRI_dir):
        for file in files:
            if SEVIRI_time_str in file:
                SEVIRI_CLM_file = os.path.join(root, file)
                SEVIRI_CLM_data = get_SEVIRI_CLM(SEVIRI_CLM_file)
            else:
                logger.warning('No SEVIRI CLM file found for the given time: %s' % central_time)
                CLM_valid = np.zeros((SEVIRI_CLM_data.shape))
                CLM_valid[:] = np.nan
                CLM_valid[SEVIRI_CLM_data == 2] = 1
                mask = np.isnan(CLM_valid)
                CLM_valid = np.ma.masked_array(SEVIRI_CLM_data, mask)

    plot_aeolus_basemap(lat_ascending, lon_ascending, lat_SEVIRI, lon_SEVIRI, CLM_valid, './test_fig.png')
    quit()
    #
    # beta_volume_sum = np.sum(backscatter_resample, axis=1)
    #
    # axk = fig.add_subplot(gs[0, k])
    #
    # figk = plt.plot(np.mean(backscatter_resample[beta_volume_sum > 0, :], axis=0), alt_caliop, 'r-*', lw=2,
    #                 label='no filter')
    # plt.plot(np.mean(backscatter_resample[(beta_volume_sum > 0) & (ber_volume_sum < 1), :], axis=0),
    #          alt_caliop, 'b-*', lw=2, label='cloud removed')
    #
    # if meridional_boundary[k] < 0:
    #     if meridional_boundary[k+1] < 0:
    #         axk.set_xlabel('[%s$^{\circ}$ W - %s$^{\circ}$ W]' % (abs(meridional_boundary[k]), abs(meridional_boundary[k+1])), fontsize=15)
    #     else:
    #         axk.set_xlabel('[%s$^{\circ}$ W - %s$^{\circ}$ E]' % (abs(meridional_boundary[k]), abs(meridional_boundary[k+1])), fontsize=15)
    # else:
    #     if meridional_boundary[k+1] < 0:
    #         axk.set_xlabel('[%s$^{\circ}$ E - %s$^{\circ}$ W]' % (abs(meridional_boundary[k]), abs(meridional_boundary[k+1])), fontsize=15)
    #     else:
    #         axk.set_xlabel('[%s$^{\circ}$ E - %s$^{\circ}$ E]' % (abs(meridional_boundary[k]), abs(meridional_boundary[k+1])), fontsize=15)
    #
    # # axk.set_ylabel('Averaged photon counts', fontsize=15)
    # for tick in axk.xaxis.get_major_ticks():
    #     tick.label.set_fontsize(15)
    # for tick in axk.yaxis.get_major_ticks():
    #     tick.label.set_fontsize(15)
    # # axk.legend(loc='upper right', fontsize=15)
    # axk.set_xscale('log')
    # axk.set_xlim([1.e-4, 2.e-2])
    # axk.set_ylim([0., 8])
    # axk.grid()
    #
