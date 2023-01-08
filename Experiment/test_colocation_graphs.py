#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    test_colocation_graphs.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        08/01/2023 14:54

import os
import sys
sys.path.append('../')

from datetime import datetime, timedelta
import logging
import csv

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                    filemode='w',
                    filename=sys.modules['__main__'].__file__,
                    level=logging.INFO)

# Get a logger object
logger = logging.getLogger()

# aeolus data mirror
Aeolus_JASMIN_dir = '/gws/pw/j07/nceo_aerosolfire/rsong/project/global_aerosol/aeolus_archive'
# caliop v-20 and v-21 data
CALIOP_JASMIN_dir = '/gws/nopw/j04/eo_shared_data_vol1/satellite/calipso/APro5km'
# colocation footprint data in csv files
colocation_fp_dir = '/gws/pw/j07/nceo_aerosolfire/rsong/project/global_aerosol/Colocation/colocation_database'
# dir to save graphs and netcdf
savefig_dir = '/gws/pw/j07/nceo_aerosolfire/rsong/project/global_aerosol/getColocationData/figures'
cwd = os.getcwd()

start_date = '2019-05-03' # start data for analysis
end_date   = '2019-05-04' # end date for analysis
time_delta = timedelta(days = 1)

start_date_datetime = datetime.strptime(start_date, '%Y-%m-%d')
end_date_datetime = datetime.strptime(end_date, '%Y-%m-%d')

while start_date_datetime <= end_date_datetime:

    year_i = '{:04d}'.format(start_date_datetime.year)
    month_i = '{:02d}'.format(start_date_datetime.month)
    day_i = '{:02d}'.format(start_date_datetime.day)
    logging.info('#############################################################')
    logging.info('Start searching colocations for: %s-%s-%s' % (year_i, month_i, day_i))
    logging.info('#############################################################')

    search_year = year_i
    search_month = month_i
    search_day = day_i

    # locate the daily footprint data directory
    colocation_dir_daily = colocation_fp_dir + '/%s/%s-%s-%s/' % (search_year, search_year, search_month, search_day)

    for file in os.listdir(colocation_dir_daily):

        aeolus_time_str = (file.split('AEOLUS-'))[1].split('.csv')[0]
        aeolus_time_datetime = datetime.strptime(aeolus_time_str, '%Y%m%dT%H%M%S')

        input_file = colocation_dir_daily + file

        with open(input_file, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                lat_aeolus = row['AEOLUS_latitude']
                lon_aeolus = row['AEOLUS_longitude']
                caliop_filename = row['CALIOP_filename']

        logging.info('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
        logging.info('Fetching colocations for lat lon: %.2f, %.2f' % (float(lat_aeolus), float(lon_aeolus)))
        # (lat_m, lon_m, aod_m) = get_MODIS_aod(float(lat_aeolus), float(lon_aeolus), aeolus_time_datetime, cwd,
        #                                       savefig_dir)

        aeolus_colocation_file = Aeolus_JASMIN_dir + '/%s-%s/%s-%s-%s.nc' % \
                                 (search_year, search_month, search_year, search_month, search_day)