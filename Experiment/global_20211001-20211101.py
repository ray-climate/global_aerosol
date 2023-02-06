#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    global_20211001-20211101.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        06/02/2023 12:21

# Import external libraries

from datetime import datetime, timedelta
from scipy.stats import gaussian_kde
import matplotlib.pyplot as plt
from matplotlib import colors
import numpy as np
import logging
import csv
import sys
import os

sys.path.append('../')
from readColocationData.readColocationNetCDF import *

"""
This code uses all pre-calculated colocation files to do the retrieval analysis and comparison.
"""

##############################################################
start_date = '2021-06-01' # start data for analysis
end_date   = '2021-12-01' # end date for analysis
temporal_wd = 5. # hours of temporal window
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
#
# colocationData_dir = '/gws/pw/j07/nceo_aerosolfire/rsong/project/global_aerosol/Database'
#
# # Parse start and end dates
# start_date_datetime = datetime.strptime(start_date, '%Y-%m-%d')
# end_date_datetime = datetime.strptime(end_date, '%Y-%m-%d')
#
# # Set up time delta
# time_delta = timedelta(days = 1)
#
# beta_aeolus_all = []
# beta_caliop_all = []
# alt_bottom_all = []
# alt_top_all = []
# time_str_all = []
# qc_aeolus_all = []
# ber_aeolus_all = []
# lod_aeolus_all = []
#
# # Iterate through date range
# while start_date_datetime <= end_date_datetime:
#
#     year_i = '{:04d}'.format(start_date_datetime.year)
#     month_i = '{:02d}'.format(start_date_datetime.month)
#     day_i = '{:02d}'.format(start_date_datetime.day)
#
#     # locate the daily colocation observation parameter from satellite data
#     colocationData_daily_dir = colocationData_dir + '/%s/%s-%s-%s/' % (year_i, year_i, month_i, day_i)
#
#     if os.path.isdir(colocationData_daily_dir):
#         for file in os.listdir(colocationData_daily_dir):
#             if file.endswith('.nc'):
#                 print(file)
#
#                 (beta_aeolus_i, beta_caliop_i, alt_bottom_i, alt_top_i, time_str_i, qc_i, ber_i,
#                  lod_i) = extractColocationParameters(colocationData_daily_dir + file)
#                 beta_aeolus_all.extend(beta_aeolus_i)
#                 beta_caliop_all.extend(beta_caliop_i)
#                 alt_bottom_all.extend(alt_bottom_i)
#                 alt_top_all.extend(alt_top_i)
#                 time_str_all.extend(time_str_i)
#                 qc_aeolus_all.extend(qc_i)
#                 ber_aeolus_all.extend(ber_i)
#                 lod_aeolus_all.extend(lod_i)
#
#     else:
#         print('No colocation for %s-%s-%s'%(year_i, month_i, day_i))
#
#     start_date_datetime = start_date_datetime + time_delta
#
# beta_aeolus_all = np.asarray(beta_aeolus_all)
# beta_caliop_all = np.asarray(beta_caliop_all)
#
# with open('./%s.csv' % script_base, "w") as output:
#     writer = csv.writer(output, lineterminator='\n')
#     writer.writerow(('Colocation_Datetime', 'Aeolus_beta', 'Caliop_beta', 'alt_bottom', 'alt_top', 'Aeolus_QC', 'Aeolus_BER', 'Aeolus_LOD'))
#
#     for j in range(np.size(beta_aeolus_all)):
#         print(beta_aeolus_all[j], beta_caliop_all[j])
#         try:
#             if (float(beta_aeolus_all[j]) > 0) & (float(beta_caliop_all[j]) >0):
#                 writer.writerow((time_str_all[j], float(beta_aeolus_all[j]), float(beta_caliop_all[j]),
#                                  alt_bottom_all[j], alt_top_all[j], qc_aeolus_all[j],
#                                  ber_aeolus_all[j], lod_aeolus_all[j]))
#         except:
#             continue

beta_caliop_all = []
beta_aeolus_all = []

with open('./%s.csv' % script_base, newline='') as csvfile:
    reader = csv.reader(csvfile)
    index = 0
    for row in reader:
        if index > 0:
            beta_caliop_all.append(float(row[1]))
            beta_aeolus_all.append(float(row[2]))
        index = index + 1

beta_aeolus_all = np.asarray(beta_aeolus_all)
beta_caliop_all = np.asarray(beta_caliop_all)

x = beta_caliop_all[(beta_caliop_all > 0) & (beta_aeolus_all > 0) & (beta_caliop_all < 0.004) & (beta_aeolus_all < 0.004)]
y = beta_aeolus_all[(beta_caliop_all > 0) & (beta_aeolus_all > 0) & (beta_caliop_all < 0.004) & (beta_aeolus_all < 0.004)]
# xy = np.vstack([x,y])
# z = gaussian_kde(xy)(xy)
print(np.size(x))
fig, ax = plt.subplots(figsize=(10, 10))
plt.hist2d(x, y, bins=(70, 70), cmap = "RdYlGn_r",
           norm = colors.LogNorm())

# ax.scatter(x, y, c=z, s=50, cmap=plt.cm.jet)
ax.set_xlabel('beta_caliop_all', fontsize=18)
ax.set_ylabel('beta_aeolus_all', fontsize=18)
plt.xlim([0.,0.004])
plt.ylim([0.,0.004])

for tick in ax.xaxis.get_major_ticks():
    tick.label.set_fontsize(18)
for tick in ax.yaxis.get_major_ticks():
    tick.label.set_fontsize(18)

plt.savefig('./beta_all_from_20211101_hist.png')