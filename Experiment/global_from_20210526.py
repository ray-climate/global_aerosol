#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    global_from_20210526.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        03/02/2023 15:21

# Import external libraries
from datetime import datetime, timedelta
import logging
import sys
import os

# Import internal modules
import numpy as np

sys.path.append('../')
from readColocationData.readColocationNetCDF import *

"""
This code uses all pre-calculated colocation files to do the retrieval analysis and comparison.
"""

##############################################################
start_date = '2021-05-26' # start data for analysis
end_date   = '2021-07-01' # end date for analysis
temporal_wd = 10. # hours of temporal window
lat_up = 60.
lat_down = -60.
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

colocationData_dir = '/gws/pw/j07/nceo_aerosolfire/rsong/project/global_aerosol/Database'

# Parse start and end dates
start_date_datetime = datetime.strptime(start_date, '%Y-%m-%d')
end_date_datetime = datetime.strptime(end_date, '%Y-%m-%d')

# Set up time delta
time_delta = timedelta(days = 1)

beta_aeolus_all = []
beta_caliop_all = []

# Iterate through date range
while start_date_datetime <= end_date_datetime:

    year_i = '{:04d}'.format(start_date_datetime.year)
    month_i = '{:02d}'.format(start_date_datetime.month)
    day_i = '{:02d}'.format(start_date_datetime.day)

    # locate the daily colocation observation parameter from satellite data
    colocationData_daily_dir = colocationData_dir + '/%s/%s-%s-%s/' % (year_i, year_i, month_i, day_i)

    if os.path.isdir(colocationData_daily_dir):
        for file in os.listdir(colocationData_daily_dir):
            if file.endswith('.nc'):
                print(file)
                (beta_aeolus_i, beta_caliop_i) = extractColocationParameters(colocationData_daily_dir + file)
                beta_aeolus_all.extend(beta_aeolus_i)
                beta_caliop_all.extend(beta_caliop_i)

    else:
        print('No colocation for %s-%s-%s'%(year_i, month_i, day_i))

    start_date_datetime = start_date_datetime + time_delta

beta_aeolus_all = np.asarray(beta_aeolus_all)
beta_caliop_all = np.asarray(beta_caliop_all)

import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde

x = beta_caliop_all[(beta_caliop_all > 0) & (beta_aeolus_all > 0)]
y = beta_aeolus_all[(beta_caliop_all > 0) & (beta_aeolus_all > 0)]
xy = np.vstack([x,y])
z = gaussian_kde(xy)(xy)

fig, ax = plt.subplots(figsize=(8, 8))
ax.scatter(x, y, c=z, s=100)
ax.set_xlabel('beta_caliop_all')
ax.set_ylabel('beta_aeolus_all')
plt.xlim([0.,0.01])
plt.ylim([0.,0.01])
plt.savefig('./beta_all_from_20210526.png')