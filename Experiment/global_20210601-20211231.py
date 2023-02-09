#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    global_20210601-20211231.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        06/02/2023 17:49

from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib import colors
from scipy.stats import kde
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
# beta_threshold = 0.004

plot_beta_max = 0.04
##############################################################
# set up the altitude range for different layers, this altitude range is Aeolus_top bin.
aeolus_layers_dic = {'layer-1': (0, 5),
                     'layer-2': (5, 10),
                    'layer-3': (10, 15),
                    'layer-4': (15, np.nan)}

aeolus_layers_keys = list(aeolus_layers_dic.keys())

##############################################################
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
##############################################################

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
    alt_top_all = []

    with open(output_dir + '/%s.csv' % script_base, newline='') as csvfile:

        reader = csv.reader(csvfile)
        index = 0
        for row in reader:
            if index > 0:
                beta_caliop_all.append(float(row[1]))
                beta_aeolus_all.append(float(row[2]))
                qc_aeolus_all.append(row[5])
                ber_aeolus_all.append(float(row[6]))
                alt_top_all.append(float(row[4]))
            index = index + 1

    beta_aeolus_all = np.asarray(beta_aeolus_all)
    beta_caliop_all = np.asarray(beta_caliop_all)
    qc_aeolus_all = np.asarray(qc_aeolus_all)
    ber_aeolus_all = np.asarray(ber_aeolus_all)
    alt_top_all = np.asarray(alt_top_all)

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

################################################################################
# remove aeolus with low SNR
qc_aeolus_all = [0 if element =='--' else element for element in qc_aeolus_all]
qc_aeolus_all = np.array(qc_aeolus_all, dtype=np.uint8)
qc_aeolus_flag = np.unpackbits(qc_aeolus_all).reshape([np.size(qc_aeolus_all), 8])

beta_aeolus_SNR_filtered = [np.nan if qc_aeolus_flag[q][1] == 0 else beta_aeolus_all[q] for q in range(np.size(qc_aeolus_all))]
beta_aeolus_SNR_cloud_filtered = np.copy(beta_aeolus_SNR_filtered)
beta_aeolus_SNR_cloud_filtered[ber_aeolus_all < BER_threshold] = np.nan
beta_aeolus_SNR_cloud_filtered = np.asarray(beta_aeolus_SNR_cloud_filtered)

#
#
# x = beta_caliop_all[(beta_caliop_all > 0) & (beta_aeolus_all > 0) & (beta_caliop_all < 0.02) & (beta_aeolus_all < 0.02)]
# y = beta_aeolus_all[(beta_caliop_all > 0) & (beta_aeolus_all > 0) & (beta_caliop_all < 0.02) & (beta_aeolus_all < 0.02)]

################################################################################
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
################################################################################

################################################################################
# AEOLUS Altitude top bin hist plot
fig, ax = plt.subplots(figsize=(10, 10))
plt.hist(alt_top_all, bins=100, color='red', edgecolor='black', alpha=0.7)

ax.set_xlabel('AEOLUS top bin altitude', fontsize=18)
ax.set_ylabel('Number of retrievals', fontsize=18)

for tick in ax.xaxis.get_major_ticks():
    tick.label.set_fontsize(18)
for tick in ax.yaxis.get_major_ticks():
    tick.label.set_fontsize(18)
# plt.xlim([0, .2])
plt.title('AEOLUS top bin altitude histogram', fontsize=18)
plt.savefig(output_dir + '/%s_top_alt_hist1d.png' %script_base)
################################################################################

x = beta_caliop_all[(beta_caliop_all > 0) & (beta_aeolus_SNR_cloud_filtered > 0)]
y = beta_aeolus_all[(beta_caliop_all > 0) & (beta_aeolus_SNR_cloud_filtered > 0)]

fig, ax = plt.subplots(4, 2, figsize=(10, 16))

# Loop through the axis array and plot random data
for i in range(4):
    for j in range(2):
        x = np.linspace(0, 10, 100)
        y = np.random.randn(100)
        ax[i, j].plot(x, y)

plt.savefig(output_dir + '/test.png' %script_base)
quit()
nbins=1000
k = kde.gaussian_kde([x,y])
xi, yi = np.mgrid[x.min():x.max():nbins*1j, y.min():y.max():nbins*1j]
zi = k(np.vstack([xi.flatten(), yi.flatten()]))

fig, ax = plt.subplots(figsize=(10, 10))
plt.pcolormesh(xi, yi, zi.reshape(xi.shape), shading='auto', cmap='RdYlGn_r')
ax.set_xlabel('beta_caliop_all', fontsize=18)
ax.set_ylabel('beta_aeolus_all', fontsize=18)
plt.xlim([0., np.nanmin([np.nanmax(x), np.nanmax(y)])])
plt.ylim([0., np.nanmin([np.nanmax(x), np.nanmax(y)])])

for tick in ax.xaxis.get_major_ticks():
    tick.label.set_fontsize(18)
for tick in ax.yaxis.get_major_ticks():
    tick.label.set_fontsize(18)

plt.savefig(output_dir + '/%s_cloudQC_SNRQC_hist2d.png' %script_base)

x2 = beta_caliop_all[(beta_caliop_all > 0) & (beta_aeolus_SNR_cloud_filtered > 0) & (alt_top_all < 5.)]
y2 = beta_aeolus_all[(beta_caliop_all > 0) & (beta_aeolus_SNR_cloud_filtered > 0) & (alt_top_all < 5.)]

k = kde.gaussian_kde([x2,y2])
xi, yi = np.mgrid[x2.min():x2.max():nbins*1j, y2.min():y2.max():nbins*1j]
zi = k(np.vstack([xi.flatten(), yi.flatten()]))

fig, ax = plt.subplots(figsize=(10, 10))
plt.pcolormesh(xi, yi, zi.reshape(xi.shape), shading='auto', cmap='RdYlGn_r')
ax.set_xlabel('beta_caliop_all', fontsize=18)
ax.set_ylabel('beta_aeolus_all', fontsize=18)
plt.xlim([0., np.nanmin([np.nanmax(x2), np.nanmax(y2)])])
plt.ylim([0., np.nanmin([np.nanmax(x2), np.nanmax(y2)])])

for tick in ax.xaxis.get_major_ticks():
    tick.label.set_fontsize(18)
for tick in ax.yaxis.get_major_ticks():
    tick.label.set_fontsize(18)

plt.savefig(output_dir + '/%s_cloudQC_SNRQC_0-5km_hist2d.png' %script_base)

x3 = beta_caliop_all[(beta_caliop_all > 0) & (beta_aeolus_SNR_cloud_filtered > 0) & (alt_top_all < 10.) & (alt_top_all > 8.5)]
y3 = beta_aeolus_all[(beta_caliop_all > 0) & (beta_aeolus_SNR_cloud_filtered > 0) & (alt_top_all < 10.) & (alt_top_all > 8.5)]

k = kde.gaussian_kde([x3,y3])
xi, yi = np.mgrid[x3.min():x3.max():nbins*1j, y3.min():y3.max():nbins*1j]
zi = k(np.vstack([xi.flatten(), yi.flatten()]))

fig, ax = plt.subplots(figsize=(10, 10))
plt.pcolormesh(xi, yi, zi.reshape(xi.shape), shading='auto', cmap='RdYlGn_r')
ax.set_xlabel('beta_caliop_all', fontsize=18)
ax.set_ylabel('beta_aeolus_all', fontsize=18)
plt.xlim([0., np.nanmin([np.nanmax(x3), np.nanmax(y3)])])
plt.ylim([0., np.nanmin([np.nanmax(x3), np.nanmax(y3)])])

for tick in ax.xaxis.get_major_ticks():
    tick.label.set_fontsize(18)
for tick in ax.yaxis.get_major_ticks():
    tick.label.set_fontsize(18)

plt.savefig(output_dir + '/%s_cloudQC_SNRQC_5-10km_hist2d.png' %script_base)

x4 = beta_caliop_all[(beta_caliop_all > 0) & (beta_aeolus_SNR_cloud_filtered > 0) & (alt_top_all < 15.) & (alt_top_all > 10.)]
y4 = beta_aeolus_all[(beta_caliop_all > 0) & (beta_aeolus_SNR_cloud_filtered > 0) & (alt_top_all < 15.) & (alt_top_all > 10.)]

k = kde.gaussian_kde([x4,y4])
xi, yi = np.mgrid[x4.min():x4.max():nbins*1j, y4.min():y4.max():nbins*1j]
zi = k(np.vstack([xi.flatten(), yi.flatten()]))

fig, ax = plt.subplots(figsize=(10, 10))
plt.pcolormesh(xi, yi, zi.reshape(xi.shape), shading='auto', cmap='RdYlGn_r')
ax.set_xlabel('beta_caliop_all', fontsize=18)
ax.set_ylabel('beta_aeolus_all', fontsize=18)
plt.xlim([0., np.nanmin([np.nanmax(x4), np.nanmax(y4)])])
plt.ylim([0., np.nanmin([np.nanmax(x4), np.nanmax(y4)])])

for tick in ax.xaxis.get_major_ticks():
    tick.label.set_fontsize(18)
for tick in ax.yaxis.get_major_ticks():
    tick.label.set_fontsize(18)

plt.savefig(output_dir + '/%s_cloudQC_SNRQC_10-15km_hist2d.png' %script_base)

x5 = beta_caliop_all[(beta_caliop_all > 0) & (beta_aeolus_SNR_cloud_filtered > 0) & (alt_top_all > 15.)]
y5 = beta_aeolus_all[(beta_caliop_all > 0) & (beta_aeolus_SNR_cloud_filtered > 0) & (alt_top_all > 15.)]

k = kde.gaussian_kde([x5,y5])
xi, yi = np.mgrid[x5.min():x5.max():nbins*1j, y5.min():y5.max():nbins*1j]
zi = k(np.vstack([xi.flatten(), yi.flatten()]))

fig, ax = plt.subplots(figsize=(10, 10))
plt.pcolormesh(xi, yi, zi.reshape(xi.shape), shading='auto', cmap='RdYlGn_r')
ax.set_xlabel('beta_caliop_all', fontsize=18)
ax.set_ylabel('beta_aeolus_all', fontsize=18)
plt.xlim([0., np.nanmin([np.nanmax(x5), np.nanmax(y5)])])
plt.ylim([0., np.nanmin([np.nanmax(x5), np.nanmax(y5)])])

for tick in ax.xaxis.get_major_ticks():
    tick.label.set_fontsize(18)
for tick in ax.yaxis.get_major_ticks():
    tick.label.set_fontsize(18)

plt.savefig(output_dir + '/%s_cloudQC_SNRQC_15km-above_hist2d.png' %script_base)