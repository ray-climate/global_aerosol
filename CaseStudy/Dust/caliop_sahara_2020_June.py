#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    caliop_sahara_2020_June.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        16/02/2023 18:26

from datetime import datetime, timedelta
import logging
import pathlib
import sys
import os

##############################################################
# Define start and end dates
start_date = '2020-06-15'
end_date = '2020-06-21'

# Define the spatial bounds
lat_up = 37.
lat_down = 1.
lon_left = -72.
lon_right = 31.

# Set up time delta
time_delta = timedelta(days = 1)
##############################################################

##############################################################
def get_script_name():
    return sys.modules['__main__'].__file__

# Get the name of the script
script_name = get_script_name()

# Split the script name into a base name and an extension
script_base, script_ext = os.path.splitext(script_name)

output_dir = './%s' %script_base
# Create output directories if they don't exist
##############################################################

# Add the .log extension to the base name
log_filename = script_base + '.log'

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                    filemode='w',
                    filename=log_filename,
                    level=logging.INFO)

# Get a logger object
logger = logging.getLogger()

##############################################################
# add data directory
CALIOP_JASMIN_dir = '/gws/nopw/j04/eo_shared_data_vol1/satellite/calipso/APro5km/'
try:
    os.stat(output_dir)
except:
    pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True)
##############################################################

# Parse start and end dates
start_date_datetime = datetime.strptime(start_date, '%Y-%m-%d')
end_date_datetime = datetime.strptime(end_date, '%Y-%m-%d')

print(start_date_datetime)
while start_date_datetime <= end_date_datetime:

    year_i = '{:04d}'.format(start_date_datetime.year)
    month_i = '{:02d}'.format(start_date_datetime.month)
    day_i = '{:02d}'.format(start_date_datetime.day)
    hour_i = '{:02d}'.format(start_date_datetime.hour)
    minute_i = '{:02d}'.format(start_date_datetime.minute)

    caliop_fetch_dir = CALIOP_JASMIN_dir + '%s/%s_%s_%s/' % (year_i,year_i,month_i,day_i)

    for file in os.listdir(caliop_fetch_dir):
        if file.endswith('hdf'):
            print('Find data: %s'%file)

    start_date_datetime = start_date_datetime + time_delta


