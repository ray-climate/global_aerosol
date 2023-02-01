#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    generate_colocation_global.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        23/11/2022 13:02

import sys
sys.path.append('../')

from Caliop.caliop import Caliop_hdf_reader
from datetime import datetime, timedelta
from Aeolus.aeolus import *
import geopy.distance
import pandas as pd
import numpy as np
import pathlib
import logging
import time
import csv
import sys
import os

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                    filemode='w',
                    filename='../Colocation/aeolus_caliop_global_colocation.log',
                    level=logging.INFO)

CALIOP_JASMIN_dir = '/gws/nopw/j04/eo_shared_data_vol1/satellite/calipso/APro5km/'
database_dir = '../Colocation/database'

try:
    os.stat(database_dir)
except:
    os.mkdir(database_dir)

spatial_threshold = 200. # 200km threshold

with open(sys.argv[1], newline='') as csvfile:
    csvreader = csv.reader(csvfile, delimiter=',')
    row_index = 0
    for row in csvreader:
        if row_index == 1:
            start_date = row[0]
            end_date = row[1]
        row_index += 1

# start_date = '2019-01-01 00:00' # start date of search colocations, year-month-day
# end_date = '2022-01-01 00:00' # end date of search colocations, year-month-day
time_delta = timedelta(hours = 1) # time delta for separating Aeolus measuremets

start_date_datetime = datetime.strptime(start_date, '%Y-%m-%d %H:%M')
end_date_datetime = datetime.strptime(end_date, '%Y-%m-%d %H:%M')
AEOLUS_DATA_PRODUCT = "ALD_U_N_2A"

queue_folder = './queue_status'

try:
    os.stat(queue_folder)
except:
    os.mkdir(queue_folder)

time.sleep(float(sys.argv[2]) * 15.) # sbatch job ID * 10s

while start_date_datetime <= end_date_datetime:

    year_i = '{:04d}'.format(start_date_datetime.year)
    month_i = '{:02d}'.format(start_date_datetime.month)
    day_i = '{:02d}'.format(start_date_datetime.day)
    hour_i = '{:02d}'.format(start_date_datetime.hour)
    minute_i = '{:02d}'.format(start_date_datetime.minute)
    print('%s-%s-%s %s:%s'%(year_i, month_i, day_i, hour_i, minute_i))
    # database_subdir = database_dir + '/%s-%s-%s'%()

    aeolus_interval_start = start_date_datetime
    aeolus_interval_end = start_date_datetime + time_delta

    ds_sca_index = 0
    while ds_sca_index == 0:
        try:
            VirES_request = GetAeolusFromVirES(measurement_start=aeolus_interval_start,
                                               measurement_stop=aeolus_interval_end,
                                               DATA_PRODUCT=AEOLUS_DATA_PRODUCT)
            ds_sca_index += 1
            os.system('cp ./queue.txt %s/task_%s_queue_entered.txt'%(queue_folder, sys.argv[2]))

        except:
            logging.warning('vires sever request busy, retring in 10 seconds...')
            time.sleep(10)
    try:
        ds_sca = VirES_request._get_ds_sca()
    except:
        logging.warning('One or more Aeolus parameters are not able to be derived from this time range.')

    aeolus_interval_latitude = ds_sca['latitude_of_DEM_intersection_obs']
    aeolus_interval_longitude = ds_sca['longitude_of_DEM_intersection_obs']
    aeolus_interval_timestamp = ds_sca['sca_time_obs_datetime']
    aeolus_interval_timestamp = pd.to_datetime(aeolus_interval_timestamp)

    for j in range(len(aeolus_interval_latitude)):

        year_j = '{:04d}'.format(aeolus_interval_timestamp[j].year)
        month_j = '{:02d}'.format(aeolus_interval_timestamp[j].month)
        day_j = '{:02d}'.format(aeolus_interval_timestamp[j].day)
        hour_j = '{:02d}'.format(aeolus_interval_timestamp[j].hour)
        minute_j = '{:02d}'.format(aeolus_interval_timestamp[j].minute)
        second_j = '{:02d}'.format(aeolus_interval_timestamp[j].second)

        logging.info(
            '----------> Search colocated CALIOP profiles based on Aeolus location: (%.2f, %.2f) at %s-%s-%s %s:%s:%s'
            % (aeolus_interval_latitude[j], aeolus_interval_longitude[j], year_j, month_j, day_j, hour_j, minute_j,
               second_j))

        caliop_interval_start = aeolus_interval_timestamp[j] - timedelta(days = 1)

        while caliop_interval_start <= aeolus_interval_timestamp[j] + timedelta(days = 1):

            caliop_fetch_dir = CALIOP_JASMIN_dir + '%s/%s_%s_%s/'%(
                caliop_interval_start.year,
                caliop_interval_start.year,
                '{:02d}'.format(caliop_interval_start.month),
                '{:02d}'.format(caliop_interval_start.day))

            for file in os.listdir(caliop_fetch_dir):

                if file.endswith('hdf'):

                    caliop_file_datetime = datetime.strptime(file[-25:-6], '%Y-%m-%dT%H-%M-%S')

                    if caliop_file_datetime - aeolus_interval_timestamp[j] < timedelta(hours=24):

                        caliop_request = Caliop_hdf_reader()
                        caliop_interval_latitude = caliop_request._get_latitude(caliop_fetch_dir + file)
                        caliop_interval_longitude = caliop_request._get_longitude(caliop_fetch_dir + file)

                        aeolus_caliop_distance = [geopy.distance.geodesic((
                            aeolus_interval_latitude[j], aeolus_interval_longitude[j]),
                            (caliop_interval_latitude[k], caliop_interval_longitude[k])).km
                                                  for k in range(len(caliop_interval_latitude))]
                        aeolus_caliop_distance = np.asarray(aeolus_caliop_distance)

                        if len(aeolus_caliop_distance[aeolus_caliop_distance < spatial_threshold]) >= 1:
                            logging.info(
                                '----------> Colocation profiles found ......')
                            logging.info(
                                '----------> Saving AEOLUS and CALIOP colocation information ......')

                            saving_dir = database_dir + '/%s/%s-%s-%s'%(year_j, year_j, month_j, day_j)
                            try:
                                os.stat(saving_dir)
                            except:
                                pathlib.Path(saving_dir).mkdir(parents=True, exist_ok=True)

                            with open(saving_dir + '/AEOLUS-%s%s%sT%s%s%s.csv' %
                                      (year_j, month_j, day_j,
                                       hour_j, minute_j, second_j) , "w") as output:

                                writer = csv.writer(output, lineterminator='\n')
                                writer.writerow(('AEOLUS_latitude', 'AEOLUS_longitude', 'CALIOP_filename'))
                                writer.writerow((aeolus_interval_latitude[j].values, aeolus_interval_longitude[j].values, file))

            caliop_interval_start += timedelta(days = 1)
        print('---------------------')

    start_date_datetime += time_delta

os.system('mv %s %s_complete.csv'%(sys.argv[1], sys.argv[1][0:-4]))