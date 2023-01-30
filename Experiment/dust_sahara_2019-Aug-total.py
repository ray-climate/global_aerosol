#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    dust_sahara_2019-Aug-total.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        27/01/2023 13:19

# Import external libraries
from datetime import datetime, timedelta
import logging
import sys
import os

# Import internal modules
sys.path.append('../')
from readColocationData.readColocationNetCDF import *

"""
This code uses all pre-calculated colocation files to do the retrieval analysis and comparison.
"""

##############################################################
start_date = '2019-08-24' # start data for analysis
end_date   = '2019-08-31' # end date for analysis
temporal_wd = 10. # hours of temporal window
lat_up = 38.
lat_down = 5.
lon_left = -52.
lon_right = 0.
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
                (beta_aeolus_i, beta_caliop_stats_i) = extractColocationParameters(colocationData_daily_dir + file)
                beta_aeolus_all.extend(beta_aeolus_i)
                beta_caliop_all.extend(beta_caliop_stats_i)
                print(len(beta_aeolus_all))
                print(len(beta_aeolus_all))

    else:
        print('No colocation for %s-%s-%s'%(year_i, month_i, day_i))

    start_date_datetime = start_date_datetime + time_delta

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Convert data to pandas dataframe
data = np.array([beta_aeolus_all, beta_caliop_all]).T

fig, ax = plt.subplots(figsize=(12, 12))
sns.kdeplot(data, shade=True, cmap="Blues")
ax.set_xlabel('beta_caliop_all')
ax.set_ylabel('beta_aeolus_all')
plt.xlim([0.,0.05])
plt.ylim([0.,0.05])
plt.savefig('./beta_all.png')