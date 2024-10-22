#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    produce_global_colocation_daily.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        01/02/2023 14:49

# Import external libraries
import os
import sys
import argparse
import pathlib
import logging
import csv

# Import internal modules
sys.path.append('../')
from getColocationData.save_colocated_data import *
from getColocationData.get_reprojection import *
from getColocationData.get_basemap import *
from getColocationData.get_aeolus import *
from getColocationData.get_caliop import *
from datetime import datetime, timedelta

##############################################################
# start_date = '2019-01-01' # start data for analysis
# end_date   = '2019-01-01' # end date for analysis

with open(sys.argv[1], newline='') as csvfile:
    csvreader = csv.reader(csvfile, delimiter=',')
    row_index = 0
    for row in csvreader:
        if row_index == 1:
            start_date = row[0]
            end_date = row[1]
        row_index += 1

temporal_wd = 10. # hours of temporal window
lat_up = 90.
lat_down = -90.
lon_left = -180.
lon_right = 180.
##############################################################

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

# Set up data directories
# aeolus data mirror
Aeolus_JASMIN_dir = '/gws/pw/j07/nceo_aerosolfire/rsong/project/global_aerosol/aeolus_archive'
# caliop v-20 and v-21 data
CALIOP_JASMIN_dir = '/gws/nopw/j04/eo_shared_data_vol1/satellite/calipso/APro5km'
# colocation footprint data in csv files
colocation_fp_dir = '/gws/pw/j07/nceo_aerosolfire/rsong/project/global_aerosol/Colocation/colocation_database'
# dir to save graphs and netcdf
savenc_dir = '/gws/pw/j07/nceo_aerosolfire/rsong/project/global_aerosol/Database_v2'

cwd = os.getcwd()

# Set up time delta
time_delta = timedelta(days = 1)

# Parse start and end dates
start_date_datetime = datetime.strptime(start_date, '%Y-%m-%d-%M%S')
end_date_datetime = datetime.strptime(end_date, '%Y-%m-%d-%M%S')

# Initialize lists for datetime strings and netCDF files
datetime_str_list = []
ncFile_list = []



# Iterate through date range
while start_date_datetime <= end_date_datetime:

    year_i = '{:04d}'.format(start_date_datetime.year)
    month_i = '{:02d}'.format(start_date_datetime.month)
    day_i = '{:02d}'.format(start_date_datetime.day)
    hour_i = '{:02d}'.format(start_date_datetime.hour)
    minute_i = '{:02d}'.format(start_date_datetime.minute)

    logger.info('#############################################################')
    logger.info('Start searching colocations for: %s-%s-%s %s:%s +1 hour' % (year_i, month_i, day_i, hour_i, minute_i))
    logger.info('#############################################################')

    search_year = year_i
    search_month = month_i
    search_day = day_i

    savenc_subdir = savenc_dir + '/%s/%s-%s-%s' % (year_i, year_i, month_i, day_i)

    try:
        os.stat(savenc_subdir)
    except:
        pathlib.Path(savenc_subdir).mkdir(parents=True, exist_ok=True)

    with open(savenc_subdir + '/colocation_ref_%s.csv' % start_date, "w") as output:

        writer = csv.writer(output, lineterminator='\n')
        writer.writerow(('Colocation_Datetime', 'Parameter_File_Location'))

    # locate the daily footprint data directory
    colocation_dir_daily = colocation_fp_dir + '/%s/%s-%s-%s/' % (search_year, search_year, search_month, search_day)

    if os.path.isdir(colocation_dir_daily):

        for file in os.listdir(colocation_dir_daily):

            aeolus_time_str = (file.split('AEOLUS-'))[1].split('.csv')[0]
            aeolus_time_datetime = datetime.strptime(aeolus_time_str, '%Y%m%dT%H%M%S')

            input_file = colocation_dir_daily + file

            with open(input_file, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                try:
                    for row in reader:
                        lat_colocation = float(row['AEOLUS_latitude'])
                        lon_colocation = float(row['AEOLUS_longitude'])
                        caliop_filename = row['CALIOP_filename']

                        if lat_colocation > 180.:
                            lat_colocation = lat_colocation - 360.
                        if lon_colocation > 180.:
                            lon_colocation = lon_colocation - 360.
                except:
                    logger.error('Error reading colocation footprint')
                    continue

            logger.info('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
            logger.info('Fetching colocations......')
            logger.info('lat, lon: (%.2f, %.2f)' % (float(lat_colocation), float(lon_colocation)))

            if (lat_colocation > lat_down) & (lat_colocation < lat_up) & (lon_colocation > lon_left) & (lon_colocation < lon_right):

                # (lat_m, lon_m, aod_m) = get_MODIS_aod(float(lat_aeolus), float(lon_aeolus), aeolus_time_datetime, cwd,
                #                                       savefig_dir)

                aeolus_colocation_file = Aeolus_JASMIN_dir + '/%s-%s/%s-%s-%s.nc' % \
                                         (search_year, search_month, search_year, search_month, search_day)

                (footprint_lat_aeolus, footprint_lon_aeolus, altitude_aeolus,
                 footprint_time_aeolus, beta_aeolus_mb, alpha_aeolus_mb,
                 qc_aeolus_mb, ber_aeolus_mb, lod_aeolus_mb) = \
                    extract_variables_from_aeolus(aeolus_colocation_file, logger)

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

                cliop_time_datetime = datetime.strptime(caliop_colocation_file[-25:-6], '%Y-%m-%dT%H-%M-%S')
                abs_temportal_distance = abs(aeolus_time_datetime - cliop_time_datetime)
                abs_temportal_total_seconds = abs_temportal_distance.total_seconds()
                abs_temportal_total_hours = abs_temportal_total_seconds / 3600.

                if abs_temportal_distance < timedelta(hours=temporal_wd):
                    (footprint_lat_caliop, footprint_lon_caliop,
                     alt_caliop, beta_caliop, alpha_caliop,
                     aerosol_type_caliop, feature_type_caliop, caliop_Depolarization_Ratio_list) \
                        = extract_variables_from_caliop(caliop_colocation_file, logger)

                    (lat_aeolus_cutoff, lon_aeolus_cutoff, alt_aeolus_cutoff,
                     beta_aeolus_cutoff, alpha_aeolus_cutoff,
                     qc_aeolus_cutoff, ber_aeolus_cutoff, lod_aeolus_cutoff,
                     lat_caliop_cutoff, lon_caliop_cutoff, beta_caliop_cutoff, alpha_caliop_cutoff,
                     aerosol_type_caliop_cutoff, feature_type_caliop_cutoff, depolarization_ratio_caliop_cutoff) = \
                        reproject_observations(lat_colocation, lon_colocation, aeolus_time_datetime,
                                               footprint_lat_aeolus, footprint_lon_aeolus, altitude_aeolus,
                                               footprint_time_aeolus, beta_aeolus_mb, alpha_aeolus_mb,
                                               qc_aeolus_mb, ber_aeolus_mb, lod_aeolus_mb,
                                               footprint_lat_caliop, footprint_lon_caliop, beta_caliop,
                                               alpha_caliop, aerosol_type_caliop,
                                               feature_type_caliop, caliop_Depolarization_Ratio_list,
                                               interval=10)

                    beta_aeolus_resample = resample_aeolus(lat_aeolus_cutoff, alt_aeolus_cutoff, beta_aeolus_cutoff, alt_caliop)
                    alpha_aeolus_resample = resample_aeolus(lat_aeolus_cutoff, alt_aeolus_cutoff, alpha_aeolus_cutoff, alt_caliop)

                    colocation_info = 'Temporal distance = %.1f hours'%(abs_temportal_total_hours)

                    saveFilenameNC = savenc_subdir + '/%s.nc'%aeolus_time_str
                    saveFilenamePNG = savenc_subdir + '/%s.png' % aeolus_time_str

                    (tem_dis, spa_dis) = plot_grid_tiles(lat_colocation, lon_colocation, lat_aeolus_cutoff,
                                                         lon_aeolus_cutoff, alt_aeolus_cutoff, beta_aeolus_resample,
                                                         alpha_aeolus_resample, lat_caliop_cutoff, lon_caliop_cutoff,
                                                         alt_caliop, beta_caliop_cutoff, alpha_caliop_cutoff,
                                                         aerosol_type_caliop_cutoff, feature_type_caliop_cutoff,
                                                         savefigname=saveFilenamePNG,
                                                         title='%s/%s/%s CALIOP-AEOLUS Co-located Level-2 Profiles'%(search_day, search_month, search_year),
                                                         colocation_info=colocation_info, tem_dis = abs_temportal_total_hours, logger=logger)

                    save_colocation_nc(saveFilenameNC, lat_colocation, lon_colocation, lat_aeolus_cutoff, lon_aeolus_cutoff, alt_aeolus_cutoff,
                                       beta_aeolus_cutoff, alpha_aeolus_cutoff, qc_aeolus_cutoff, ber_aeolus_cutoff, lod_aeolus_cutoff,
                                       lat_caliop_cutoff, lon_caliop_cutoff, alt_caliop, beta_caliop_cutoff, alpha_caliop_cutoff,
                                       aerosol_type_caliop_cutoff, feature_type_caliop_cutoff, depolarization_ratio_caliop_cutoff,
                                       tem_dis, spa_dis)

                    datetime_str_list.append('%s'%aeolus_time_str)
                    ncFile_list.append(saveFilenameNC)

                    with open(savenc_subdir + '/colocation_ref_%s.csv' % start_date, "a") as output:

                        writer = csv.writer(output, lineterminator='\n')
                        writer.writerow((aeolus_time_str, saveFilenameNC))

                else:
                    logger.warning("Colocation profiles exceed minimum temporal window, go to next......")

            else:
                logger.warning("Colocation profiles exceed the AOI, go to next......")
    else:
        logger.warning(f'{colocation_dir_daily} not exists, no colocation data found.')



    start_date_datetime = start_date_datetime + time_delta






