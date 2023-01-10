#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    test_colocation_graphs.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        08/01/2023 14:54

import os
import sys
sys.path.append('../')

from getColocationData.get_reprojection import *
from getColocationData.get_basemap import *
from getColocationData.get_aeolus import *
from getColocationData.get_caliop import *
from datetime import datetime, timedelta
import logging
import csv

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
    logger.info('#############################################################')
    logger.info('Start searching colocations for: %s-%s-%s' % (year_i, month_i, day_i))
    logger.info('#############################################################')

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
                lat_colocation = float(row['AEOLUS_latitude'])
                lon_colocation = float(row['AEOLUS_longitude'])
                caliop_filename = row['CALIOP_filename']

                if lat_colocation > 180.:
                    lat_colocation = lat_colocation - 360.
                if lon_colocation > 180.:
                    lon_colocation = lon_colocation - 360.

        logger.info('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
        logger.info('Fetching colocations for lat lon: %.2f, %.2f' % (float(lat_colocation), float(lon_colocation)))
        # (lat_m, lon_m, aod_m) = get_MODIS_aod(float(lat_aeolus), float(lon_aeolus), aeolus_time_datetime, cwd,
        #                                       savefig_dir)

        aeolus_colocation_file = Aeolus_JASMIN_dir + '/%s-%s/%s-%s-%s.nc' % \
                                 (search_year, search_month, search_year, search_month, search_day)

        (footprint_lat_aeolus, footprint_lon_aeolus, footprint_time_aeolus) = extract_variables_from_aeolus(aeolus_colocation_file, logger)

        # Search for the file on the specified date
        caliop_colocation_file = find_caliop_file(CALIOP_JASMIN_dir, caliop_filename, start_date_datetime)

        # If the file is not found, search for the file on the previous day
        if caliop_colocation_file is None:
            caliop_colocation_file = find_caliop_file(CALIOP_JASMIN_dir, caliop_filename,
                                                      start_date_datetime - timedelta(days=1))

        # If the file is still not found, search for the file on the following day
        if caliop_colocation_file is None:
            caliop_colocation_file = find_caliop_file(CALIOP_JASMIN_dir, caliop_filename,
                                                      start_date_datetime + timedelta(days=1))

        # If the file is still not found after searching the specified date and the previous and following days, raise an error
        if caliop_colocation_file is None:
            logger.error("CALIOP file not found in specified date or surrounding days")

        (footprint_lat_caliop, footprint_lon_caliop, footprint_altitude_caliop, beta_caliop) = extract_variables_from_caliop(caliop_colocation_file, logger)
        print(footprint_lat_caliop.shape)
        print(footprint_altitude_caliop.shape)
        print(beta_caliop.shape)
        quit()
        (lat_aeolus_cutoff, lon_aeolus_cutoff, lat_caliop_cutoff, lon_caliop_cutoff, beta_caliop_cutoff) = \
            reproject_observations(lat_colocation, lon_colocation, aeolus_time_datetime,
                               footprint_lat_aeolus, footprint_lon_aeolus, footprint_time_aeolus,
                               footprint_lat_caliop, footprint_lon_caliop, beta_caliop,
                               interval=10)

        plot_grid_tiles(lat_colocation, lon_colocation, lat_aeolus_cutoff, lon_aeolus_cutoff, lat_caliop_cutoff, lon_caliop_cutoff, beta_caliop_cutoff)

        quit()
