#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    global_20210601-20211231.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        06/02/2023 17:49

from datetime import datetime, timedelta
from scipy.stats import gaussian_kde
import matplotlib.pyplot as plt
from matplotlib import colors
import numpy as np
import pathlib
import csv
import sys
import os

sys.path.append('../')
from readColocationData.readColocationNetCDF import *

"""
This code uses all pre-calculated colocation files to do the retrieval analysis and comparison.
"""

##############################################################
# Define start and end dates
start_date = '2021-06-01'
end_date = '2021-12-31'

# Define the temporal window size
temporal_wd = 5. # hours

# Define the spatial bounds
lat_up = 60.
lat_down = -60.
lon_left = -180.
lon_right = 180.
##############################################################

BER_threshold = 0.05

def get_script_name():
    return sys.modules['__main__'].__file__

# Get the name of the script
script_name = get_script_name()

# Split the script name into a base name and an extension
script_base, script_ext = os.path.splitext(script_name)

# Add the .log extension to the base name
log_filename = script_base + '.log'

output_dir = './%s' %script_base
# Create output directories if they don't exist
try:
    os.stat(output_dir)
except:
    pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True)

colocationData_dir = '/gws/pw/j07/nceo_aerosolfire/rsong/project/global_aerosol/Database'

# Parse start and end dates
start_date_datetime = datetime.strptime(start_date, '%Y-%m-%d')
end_date_datetime = datetime.strptime(end_date, '%Y-%m-%d')

# Set up time delta
time_delta = timedelta(days = 1)

if os.path.exists(output_dir + '/%s.csv' % script_base):

    print("Colocated profiles are already extracted in %s.csv" %script_base)

    beta_caliop_all = []
    beta_aeolus_all = []
    ber_aeolus_all = []
    qc_aeolus_all = []

    with open(output_dir + '/%s.csv' % script_base, newline='') as csvfile:

        reader = csv.reader(csvfile)
        index = 0
        for row in reader:
            if index > 0:
                beta_caliop_all.append(float(row[1]))
                beta_aeolus_all.append(float(row[2]))
                qc_aeolus_all.append(row[5])
                ber_aeolus_all.append(float(row[6]))

            index = index + 1

    beta_aeolus_all = np.asarray(beta_aeolus_all)
    beta_caliop_all = np.asarray(beta_caliop_all)
    qc_aeolus_all = np.asarray(qc_aeolus_all)
    ber_aeolus_all = np.asarray(ber_aeolus_all)

else:

    beta_aeolus_all = []
    beta_caliop_all = []
    alt_bottom_all = []
    alt_top_all = []
    time_str_all = []
    qc_aeolus_all = []
    ber_aeolus_all = []
    lod_aeolus_all = []

    # Iterate through date range
    while start_date_datetime <= end_date_datetime:

        year_i = '{:04d}'.format(start_date_datetime.year)
        month_i = '{:02d}'.format(start_date_datetime.month)
        day_i = '{:02d}'.format(start_date_datetime.day)

        # locate the daily colocation observation parameter from satellite data
        colocationData_daily_dir = os.path.join(colocationData_dir, year_i, f"{year_i}-{month_i}-{day_i}")

        if os.path.isdir(colocationData_daily_dir):
            for file in os.listdir(colocationData_daily_dir):
                if file.endswith('.nc'):

                    try:
                        print('Processing file %s......'%file)
                        (beta_aeolus_i, beta_caliop_i, alt_bottom_i, alt_top_i, time_str_i, qc_i, ber_i,
                         lod_i) = extractColocationParameters(colocationData_daily_dir + '/' + file)

                        beta_aeolus_all.extend(beta_aeolus_i)
                        beta_caliop_all.extend(beta_caliop_i)
                        alt_bottom_all.extend(alt_bottom_i)
                        alt_top_all.extend(alt_top_i)
                        time_str_all.extend(time_str_i)
                        qc_aeolus_all.extend(qc_i)
                        ber_aeolus_all.extend(ber_i)
                        lod_aeolus_all.extend(lod_i)
                    except:
                        continue

        else:
            print('No colocation for %s-%s-%s'%(year_i, month_i, day_i))

        start_date_datetime = start_date_datetime + time_delta

    beta_aeolus_all = np.asarray(beta_aeolus_all)
    beta_caliop_all = np.asarray(beta_caliop_all)

    with open(output_dir + '/%s.csv' % script_base, "w") as output:
        writer = csv.writer(output, lineterminator='\n')
        writer.writerow(('Colocation_Datetime', 'Aeolus_beta', 'Caliop_beta', 'alt_bottom', 'alt_top', 'Aeolus_QC', 'Aeolus_BER', 'Aeolus_LOD'))

        for j in range(np.size(beta_aeolus_all)):

            try:
                if (float(beta_aeolus_all[j]) > 0) & (float(beta_caliop_all[j]) >0):
                    writer.writerow((time_str_all[j], float(beta_aeolus_all[j]), float(beta_caliop_all[j]),
                                     alt_bottom_all[j], alt_top_all[j], qc_aeolus_all[j],
                                     ber_aeolus_all[j], lod_aeolus_all[j]))
            except:
                continue

qc_aeolus_all = [0 if ele =='--' else ele for ele in qc_aeolus_all]
qc_aeolus_all = np.array(qc_aeolus_all, dtype=np.uint8)
qc_aeolus_flag = np.unpackbits(qc_aeolus_all).reshape([np.size(qc_aeolus_all), 8])

print(qc_aeolus_flag[0])
print(qc_aeolus_all[0])

quit()

x = beta_caliop_all[(beta_caliop_all > 0) & (beta_aeolus_all > 0) & (beta_caliop_all < 0.02) & (beta_aeolus_all < 0.02)]
y = beta_aeolus_all[(beta_caliop_all > 0) & (beta_aeolus_all > 0) & (beta_caliop_all < 0.02) & (beta_aeolus_all < 0.02)]

# AEOLUS BER hist plot
fig, ax = plt.subplots(figsize=(10, 10))

plt.hist(ber_aeolus_all, bins=1000, color='red', edgecolor='black', alpha=0.7)

ax.set_xlabel('AEOLUS BER', fontsize=18)
ax.set_ylabel('Number of retrievals', fontsize=18)

for tick in ax.xaxis.get_major_ticks():
    tick.label.set_fontsize(18)
for tick in ax.yaxis.get_major_ticks():
    tick.label.set_fontsize(18)
plt.xlim([0, .2])
plt.title('AEOLUS Backscatter-Extinction-Ratio histogram', fontsize=18)
plt.savefig(output_dir + '/%s_BER_hist1d.png' %script_base)

fig, ax = plt.subplots(figsize=(10, 10))
plt.hist2d(x, y, bins=(50, 50), cmap = "RdYlGn_r", norm = colors.LogNorm())

ax.set_xlabel('beta_caliop_all', fontsize=18)
ax.set_ylabel('beta_aeolus_all', fontsize=18)
plt.xlim([0.,0.02])
plt.ylim([0.,0.02])

for tick in ax.xaxis.get_major_ticks():
    tick.label.set_fontsize(18)
for tick in ax.yaxis.get_major_ticks():
    tick.label.set_fontsize(18)

plt.savefig(output_dir + '/%s_hist2d.png' %script_base)


x2 = beta_caliop_all[(beta_caliop_all > 0) & (beta_aeolus_all > 0) & (beta_caliop_all < 0.02) & (beta_aeolus_all < 0.02) & (ber_aeolus_all < BER_threshold)]
y2 = beta_aeolus_all[(beta_caliop_all > 0) & (beta_aeolus_all > 0) & (beta_caliop_all < 0.02) & (beta_aeolus_all < 0.02) & (ber_aeolus_all < BER_threshold)]

fig, ax = plt.subplots(figsize=(10, 10))
plt.hist2d(x2, y2, bins=(50, 50), cmap = "RdYlGn_r", norm = colors.LogNorm())

ax.set_xlabel('beta_caliop_all', fontsize=18)
ax.set_ylabel('beta_aeolus_all', fontsize=18)
plt.xlim([0.,0.02])
plt.ylim([0.,0.02])

for tick in ax.xaxis.get_major_ticks():
    tick.label.set_fontsize(18)
for tick in ax.yaxis.get_major_ticks():
    tick.label.set_fontsize(18)

plt.savefig(output_dir + '/%s_cloudQC_hist2d.png' %script_base)