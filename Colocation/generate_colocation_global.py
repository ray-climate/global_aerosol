#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    generate_colocation_global.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        23/11/2022 13:02

import sys
sys.path.append('../')

from datetime import datetime, timedelta
from Aeolus.aeolus import *
import pandas as pd
import numpy as np
import logging
import sys
import os

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                    filemode='w',
                    filename= './aeolus_caliop_global_colocation.log',
                    level=logging.INFO)

CALIOP_JASMIN_dir = '/gws/nopw/j04/eo_shared_data_vol1/satellite/calipso/APro5km/'
database_dir = './database'

try:
    os.stat(database_dir)
except:
    os.mkdir(database_dir)

start_date = '2019-01-01 00:00' # start date of search colocations, year-month-day
end_date = '2022-01-01 00:00' # end date of search colocations, year-month-day
time_delta = timedelta(hours = 1) # time delta for separating Aeolus measuremets

start_date_datetime = datetime.strptime(start_date, '%Y-%m-%d %H:%M')
end_date_datetime = datetime.strptime(end_date, '%Y-%m-%d %H:%M')
AEOLUS_DATA_PRODUCT = "ALD_U_N_2A"


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
    VirES_request = GetAeolusFromVirES(measurement_start=aeolus_interval_start,
                                       measurement_stop=aeolus_interval_end,
                                       DATA_PRODUCT=AEOLUS_DATA_PRODUCT)
    ds_sca = VirES_request._get_ds_sca()

    aeolus_interval_latitude = ds_sca['latitude_of_DEM_intersection_obs']
    aeolus_interval_longitude = ds_sca['longitude_of_DEM_intersection_obs']
    aeolus_interval_timestamp = ds_sca['SCA_time_obs_datetime']
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
                print(caliop_fetch_dir + file)
            caliop_interval_start += timedelta(days = 1)
        print('---------------------')


    quit()
    start_date_datetime += time_delta