#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    colocation_data_fetch.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        18/10/2022 12:13


"""
# v1 set up on 18th October 2022 is to fetch Aeolus data, as Aeolus data is in a coarser resolution than CALIOP.
"""

import sys
import os
sys.path.append('../')

from Caliop.caliop import Caliop_hdf_reader
from datetime import datetime, timedelta
from netCDF4 import Dataset
from Aeolus.aeolus import *
import pandas as pd
import numpy as np
import logging

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# set default logging level as INFO level
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                    filemode='w',
                    filename= './output.log',
                    level=logging.INFO)

output_dir = './subdatasets'
temporal_threshold = 8. # temporal space between co-located AEOLUS and CALIOP data.
caliop_dir = '/gws/pw/j07/nceo_aerosolfire/rsong/project/global_aerosol/Colocation/CALIOP_data/' \
             'asdc.larc.nasa.gov/data/CALIPSO/LID_L2_05kmAPro-Standard-V4-20'

colocation_filename = []
lat_ALADIN_colocation = []
lon_ALADIN_colocation = []
lat_CALIOP_colocation = []
lon_CALIOP_colocation = []
time_ALADIN_colocation = []
time_CALIOP_colocation = []

def get_beta_plot(aladin_alt, aladin_beta, caliop_alt, caliop_beta, save_dir, lat, lon):

    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(5, 8))

    plt.plot(aladin_beta, aladin_alt / 1.e3, 'r-', lw=2, label = 'ALADIN')
    # plt.hist(aladin_beta, bins=aladin_alt/1.e3, orientation="horizontal")
    plt.plot(caliop_beta * 1.e3, caliop_alt , 'k-', lw=2, label='CALIOP')

    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(12)
    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(12)

    plt.legend(fontsize=14)
    plt.xlabel('Part. backsc. coeff. [Mm$^{-1}$sr$^{-1}$]', fontsize=15)
    plt.ylabel('Height [km]', fontsize=15)

    plt.title('(%.2f$^{\circ}$ %.2f$^{\circ}$)'%(lat, lon), fontsize=14)

    plt.xlim([0., 35.])
    plt.ylim([0., 12.])
    plt.tight_layout()
    plt.savefig(save_dir)


for file in os.listdir('./colocated_AEOLUS_CALIPSO/'):

    if (file.endswith('.nc')) & ('2020_06' in file):

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

        try:
            colocation_year = colocation_filename[i][0:4]
            colocation_month = colocation_filename[i][5:7]
            colocation_day = colocation_filename[i][8:10]

            print('%s-%s-%s, %s %s'%(colocation_year, colocation_month, colocation_day, lat_ALADIN_colocation[i], lon_ALADIN_colocation[i]))
            if (int(colocation_year) == 2020) & (int(colocation_month) == 6) & \
                    (int(colocation_day) >= 20) & (int(colocation_day) <= 25) & \
                    (lat_ALADIN_colocation[i] > 1.) & (lat_ALADIN_colocation[i] < 38.) & \
                    (lon_ALADIN_colocation[i] > -24.) & (lon_ALADIN_colocation[i] < 27.):

                logging.info('--------------------------------------------------------------------------------')
                logging.info('----------> Start fetching co-location data ......')
                logging.info('----------> AEOLUS data location: (%.2f, %.2f)' % (lat_ALADIN_colocation[i], lon_ALADIN_colocation[i]))

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

                # print('target aeolus time: %s'%datetime_UTC_ALADIN_i)
                # print('search aeolus time:', SCA_time_obs_datetime)
                # print('search aeolus lat', latitude_of_DEM_intersection_obs)

                time_list_aladin = [abs((pd.to_datetime(k) - datetime_UTC_ALADIN_i).total_seconds()) for k in SCA_time_obs_datetime.values]
                # print('search aeolus alt', SCA_middle_bin_altitude[np.argmin(time_list_aladin), :])
                # print('search aeolus beta', SCA_middle_bin_backscatter[np.argmin(time_list_aladin), :])
                SCA_middle_bin_backscatter_obs = SCA_middle_bin_backscatter[np.argmin(time_list_aladin), :]
                SCA_middle_bin_backscatter_obs[SCA_middle_bin_backscatter_obs == -1.e6] = np.nan
                # print('min index:', np.argmin(time_list_aladin), SCA_time_obs_datetime[np.argmin(time_list_aladin)])
                SCA_middle_bin_altitude_obs = SCA_middle_bin_altitude[np.argmin(time_list_aladin), :]
                print(SCA_middle_bin_backscatter_obs)
                print(SCA_middle_bin_altitude_obs)
                # quit()
                logging.info('----------> CALIOP data location: (%.2f, %.2f)' % (lat_CALIOP_colocation[i], lon_CALIOP_colocation[i]))

                CALIOP_hour = str(int(time_CALIOP_colocation[i]))
                CALIOP_minute = str(int((time_CALIOP_colocation[i] - int(time_CALIOP_colocation[i])) * 60.))
                CALIOP_second = str(int(time_CALIOP_colocation[i] * 3600. - int(time_CALIOP_colocation[i]) * 3600. -
                                        int((time_CALIOP_colocation[i] - int(time_CALIOP_colocation[i])) * 60.) * 60))

                if len(CALIOP_hour) == 1:
                    CALIOP_hour = '0' + CALIOP_hour
                if len(CALIOP_minute) == 1:
                    CALIOP_minute = '0' + CALIOP_minute
                if len(CALIOP_second) == 1:
                    CALIOP_second = '0' + CALIOP_second

                logging.info('----------> CALIOP data date: %s-%s-%s %s:%s'
                             % (colocation_year, colocation_month, colocation_day, CALIOP_hour, CALIOP_minute))

                caliop_time_obs_datetime = []
                caliop_file_list = []

                datetime_UTC_caliop = datetime.strptime(colocation_filename[i][:-3] + ' 00:00:00',
                                                          '%Y_%m_%d %H:%M:%S') + timedelta(hours=time_CALIOP_colocation[i])

                for file in os.listdir('%s/%s/%s/'%(caliop_dir, colocation_year, colocation_month)):

                    caliop_filename_day = file[-17:-15]
                    caliop_filename_hour = file[-14:-12]
                    caliop_filename_minute = file[-11:-9]
                    caliop_filename_second = file[-8:-6]
                    caliop_time_obs_datetime.append(datetime.strptime('%s_%s_%s %s:%s:%s'%
                                                                      (colocation_year, colocation_month,
                                                                       caliop_filename_day, caliop_filename_hour,
                                                                       caliop_filename_minute, caliop_filename_second),
                                                                      '%Y_%m_%d %H:%M:%S'))
                    caliop_file_list.append(file)


                def nearest(items, pivot):
                    return min([p for p in items if p <= pivot], key=lambda x: abs(x - pivot))

                caliop_time_obs_datetime_min = nearest(caliop_time_obs_datetime, datetime_UTC_caliop)

                for j in range(len(caliop_time_obs_datetime)):
                    if caliop_time_obs_datetime[j] == caliop_time_obs_datetime_min:
                        target_caliop_filename = caliop_file_list[j]

                        caliop_request = Caliop_hdf_reader()

                        caliop_l2_latitude = caliop_request._get_latitude(
                            filename='%s/%s/%s/%s' % (caliop_dir, colocation_year, colocation_month, target_caliop_filename))
                        caliop_l2_longitude = caliop_request._get_longitude(
                            filename='%s/%s/%s/%s' % (caliop_dir, colocation_year, colocation_month, target_caliop_filename))
                        caliop_l2_altitude = caliop_request.get_altitudes(
                            filename='%s/%s/%s/%s' % (caliop_dir, colocation_year, colocation_month, target_caliop_filename))
                        caliop_datime_utc = caliop_request._get_profile_UTC(
                            filename='%s/%s/%s/%s' % ( caliop_dir, colocation_year, colocation_month, target_caliop_filename))
                        caliop_beta_532nm = caliop_request._get_calipso_data(
                            filename='%s/%s/%s/%s' % ( caliop_dir, colocation_year, colocation_month, target_caliop_filename),
                            variable='Total_Backscatter_Coefficient_532')

                        time_list_caliop = [abs((k - datetime_UTC_caliop).total_seconds()) for k in caliop_datime_utc]


                netcdf_file = output_dir + '/%s%s%s%s%s%s.nc' % (
                colocation_year, colocation_month, colocation_day, ALADIN_hour, ALADIN_minute, ALADIN_second)
                ncfile = Dataset(netcdf_file, mode='w', format='NETCDF4')

                # aladin write
                aladin_backscatter_dim = ncfile.createDimension('aladin_backscatter', SCA_middle_bin_backscatter.shape[1])
                aladin_altitude_dim = ncfile.createDimension('aladin_altitude', SCA_middle_bin_altitude.shape[1])

                nc_ALADIN_latitude = ncfile.createVariable('ALADIN_latitude', 'f4')
                nc_ALADIN_latitude[:] = latitude_of_DEM_intersection_obs[np.argmin(time_list_aladin)]

                nc_ALADIN_longitude = ncfile.createVariable('ALADIN_longitude', 'f4')
                nc_ALADIN_longitude[:] = longitude_of_DEM_intersection_obs[np.argmin(time_list_aladin)]

                nc_ALADIN_backscatter = ncfile.createVariable('ALADIN_backscatter_midBin', 'f4', ('aladin_backscatter',))
                nc_ALADIN_backscatter[:] = SCA_middle_bin_backscatter_obs

                nc_ALADIN_altitude = ncfile.createVariable('ALADIN_altitude', 'f4', ('aladin_altitude',))
                nc_ALADIN_altitude[:] = SCA_middle_bin_altitude_obs

                # caliop write
                caliop_backscatter_dim = ncfile.createDimension('caliop_backscatter', caliop_beta_532nm.shape[0])
                caliop_altitude_dim = ncfile.createDimension('caliop_altitude', caliop_beta_532nm.shape[0])

                nc_CALIOP_latitude = ncfile.createVariable('CALIOP_latitude', 'f4')
                nc_CALIOP_latitude[:] = caliop_l2_latitude[np.argmin(time_list_caliop)]

                nc_CALIOP_longitude = ncfile.createVariable('CALIOP_longitude', 'f4')
                nc_CALIOP_longitude[:] = caliop_l2_longitude[np.argmin(time_list_caliop)]

                nc_CALIOP_backscatter_532nm = ncfile.createVariable('CALIOP_backscatter_532nm', 'f4', ('caliop_backscatter',))
                nc_CALIOP_backscatter_532nm[:] = caliop_beta_532nm[:, np.argmin(time_list_caliop)]

                nc_CALIOP_altitude = ncfile.createVariable('CALIOP_altitude', 'f4', ('caliop_altitude',))
                nc_CALIOP_altitude[:] = caliop_l2_altitude

                print(SCA_middle_bin_altitude_obs)
                print(SCA_middle_bin_backscatter_obs)

                get_beta_plot(SCA_middle_bin_altitude_obs[1:], SCA_middle_bin_backscatter_obs,
                              caliop_l2_altitude, caliop_beta_532nm[:, np.argmin(time_list_caliop)],
                              './figures/%s%s%s%s%s%s.png'%(colocation_year, colocation_month,
                                                            colocation_day, ALADIN_hour, ALADIN_minute, ALADIN_second),
                              latitude_of_DEM_intersection_obs[np.argmin(time_list_aladin)],
                              longitude_of_DEM_intersection_obs[np.argmin(time_list_aladin)])
        except:
            continue
            # print('new updated implementation version-2')
            #
            # logging.info(
            #     '----------> CALIOP data location: (%.2f, %.2f)' % (lat_CALIOP_colocation[i], lon_CALIOP_colocation[i]))
            #
            # logging.info('----------> CALIOP data location: (%.2f, %.2f)' % (lat_CALIOP_colocation[i], lon_CALIOP_colocation[i]))
            # logging.info('--------------------------------------------------------------------------------\n\n\n')
