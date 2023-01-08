#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    generate_ncFile_colocation.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        07/01/2023 15:56

import os
import sys
sys.path.append('../')

from Caliop.caliop import Caliop_hdf_reader
from mpl_toolkits.basemap import Basemap
from datetime import datetime, timedelta
from matplotlib.gridspec import GridSpec
from netCDF4 import Dataset, date2num
import matplotlib.pyplot as plt
from netCDF4 import num2date
from osgeo import gdal
import netCDF4 as nc
import numpy as np
import logging
import pyproj
import glob
import csv

def extract_colocation_data(aeolus_colocation_file, caliop_colocation_file,
                            colocation_datetime, lat_modis, lon_modis, aod_modis,
                            savefig_filename, save_netcdf):

    # Open the netCDF file containing AEOLUS data
    dataset_nc = nc.Dataset(aeolus_colocation_file)

    # Extract relevant variables from the AEOLUS data
    L1B_start_time_obs = dataset_nc['observations']['L1B_start_time_obs'][:]
    L1B_start_time_obs = list(map(int, L1B_start_time_obs))

    latitude_of_DEM_intersection_obs = dataset_nc['observations']['latitude_of_DEM_intersection_obs'][:]
    longitude_of_DEM_intersection_obs = dataset_nc['observations']['longitude_of_DEM_intersection_obs'][:]

    sca_observation_time = dataset_nc['sca']['sca_time_obs'][:]
    sca_observation_time = [int(i) for i in sca_observation_time]

    sca_middle_bin_backscatter = dataset_nc['sca']['sca_middle_bin_backscatter'][:]
    sca_middle_bin_extinction = dataset_nc['sca']['sca_middle_bin_extinction'][:]

    # Convert time variables to datetime objects
    sca_observation_time_dt = num2date(sca_observation_time, units="s since 2000-01-01", only_use_cftime_datetimes=False)
    L1B_start_time_obs_datetime = num2date(L1B_start_time_obs, units="s since 2000-01-01",
                                           only_use_cftime_datetimes=False)

    # Initialize lists to store selected AEOLUS data
    sca_observation_time_list = []
    sca_lat_obs_list = []
    sca_lon_obs_list = []
    sca_middle_bin_backscatter_list = []
    sca_middle_bin_extinction_list = []

    # Iterate through the AEOLUS data, selecting only data points that have a corresponding L1B_start_time_obs value
    
    for i in range(len(sca_observation_time_dt)):

        if sca_observation_time_dt[i] in L1B_start_time_obs_datetime:
            
            sca_observation_time_list.append(sca_observation_time_dt[i])
            sca_lat_obs_list.append(
                latitude_of_DEM_intersection_obs[L1B_start_time_obs_datetime == sca_observation_time_dt[i]][0])
            sca_lon_obs_list.append(
                longitude_of_DEM_intersection_obs[L1B_start_time_obs_datetime == sca_observation_time_dt[i]][0])
            sca_middle_bin_backscatter_list.append(sca_middle_bin_backscatter[i, :].filled())
            sca_middle_bin_extinction_list.append(sca_middle_bin_extinction[i, :].filled())

    sca_observation_time_array = np.asarray(sca_observation_time_list)
    sca_lat_obs_array = np.asarray(sca_lat_obs_list)
    sca_lon_obs_array = np.asarray(sca_lon_obs_list)
    sca_middle_bin_backscatter_array = np.asarray(sca_middle_bin_backscatter_list)
    sca_middle_bin_extinction_array = np.asarray(sca_middle_bin_extinction_list)

    sca_lon_obs_array[sca_lon_obs_array > 180.] = sca_lon_obs_array[sca_lon_obs_array > 180.] - 360.
    index = np.where(sca_observation_time_array == colocation_datetime)[0][0]

    print('colocation at %s from %.2f, %.2f' % (colocation_datetime, sca_lat_obs_array[index], sca_lon_obs_array[index]))

    aeolus_index_start = index - 50
    aeolus_index_end = index + 50

    if aeolus_index_start < 0:
        aeolus_index_start = 0
    if aeolus_index_end > len(sca_lat_obs_array):
        aeolus_index_end = len(sca_lat_obs_array)

    aeolus_lat_list = sca_lat_obs_array[aeolus_index_start: aeolus_index_end][:]
    aeolus_lon_list = sca_lon_obs_array[aeolus_index_start: aeolus_index_end][:]
    aeolus_beta_list = sca_middle_bin_backscatter_array[aeolus_index_start: aeolus_index_end][:]

    caliop_request = Caliop_hdf_reader()
    caliop_latitude_list = caliop_request.\
        _get_latitude(caliop_colocation_file)
    caliop_longitude_list = caliop_request.\
        _get_longitude(caliop_colocation_file)
    caliop_beta_list = caliop_request.\
        _get_calipso_data(filename=caliop_colocation_file,
                          variable='Total_Backscatter_Coefficient_532')
    print(aeolus_beta_list.shape)
    print(caliop_beta_list.shape)

    # fig = plt.figure(figsize=(12, 12))

    ax1 = fig.add_subplot(gs[0, :])
    # ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    # setup mercator map projection.
    m = Basemap(llcrnrlon=int(sca_lon_obs_array[index] - 20.),
                llcrnrlat=int(sca_lat_obs_array[index] - 20.),
                urcrnrlon=int(sca_lon_obs_array[index] + 20.),
                urcrnrlat=int(sca_lat_obs_array[index] + 20.),
                rsphere=(6378137.00, 6356752.3142),
                resolution='l', projection='merc',
                lat_0=aeolus_lat_list[50], lon_0=aeolus_lon_list[50], suppress_ticks='False')

    m.drawcoastlines()
    m.fillcontinents()

    x, y = m(aeolus_lon_list, aeolus_lat_list)
    x2, y2 = m(caliop_longitude_list, caliop_latitude_list)
    x_0, y_0 = m(sca_lon_obs_array[index], sca_lat_obs_array[index])

    aod_modis_masked = np.zeros((aod_modis.shape))
    aod_modis_masked[:] = np.nan
    aod_modis_masked[aod_modis > 0] = aod_modis[aod_modis > 0]
    aod_modis_masked = aod_modis_masked * 0.001

    m.pcolormesh(lon_modis, lat_modis, aod_modis_masked, latlon=True, alpha=0.8, vmin=0, vmax=0.6)

    cbar = m.colorbar(shrink=0.7, extend='both')
    cbar.set_label('MCD19A2 550 nm AOD', fontsize=24)
    cbar.ax.tick_params(labelsize=16)

    m.scatter(x, y, marker='o', color='g', s=18, label='AEOLUS')
    m.scatter(x2, y2, marker='_', color='k', s=5, label='CALIOP')
    m.scatter(x_0, y_0, marker="*", c="r", s=100, label='Colocation')

    # draw parallels
    m.drawparallels(np.arange(-90, 90, 10), labels=[1, 0, 0, 1], fontsize=24)
    # draw meridians
    m.drawmeridians(np.arange(-180, 180, 10), labels=[1, 1, 0, 1], fontsize=24)
    ax1.legend(fontsize=20)
    # ax1.title(colocation_datetime, fontsize = 30)
    # plt.savefig(savefig_filename)
    # plt.close()

    # save co-located aeolus and caliop into one netcdf

    ncfile = Dataset(save_netcdf, mode='w', format='NETCDF4')
    ncfile.createDimension('x_aeolus', aeolus_beta_list.shape[0])
    ncfile.createDimension('y_aeolus', aeolus_beta_list.shape[1])

    nc_lat_aeolus = ncfile.createVariable('aeolus_latitude', 'f4', ('x_aeolus'))
    nc_lat_aeolus[:] = aeolus_lat_list

    nc_lon_aeolus = ncfile.createVariable('aeolus_longitude', 'f4', ('x_aeolus'))
    nc_lon_aeolus[:] = aeolus_lon_list

    nc_beta_aeolus = ncfile.createVariable('aeolus_beta', 'f4', ('y_aeolus', 'x_aeolus'))
    nc_beta_aeolus[:] = aeolus_beta_list.T

    ncfile.createDimension('x_caliop', caliop_beta_list.shape[1])
    ncfile.createDimension('y_caliop', caliop_beta_list.shape[0])

    nc_beta_caliop = ncfile.createVariable('caliop_beta', 'f4', ('y_caliop', 'x_caliop'))
    nc_beta_caliop[:] = caliop_beta_list


