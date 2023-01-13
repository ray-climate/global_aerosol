#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    generate_colocation_hourly_task.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        13/01/2023 12:44

import sys
sys.path.append('../')

from Caliop.caliop import Caliop_hdf_reader
from datetime import datetime, timedelta
from netCDF4 import num2date
import geopy.distance
import netCDF4 as nc
import numpy as np
import pathlib
import logging
import csv
import os

def get_script_name():
    return sys.modules['__main__'].__file__

# Get the name of the script
script_name = get_script_name()

# Split the script name into a base name and an extension
script_base, script_ext = os.path.splitext(script_name)

# Add the .log extension to the base name
log_filename = script_base + '.log'

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                    filemode='w',
                    filename=log_filename,
                    level=logging.INFO)

CALIOP_JASMIN_dir = '/gws/nopw/j04/eo_shared_data_vol1/satellite/calipso/APro5km/'
Aeolus_JASMIN_dir = '/gws/pw/j07/nceo_aerosolfire/rsong/project/global_aerosol/aeolus_archive/'
database_dir = './colocation_database'
spatial_threshold = 200. # 200km threshold

try:
    os.stat(database_dir)
except:
    os.mkdir(database_dir)

search_date_start = '2019-07-02-0000'
search_date_end = '2019-07-02-0100'

search_date_start_datetime = datetime.strptime(search_date_start, '%Y-%m-%d-%H%M')
search_date_end_datetime = datetime.strptime(search_date_end, '%Y-%m-%d-%H%M')

search_year = '{:04d}'.format(search_date_start_datetime.year)
search_month = '{:02d}'.format(search_date_start_datetime.month)
search_day = '{:02d}'.format(search_date_start_datetime.day)

aeolus_dir = Aeolus_JASMIN_dir + '%s-%s/%s-%s-%s.nc'%(search_year, search_month, search_year, search_month, search_day)
dataset_nc = nc.Dataset(aeolus_dir)

L1B_start_time_obs = dataset_nc['observations']['L1B_start_time_obs'][:]
L1B_start_time_obs = [int(i) for i in L1B_start_time_obs]

latitude_of_DEM_intersection_obs = dataset_nc['observations']['latitude_of_DEM_intersection_obs'][:]
longitude_of_DEM_intersection_obs = dataset_nc['observations']['longitude_of_DEM_intersection_obs'][:]

sca_time_obs = dataset_nc['sca']['SCA_time_obs'][:]
sca_time_obs = [int(i) for i in sca_time_obs]

sca_time_obs_datetime = num2date(sca_time_obs, units="s since 2000-01-01", only_use_cftime_datetimes=False)
L1B_start_time_obs_datetime = num2date(L1B_start_time_obs, units="s since 2000-01-01", only_use_cftime_datetimes=False)

sca_time_obs_list = []
sca_lat_obs_list = []
sca_lon_obs_list = []

for i in range(len(sca_time_obs_datetime)):
    if (sca_time_obs_datetime[i] in L1B_start_time_obs_datetime) & \
            (sca_time_obs_datetime[i] > search_date_start_datetime) & \
            (sca_time_obs_datetime[i] < search_date_end_datetime):
        sca_time_obs_list.append(sca_time_obs_datetime[i])
        sca_lat_obs_list.append(
            latitude_of_DEM_intersection_obs[L1B_start_time_obs_datetime == sca_time_obs_datetime[i]][0])
        sca_lon_obs_list.append(
            longitude_of_DEM_intersection_obs[L1B_start_time_obs_datetime == sca_time_obs_datetime[i]][0])

sca_time_obs_array = np.asarray(sca_time_obs_list)
sca_lat_obs_array = np.asarray(sca_lat_obs_list)
sca_lon_obs_array = np.asarray(sca_lon_obs_list)
print(sca_time_obs_array)
quit()
for m in range(np.size(sca_time_obs_array)):

    year_m = '{:04d}'.format(sca_time_obs_array[m].year)
    month_m = '{:02d}'.format(sca_time_obs_array[m].month)
    day_m = '{:02d}'.format(sca_time_obs_array[m].day)
    hour_m = '{:02d}'.format(sca_time_obs_array[m].hour)
    minute_m = '{:02d}'.format(sca_time_obs_array[m].minute)
    second_m = '{:02d}'.format(sca_time_obs_array[m].second)

    logging.info(
        '----------> Search colocated CALIOP profiles based on Aeolus location: (%.2f, %.2f) at %s-%s-%s %s:%s:%s'
        % (sca_lat_obs_array[m], sca_lon_obs_array[m], year_m, month_m, day_m, hour_m, minute_m,
           second_m))

    caliop_interval_start = sca_time_obs_array[m] - timedelta(days=1)

    while caliop_interval_start <= sca_time_obs_array[m] + timedelta(days=1):

        caliop_fetch_dir = CALIOP_JASMIN_dir + '%s/%s_%s_%s/' % (
            caliop_interval_start.year,
            caliop_interval_start.year,
            '{:02d}'.format(caliop_interval_start.month),
            '{:02d}'.format(caliop_interval_start.day))

        for file in os.listdir(caliop_fetch_dir):

            if file.endswith('hdf'):

                caliop_file_datetime = datetime.strptime(file[-25:-6], '%Y-%m-%dT%H-%M-%S')

                if caliop_file_datetime - sca_time_obs_array[m] < timedelta(hours=24):

                    caliop_request = Caliop_hdf_reader()
                    caliop_interval_latitude = caliop_request._get_latitude(caliop_fetch_dir + file)
                    caliop_interval_longitude = caliop_request._get_longitude(caliop_fetch_dir + file)

                    aeolus_caliop_distance = [geopy.distance.geodesic((
                        sca_lat_obs_array[m], sca_lon_obs_array[m]),
                        (caliop_interval_latitude[k], caliop_interval_longitude[k])).km
                                              for k in range(len(caliop_interval_latitude))]
                    aeolus_caliop_distance = np.asarray(aeolus_caliop_distance)

                    if len(aeolus_caliop_distance[aeolus_caliop_distance < spatial_threshold]) >= 1:
                        logging.info(
                            '----------> Colocation profiles found ......')
                        logging.info(
                            '----------> Saving AEOLUS and CALIOP colocation information ......')

                        saving_dir = database_dir + '/%s/%s-%s-%s' % (year_m, year_m, month_m, day_m)
                        try:
                            os.stat(saving_dir)
                        except:
                            pathlib.Path(saving_dir).mkdir(parents=True, exist_ok=True)

                        with open(saving_dir + '/AEOLUS-%s%s%sT%s%s%s.csv' %
                                  (year_m, month_m, day_m,
                                   hour_m, minute_m, second_m), "w") as output:

                            writer = csv.writer(output, lineterminator='\n')
                            writer.writerow(('AEOLUS_latitude', 'AEOLUS_longitude', 'CALIOP_filename'))
                            writer.writerow(
                                (sca_lat_obs_array[m], sca_lon_obs_array[m], file))

        caliop_interval_start += timedelta(days=1)
