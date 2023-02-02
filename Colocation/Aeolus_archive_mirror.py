#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    Aeolus_archive_mirror.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        30/11/2022 14:08

import sys
sys.path.append('../')

from datetime import datetime, timedelta
from Aeolus.aeolus import *
import pathlib
import logging

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                    filemode='w',
                    filename= './aeolus_archive_mirror.log',
                    level=logging.INFO)

start_date = '2021-01-01 00:00' # start date of search colocations, year-month-day
end_date = '2022-01-01 00:00' # end date of search colocations, year-month-day
time_delta = timedelta(days = 1)

save_dir = '/gws/pw/j07/nceo_aerosolfire/rsong/project/global_aerosol/aeolus_archive'

start_date_datetime = datetime.strptime(start_date, '%Y-%m-%d %H:%M')
end_date_datetime = datetime.strptime(end_date, '%Y-%m-%d %H:%M')
AEOLUS_DATA_PRODUCT = "ALD_U_N_2A"

while start_date_datetime <= end_date_datetime:

    year_i = '{:04d}'.format(start_date_datetime.year)
    month_i = '{:02d}'.format(start_date_datetime.month)
    day_i = '{:02d}'.format(start_date_datetime.day)
    hour_i = '{:02d}'.format(start_date_datetime.hour)
    minute_i = '{:02d}'.format(start_date_datetime.minute)
    print('mirror data for: %s-%s-%s %s:%s' % (year_i, month_i, day_i, hour_i, minute_i))

    aeolus_interval_start = start_date_datetime
    aeolus_interval_end = start_date_datetime + time_delta
    sub_dir = save_dir + '/%s-%s'%(year_i, month_i)

    try:
        os.stat(sub_dir)
    except:
        pathlib.Path(sub_dir).mkdir(parents=True, exist_ok=True)

    download_index = 0
    download_success = 'False'

    while download_index < 2:
        try:
            VirES_request = SaveVirESNetcdf(measurement_start=start_date_datetime,
                                            measurement_stop=aeolus_interval_end,
                                            DATA_PRODUCT=AEOLUS_DATA_PRODUCT,
                                            save_filename=sub_dir + '/%s-%s-%s.nc'%(year_i, month_i, day_i))
            download_success = 'True'
            download_index = download_index + 2
        except:
            download_index = download_index + 1

    if download_success == 'True':
        logging.info('Success: saved netCDF for %s-%s-%s'% (year_i, month_i, day_i))
    else:
        logging.info('Failed: saved netCDF for %s-%s-%s' % (year_i, month_i, day_i))

    start_date_datetime += time_delta
